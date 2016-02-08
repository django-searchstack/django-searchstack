# encoding: utf-8
from __future__ import unicode_literals

from django.conf import settings

import unittest


def check_solr(using='solr'):
    try:
        from pysolr import Solr, SolrError
    except ImportError:
        raise unittest.SkipTest("pysolr not installed.")

    solr = Solr(settings.SEARCHSTACK_CONNECTIONS[using]['URL'])
    try:
        solr.search('*:*')
    except SolrError as e:
        raise unittest.SkipTest("solr not running on %r" % settings.SEARCHSTACK_CONNECTIONS[using]['URL'], e)
