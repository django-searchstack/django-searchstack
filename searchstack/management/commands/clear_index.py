# encoding: utf-8
from __future__ import unicode_literals

import sys

from django.core.management.base import BaseCommand
from django.utils import six

from ... import connections

# defined statically to be useable in rebuild_index
options = {
    ('--noinput',): {
        'action': 'store_false',
        'dest': 'interactive',
        'default': True,
        'help': 'If provided, no prompts will be issued to the user and the data will be wiped out.',
    },
    ('-u', '--using'): {
        'action': 'append',
        'dest': 'using',
        'default': list(connections.connections_info.keys()),
        'help': 'Update only the named backend (can be used multiple times). '
                'By default all backends will be updated.',
    },
    ('--nocommit',): {
        'action': 'store_false',
        'dest': 'commit',
        'default': True,
        'help': 'Will pass commit=False to the backend.',
    },
}


class Command(BaseCommand):
    help = "Clears out the search index completely."

    def add_arguments(self, parser):
        for args, kwargs in options.items():
            parser.add_argument(*args, **kwargs)

    def handle(self, **kwargs):
        """Clears out the search index completely."""
        commit = kwargs['commit']
        interactive = kwargs['interactive']
        using = kwargs['using']
        verbosity = kwargs['verbosity']

        if interactive:
            self.stdout.write('')
            self.stdout.write(
                "WARNING: This will irreparably remove EVERYTHING from your "
                "search index in connection '%s'." % "', '".join(using))
            self.stdout.write(
                "Your choices after this are to restore from backups or "
                "rebuild via the `rebuild_index` command.")

            yes_or_no = six.moves.input("Are you sure you wish to continue? [y/N] ")
            self.stdout.write('')

            if not yes_or_no.lower().startswith('y'):
                self.stdout.write("No action taken.")
                sys.exit()

        if verbosity >= 1:
            self.stdout.write("Removing all documents from your index because you said so.")

        for backend_name in using:
            backend = connections[backend_name].get_backend()
            backend.clear(commit=commit)

        if verbosity >= 1:
            self.stdout.write("All documents removed.")

