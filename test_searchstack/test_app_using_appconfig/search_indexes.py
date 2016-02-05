# encoding: utf-8
from searchstack import indexes

from .models import MicroBlogPost


class MicroBlogSearchIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.TextField(document=True, use_template=False, model_attr='text')

    def get_model(self):
        return MicroBlogPost
