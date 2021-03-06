# encoding: utf-8
from __future__ import unicode_literals

from .models import Bar, Foo

from searchstack import indexes


class FooIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.TextField(document=True, model_attr='body')

    def get_model(self):
        return Foo


class BarIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.TextField(document=True)

    def get_model(self):
        return Bar
