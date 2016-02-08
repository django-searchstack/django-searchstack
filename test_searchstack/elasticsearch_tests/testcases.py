# encoding: utf-8
from __future__ import unicode_literals

import elasticsearch
from django.conf import settings
from django.test import TestCase

from searchstack import connections


def clear_elasticsearch_index(alias):
    # Wipe it clean.
    raw_es = elasticsearch.Elasticsearch(settings.SEARCHSTACK_CONNECTIONS[alias]['URL'])
    try:
        raw_es.indices.delete(index=settings.SEARCHSTACK_CONNECTIONS[alias]['INDEX_NAME'])
        raw_es.indices.refresh()
    except elasticsearch.TransportError:
        pass

    # Since we've just completely deleted the index, we'll reset setup_complete so the next access will
    # correctly define the mappings:
    connections[alias].get_backend().setup_complete = False


class ElasticSearchTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        for name, conn_settings in settings.SEARCHSTACK_CONNECTIONS.items():
            if conn_settings['ENGINE'] != 'searchstack.backends.elasticsearch_backend.ElasticsearchSearchEngine':
                continue
            clear_elasticsearch_index(name)

        super(ElasticSearchTestCase, cls).setUpClass()
