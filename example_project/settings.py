# encoding: utf-8
from __future__ import unicode_literals

from django.conf import settings

SECRET_KEY = 'CHANGE ME'

# All the normal settings apply. What's included here are the bits you'll have
# to customize.

# Add Haystack to INSTALLED_APPS. You can do this by simply placing in your list.
INSTALLED_APPS = settings.INSTALLED_APPS + (
    'searchstack',
)


SEARCHSTACK_CONNECTIONS = {
    'default': {
        # For Solr:
        'ENGINE': 'searchstack.backends.solr_backend.SolrEngine',
        'URL': 'http://localhost:9001/solr/example',
        'TIMEOUT': 60 * 5,
        'INCLUDE_SPELLING': True,
    },
    'elasticsearch': {
        'ENGINE': 'searchstack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://localhost:9200',
        'INDEX_NAME': 'example_project'
    },
}
