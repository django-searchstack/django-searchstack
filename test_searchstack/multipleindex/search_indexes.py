# encoding: utf-8
from __future__ import unicode_literals

from searchstack import indexes
from searchstack.indexes import Indexable, SearchIndex

from .models import Bar, Foo


# To test additional ignores...
class BaseIndex(indexes.SearchIndex):
    text = indexes.TextField(document=True, model_attr='body')

    def get_model(self):
        return Foo


class FooIndex(BaseIndex, indexes.Indexable):
    def index_queryset(self, using=None):
        qs = super(FooIndex, self).index_queryset(using=using)
        if using == "filtered_elasticsearch":
            qs = qs.filter(body__contains="1")
        return qs


# Import the old way & make sure things don't explode.


class BarIndex(SearchIndex, Indexable):
    text = indexes.TextField(document=True)

    def get_model(self):
        return Bar

    def prepare_text(self, obj):
        return "%s\n%s" % (obj.author, obj.content)
