# encoding: utf-8
from tempfile import mkdtemp

SECRET_KEY = "Please do not spew DeprecationWarnings"

# Haystack settings for running tests.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'searchstack_tests.db',
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',

    'searchstack',

    'test_searchstack.discovery',
    'test_searchstack.core',
    'test_searchstack.spatial',
    'test_searchstack.multipleindex',

    # This app exists to confirm that nothing breaks when INSTALLED_APPS has an app without models.py
    # which is common in some cases for things like admin extensions, reporting, etc.
    'test_searchstack.test_app_without_models',

    # Confirm that everything works with app labels which have more than one level of hierarchy
    # as reported in https://github.com/django-searchstack/django-searchstack/issues/1152
    'test_searchstack.test_app_with_hierarchy.contrib.django.hierarchal_app_django',

    'test_searchstack.test_app_using_appconfig.apps.SimpleTestAppConfig'
]

SITE_ID = 1
ROOT_URLCONF = 'test_searchstack.core.urls'

SEARCHSTACK_ROUTERS = ['searchstack.routers.DefaultRouter', 'test_searchstack.multipleindex.routers.MultipleIndexRouter']

SEARCHSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'test_searchstack.mocks.MockEngine',
    },
    'whoosh': {
        'ENGINE': 'searchstack.backends.whoosh_backend.WhooshEngine',
        'PATH': mkdtemp(prefix='test_whoosh_query'),
        'INCLUDE_SPELLING': True,
    },
    'filtered_whoosh': {
        'ENGINE': 'searchstack.backends.whoosh_backend.WhooshEngine',
        'PATH': mkdtemp(prefix='searchstack-multipleindex-filtered-whoosh-tests-'),
        'EXCLUDED_INDEXES': ['test_searchstack.multipleindex.search_indexes.BarIndex'],
    },
    'elasticsearch': {
        'ENGINE': 'searchstack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': '127.0.0.1:9200/',
        'INDEX_NAME': 'test_default',
        'INCLUDE_SPELLING': True,
    },
    'simple': {
        'ENGINE': 'searchstack.backends.simple_backend.SimpleEngine',
    },
    'solr': {
        'ENGINE': 'searchstack.backends.solr_backend.SolrEngine',
        'URL': 'http://localhost:9001/solr/',
        'INCLUDE_SPELLING': True,
    },
}

MIDDLEWARE_CLASSES = ('django.middleware.common.CommonMiddleware',
                      'django.contrib.sessions.middleware.SessionMiddleware',
                      'django.middleware.csrf.CsrfViewMiddleware',
                      'django.contrib.auth.middleware.AuthenticationMiddleware',
                      'django.contrib.messages.middleware.MessageMiddleware')
