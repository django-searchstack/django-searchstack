# encoding: utf-8
from __future__ import unicode_literals

from django.contrib import admin

from searchstack.admin import SearchModelAdmin

from .models import MockModel


class MockModelAdmin(SearchModelAdmin):
    searchstack_connection = 'solr'
    date_hierarchy = 'pub_date'
    list_display = ('author', 'pub_date')


admin.site.register(MockModel, MockModelAdmin)
