# encoding: utf-8
from django.core.management import call_command
from django.core.management.base import BaseCommand

from .clear_index import options as clear_opts
from .update_index import options as update_opts


class Command(BaseCommand):
    help = "Completely rebuilds the search index by removing the old data and then updating."

    def add_arguments(self, parser):
        # only a subset of clear_index/update_index options make sense when
        # called from rebuild_index:
        use_opts = [('--noinput',), ('-u', '--using'), ('--nocommit',), ('-b', '--batch-size'),
                    ('-k', '--workers')]
        for opt_args in use_opts:
            # try to get from clear_opts, otherwise must exist in update_opts
            opt_kwargs = clear_opts.get(opt_args, update_opts.get(opt_args))
            parser.add_argument(*opt_args, **opt_kwargs)

    def handle(self, **options):
        call_command('clear_index', **options)
        call_command('update_index', **options)
