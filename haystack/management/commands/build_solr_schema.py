# encoding: utf-8
import argparse

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from django.template import loader

from ... import connections, constants
from ...backends.solr_backend import SolrSearchBackend


class Command(BaseCommand):
    help = "Generates a Solr schema that reflects the indexes."

    def add_arguments(self, parser):
        parser.add_argument(
            "-f", "--filename", action="store", type=argparse.FileType('w'), dest="schema_file",
            help='If provided, directs output to a file instead of stdout.')
        parser.add_argument(
            "-u", "--using", action="store", dest="using", default=constants.DEFAULT_ALIAS,
            help='If provided, chooses a connection to work with.')

    def handle(self, **kwargs):
        """Generates a Solr schema that reflects the indexes."""
        schema_xml = self.build_template(kwargs['using'])

        if kwargs['schema_file']:
            self.write_file(kwargs['schema_file'], schema_xml)
        else:
            self.print_stdout(schema_xml)

    def build_template(self, using):
        t = loader.get_template('search_configuration/solr.xml')

        backend = connections[using].get_backend()

        if not isinstance(backend, SolrSearchBackend):
            raise ImproperlyConfigured("'%s' isn't configured as a SolrEngine)." % backend.connection_alias)

        content_field_name, fields = backend.build_schema(
            connections[using].get_unified_index().all_searchfields())
        context = {
            'content_field_name': content_field_name,
            'fields': fields,
            'default_operator': constants.DEFAULT_OPERATOR,
            'ID': constants.ID,
            'DJANGO_CT': constants.DJANGO_CT,
            'DJANGO_ID': constants.DJANGO_ID,
        }
        return t.render(context)

    def print_stdout(self, schema_xml):
        self.stderr.write('')
        self.stderr.write('')
        self.stderr.write('')
        self.stderr.write(
            "Save the following output to 'schema.xml' and place it in your Solr configuration directory.")
        self.stderr.write(
            "--------------------------------------------------------------------------------------------")
        self.stderr.write('')
        self.stdout.write(schema_xml)

    def write_file(self, schema_file, schema_xml):
        schema_file.write(schema_xml)
        schema_file.close()
