# encoding: utf-8
from __future__ import unicode_literals

from searchstack.routers import BaseRouter


class MultipleIndexRouter(BaseRouter):
    def for_write(self, instance=None, **hints):
        if instance and instance._meta.app_label == 'multipleindex':
            return 'solr'
