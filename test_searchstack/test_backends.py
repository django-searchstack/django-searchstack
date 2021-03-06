# encoding: utf-8
from __future__ import unicode_literals

import warnings

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from searchstack.utils import loading


class LoadBackendTestCase(TestCase):
    def test_load_solr(self):
        try:
            import pysolr
        except ImportError:
            warnings.warn("Pysolr doesn't appear to be installed. Unable to test loading the Solr backend.")
            return

        backend = loading.load_backend('searchstack.backends.solr_backend.SolrEngine')
        self.assertEqual(backend.__name__, 'SolrEngine')

    def test_load_elasticsearch(self):
        try:
            import elasticsearch
        except ImportError:
            warnings.warn("elasticsearch-py doesn't appear to be installed. Unable to test loading the ElasticSearch backend.")
            return

        backend = loading.load_backend('searchstack.backends.elasticsearch_backend.ElasticsearchSearchEngine')
        self.assertEqual(backend.__name__, 'ElasticsearchSearchEngine')

    def test_load_nonexistent(self):
        try:
            backend = loading.load_backend('foobar')
            self.fail()
        except ImproperlyConfigured as e:
            self.assertEqual(str(e), "The provided backend 'foobar' is not a complete Python path to a BaseEngine subclass.")

        try:
            backend = loading.load_backend('foobar.FooEngine')
            self.fail()
        except ImportError as e:
            pass

        try:
            backend = loading.load_backend('searchstack.backends.solr_backend.FooEngine')
            self.fail()
        except ImportError as e:
            self.assertEqual(str(e), "The Python module 'searchstack.backends.solr_backend' has no 'FooEngine' class.")
