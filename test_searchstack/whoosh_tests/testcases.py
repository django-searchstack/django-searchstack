# encoding: utf-8
import os
import shutil

from django.conf import settings
from django.test import TestCase


class WhooshTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        for name, conn_settings in settings.SEARCHSTACK_CONNECTIONS.items():
            if conn_settings['ENGINE'] != 'searchstack.backends.whoosh_backend.WhooshEngine':
                continue

            if 'STORAGE' in conn_settings and conn_settings['STORAGE'] != 'file':
                continue

            # Start clean
            if os.path.exists(conn_settings['PATH']):
                shutil.rmtree(conn_settings['PATH'])

            from searchstack import connections
            connections[name].get_backend().setup()

        super(WhooshTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        for conn in settings.SEARCHSTACK_CONNECTIONS.values():
            if conn['ENGINE'] != 'searchstack.backends.whoosh_backend.WhooshEngine':
                continue

            if 'STORAGE' in conn and conn['STORAGE'] != 'file':
                continue

            # Start clean
            if os.path.exists(conn['PATH']):
                shutil.rmtree(conn['PATH'])

        super(WhooshTestCase, cls).tearDownClass()
