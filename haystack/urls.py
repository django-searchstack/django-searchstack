# encoding: utf-8
from django.conf.urls import patterns, url

from .views import SearchView

urlpatterns = patterns('haystack.views',
    url(r'^$', SearchView(), name='haystack_search'),
)

