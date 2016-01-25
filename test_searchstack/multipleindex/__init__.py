# encoding: utf-8
from django.db.models import signals

import searchstack
from searchstack.signals import RealtimeSignalProcessor

from ..utils import check_solr


_old_sp = None
def setup():
    check_solr()
    global _old_sp
    _old_sp = searchstack.signal_processor
    searchstack.signal_processor = RealtimeSignalProcessor(searchstack.connections, searchstack.connection_router)


def teardown():
    searchstack.signal_processor = _old_sp
    signals.post_save.receivers = []
    signals.post_delete.receivers = []
