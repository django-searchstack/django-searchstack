# encoding: utf-8
from django.db.models import Model, BooleanField, CharField


class HierarchalAppModel(Model):
    enabled = BooleanField(default=True)


class HierarchalAppSecondModel(Model):
    title = CharField(max_length=16)
