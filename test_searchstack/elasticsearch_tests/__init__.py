# encoding: utf-8
from __future__ import unicode_literals

import warnings

from django.conf import settings

from ..utils import unittest

warnings.simplefilter('ignore', Warning)


def setup():
    try:
        from elasticsearch import Elasticsearch, ElasticsearchException
    except ImportError:
        raise unittest.SkipTest("elasticsearch-py not installed.")

    es = Elasticsearch(settings.SEARCHSTACK_CONNECTIONS['elasticsearch']['URL'])
    try:
        es.info()
    except ElasticsearchException as e:
        raise unittest.SkipTest("elasticsearch not running on %r" % settings.SEARCHSTACK_CONNECTIONS['elasticsearch']['URL'], e)
