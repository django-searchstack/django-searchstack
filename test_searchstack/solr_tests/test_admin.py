# encoding: utf-8
from __future__ import unicode_literals

from django import VERSION as DJANGO_VERSION
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import override_settings

from searchstack import connections, reset_search_queries
from searchstack.utils.loading import UnifiedIndex

from ..core.models import MockModel
from .test_solr_backend import SolrMockModelSearchIndex, clear_solr_index


@override_settings(DEBUG=True)
class SearchModelAdminTestCase(TestCase):
    fixtures = ['bulk_data.json']

    def setUp(self):
        super(SearchModelAdminTestCase, self).setUp()

        # With the models setup, you get the proper bits.
        # Stow.
        self.old_ui = connections['solr'].get_unified_index()
        self.ui = UnifiedIndex()
        smmsi = SolrMockModelSearchIndex()
        self.ui.build(indexes=[smmsi])
        connections['solr']._index = self.ui

        # Wipe it clean.
        clear_solr_index()

        # Force indexing of the content.
        smmsi.update(using='solr')

        User.objects.create_superuser(
            username='superuser',
            password='password',
            email='super@user.com',
        )

    def tearDown(self):
        # Restore.
        connections['solr']._index = self.old_ui
        super(SearchModelAdminTestCase, self).tearDown()

    def test_usage(self):
        reset_search_queries()
        self.assertEqual(len(connections['solr'].queries), 0)

        self.assertEqual(self.client.login(username='superuser', password='password'), True)

        # First, non-search behavior.
        resp = self.client.get('/admin/core/mockmodel/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(connections['solr'].queries), 0)
        self.assertEqual(resp.context['cl'].full_result_count, 23)

        # Then search behavior.
        resp = self.client.get('/admin/core/mockmodel/', data={'q': 'Haystack'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(connections['solr'].queries), 3)
        self.assertEqual(resp.context['cl'].full_result_count, 23)
        # Ensure they aren't search results.
        self.assertEqual(isinstance(resp.context['cl'].result_list[0], MockModel), True)

        result_pks = [i.pk for i in resp.context['cl'].result_list]
        self.assertIn(5, result_pks)

        # Make sure only changelist is affected.
        change_url = '/admin/core/mockmodel/1/'
        if DJANGO_VERSION >= (1, 9, 0):
            # in Django 1.9 change view urls changed
            change_url += 'change/'
        resp = self.client.get(change_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(connections['solr'].queries), 3)
        self.assertEqual(resp.context['original'].id, 1)
