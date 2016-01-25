# encoding: utf-8
import logging
import os
from datetime import timedelta

from dateutil.parser import parse as dateutil_parse
from django.core.management.base import BaseCommand
from django.db import connections, reset_queries
from django.utils.encoding import force_text, smart_bytes
from django.utils.timezone import now

from ... import connections as haystack_connections
from ...query import SearchQuerySet
from ...utils.app_loading import haystack_get_models, haystack_load_apps


def worker(queue):
    while True:
        # wait for a job
        bits = queue.get()

        # Check job type and do it. There are two types of jobs: do_update (which is called multiple times
        # during worker lifetime) and close (which is called before killing the process)
        if bits[0] == 'close':
            # Django makes sure that when new process/thread hits DB it gets a new connection
            # (or connections). Such connections won't be usable for other threads so let's close them.
            connections.close_all()
            queue.task_done()  # mark job as done and exit the loop
            break
        elif bits[0] == 'do_update':
            func, model, start, end, total, using, start_date, end_date, verbosity, commit = bits

            unified_index = haystack_connections[using].get_unified_index()
            index = unified_index.get_index(model)
            backend = haystack_connections[using].get_backend()

            qs = index.build_queryset(start_date=start_date, end_date=end_date)
            do_update(backend, index, qs, start, end, total, verbosity=verbosity, commit=commit)

        queue.task_done()  # mark job as done


def do_update(backend, index, qs, start, end, total, verbosity=1, commit=True):
    # Get a clone of the QuerySet so that the cache doesn't bloat up
    # in memory. Useful when reindexing large amounts of data.
    small_cache_qs = qs.all()
    current_qs = small_cache_qs[start:end]

    if verbosity >= 2:
        if hasattr(os, 'getppid') and os.getpid() == os.getppid():
            print("  indexed %s - %d of %d." % (start + 1, end, total))
        else:
            print("  indexed %s - %d of %d (by %s)." % (start + 1, end, total, os.getpid()))

    backend.update(index, current_qs, commit=commit)

    # cleanup connection query log when in DEBUG mode
    reset_queries()


# defined statically to be useable in rebuild_index
options = {
    ('-a', '--age'): {
        'action': 'store',
        'dest': 'age',
        'default': None,
        'type': int,
        'help': 'Number of hours back to consider objects new.',
    },
    ('-s', '--start'): {
        'action': 'store',
        'dest': 'start_date',
        'default': None,
        'type': dateutil_parse,
        'help': 'The start date for indexing within. Can be any dateutil-parsable string'
                ', recommended to be YYYY-MM-DDTHH:MM:SS.',
    },
    ('-e', '--end'): {
        'action': 'store',
        'dest': 'end_date',
        'default': None,
        'type': dateutil_parse,
        'help': 'The end date for indexing within. Can be any dateutil-parsable string'
                ', recommended to be YYYY-MM-DDTHH:MM:SS.',
    },
    ('-b', '--batch-size'): {
        'action': 'store',
        'dest': 'batchsize',
        'default': None,
        'type': int,
        'help': 'Number of items to index at once.',
    },
    ('-r', '--remove'): {
        'action': 'store_true',
        'dest': 'remove',
        'default': False,
        'help': 'Remove objects from the index that are no longer present in the database.',
    },
    ("-u", "--using"): {
        'action': "append",
        'dest': "using",
        'default': haystack_connections.connections_info.keys(),
        'help': 'Update only the named backend (can be used multiple times). '
                'By default all backends will be updated.',
    },
    ('-k', '--workers'): {
        'action': 'store',
        'dest': 'workers',
        'default': 0,
        'type': int,
        'help': 'Allows for the use of multiple workers to parallelize indexing. Requires multiprocessing.',
    },
    ('--nocommit',): {
        'action': 'store_false',
        'dest': 'commit',
        'default': True,
        'help': 'Will pass commit=False to the backend.',
    },
    ('app_or_model',): {
        'nargs': '*',
        'help': 'App label or Django content type (model name) to update the search index for.',
    },
}


class Command(BaseCommand):
    help = "Freshens the index for the given app(s) or model(s)."

    def add_arguments(self, parser):
        for args, kwargs in options.items():
            parser.add_argument(*args, **kwargs)

    def handle(self, **options):
        # put all options to self
        for opt, val in options.items():
            setattr(self, opt, val)

        if self.start_date is None and self.age is not None:
            self.start_date = now() - timedelta(hours=self.age)

        if not self.app_or_model:
            self.app_or_model = haystack_load_apps()

        # setup workers if needed
        if self.workers > 0:
            from multiprocessing import JoinableQueue, Process

            # queue to communicate with workers with max size of double the workers so that workers always
            # have waiting tasks before they finish previous ones
            self.queue = JoinableQueue(self.workers * 2)
            # create workers and start them
            self.processes = [Process(target=worker, args=(self.queue,)) for i in range(self.workers)]
            for process in self.processes:
                process.start()

        for app_or_model in self.app_or_model:
            for using in self.using:
                try:
                    self.update_backend(app_or_model, using)
                except:
                    logging.exception("Error updating %s using %s ", app_or_model, using)
                    raise

        # send 'close' instruction to workers and wait for them to terminate
        if self.workers > 0:
            self.queue.join()  # wait for outstanding tasks to be finished
            for i in range(self.workers):
                self.queue.put(('close',))
            self.queue.join()
            for process in self.processes:
                process.join()

    def update_backend(self, label, using):
        from ...exceptions import NotHandled

        backend = haystack_connections[using].get_backend()
        unified_index = haystack_connections[using].get_unified_index()

        for model in haystack_get_models(label):
            try:
                index = unified_index.get_index(model)
            except NotHandled:
                if self.verbosity >= 2:
                    self.stdout.write("Skipping '%s' - no index." % model)
                continue

            qs = index.build_queryset(using=using, start_date=self.start_date,
                                      end_date=self.end_date)
            total = qs.count()

            if self.verbosity >= 1:
                self.stdout.write(u"Indexing %d %s" % (total, force_text(model._meta.verbose_name_plural)))

            batch_size = self.batchsize or backend.batch_size

            for start in range(0, total, batch_size):
                end = min(start + batch_size, total)

                if self.workers == 0:
                    do_update(backend, index, qs, start, end, total,
                              verbosity=self.verbosity, commit=self.commit)
                else:
                    self.queue.put(('do_update', model, start, end, total, using,
                                    self.start_date, self.end_date, self.verbosity, self.commit))

            if self.remove:
                if self.start_date or self.end_date:
                    # They're using a reduced set, which may not incorporate
                    # all pks. Rebuild the list with everything.
                    qs = index.index_queryset()

                if not qs:
                    # nothing to remove, go to next model
                    continue

                database_pks = set(smart_bytes(pk) for pk in qs.values_list('pk', flat=True))
                total = len(database_pks)

                # Since records may still be in the search index but not the local database
                # we'll use that to create batches for processing.
                # See https://github.com/django-haystack/django-haystack/issues/1186
                index_total = SearchQuerySet(using=backend.connection_alias).models(model).count()

                # Retrieve PKs from the index. Note that this cannot be a numeric range query because although
                # pks are normally numeric they can be non-numeric UUIDs or other custom values. To reduce
                # load on the search engine, we only retrieve the pk field, which will be checked against the
                # full list obtained from the database, and the id field, which will be used to delete the
                # record should it be found to be stale.
                index_pks = SearchQuerySet(using=backend.connection_alias).models(model)
                index_pks = index_pks.values_list('pk', 'id')

                # We'll collect all of the record IDs which are no longer present in the database and delete
                # them after walking the entire index. This uses more memory than the incremental approach but
                # avoids needing the pagination logic below to account for both commit modes:
                stale_records = set()

                for start in range(0, index_total, batch_size):
                    upper_bound = start + batch_size

                    # If the database pk is no longer present, queue the index key for removal:
                    for pk, rec_id in index_pks[start:upper_bound]:
                        if smart_bytes(pk) not in database_pks:
                            stale_records.add(rec_id)

                if stale_records:
                    if self.verbosity >= 1:
                        self.stdout.write("  removing %d stale records." % len(stale_records))

                    for rec_id in stale_records:
                        # Since the PK was not in the database list,
                        # we'll delete the record from the search index:
                        if self.verbosity >= 2:
                            self.stdout.write("  removing %s." % rec_id)

                        backend.remove(rec_id, commit=self.commit)
