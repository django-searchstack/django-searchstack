# encoding: utf-8
from django.conf.urls import include, url
from django.contrib import admin

from searchstack.forms import FacetedSearchForm
from searchstack.query import SearchQuerySet
from searchstack.views import FacetedSearchView, SearchView, basic_search

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
]

urlpatterns += [
    url(r'^$', SearchView(load_all=False), name='searchstack_search'),
    url(r'^faceted/$', FacetedSearchView(searchqueryset=SearchQuerySet().facet('author'),
                                         form_class=FacetedSearchForm), name='searchstack_faceted_search'),
    url(r'^basic/$', basic_search, {'load_all': False}, name='searchstack_basic_search'),
]

urlpatterns += [
    url(r'', include('test_searchstack.test_app_without_models.urls', namespace='app-without-models')),
]
