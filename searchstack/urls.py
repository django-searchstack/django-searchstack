# encoding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url

from .views import SearchView

urlpatterns = [
    url(r'^$', SearchView(), name='haystack_search'),
]
