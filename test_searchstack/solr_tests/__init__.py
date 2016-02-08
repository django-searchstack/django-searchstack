# encoding: utf-8
from __future__ import unicode_literals

import warnings
warnings.simplefilter('ignore', Warning)

from ..utils import check_solr


def setup():
    check_solr()
