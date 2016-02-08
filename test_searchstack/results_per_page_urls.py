# encoding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url

from searchstack.views import SearchView


class CustomPerPage(SearchView):
    results_per_page = 1


urlpatterns = [
    url(r'^search/$', CustomPerPage(load_all=False), name='searchstack_search'),
    url(r'^search2/$', CustomPerPage(load_all=False, results_per_page=2), name='searchstack_search'),
]
