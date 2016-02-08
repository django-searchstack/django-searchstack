# encoding: utf-8
from __future__ import unicode_literals

import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from . import signals
from .constants import DEFAULT_ALIAS
from .utils import loading

__author__ = 'Daniel Lindsley'
__version__ = (2, 5, 'dev0')


# Setup default logging.
log = logging.getLogger('searchstack')
stream = logging.StreamHandler()
stream.setLevel(logging.INFO)
log.addHandler(stream)


# Help people clean up from 1.X.
if hasattr(settings, 'SEARCHSTACK_SITECONF'):
    raise ImproperlyConfigured('The SEARCHSTACK_SITECONF setting is no longer used & can be removed.')
if hasattr(settings, 'SEARCHSTACK_SEARCH_ENGINE'):
    raise ImproperlyConfigured('The SEARCHSTACK_SEARCH_ENGINE setting has been replaced with SEARCHSTACK_CONNECTIONS.')
if hasattr(settings, 'SEARCHSTACK_ENABLE_REGISTRATIONS'):
    raise ImproperlyConfigured('The SEARCHSTACK_ENABLE_REGISTRATIONS setting is no longer used & can be removed.')
if hasattr(settings, 'SEARCHSTACK_INCLUDE_SPELLING'):
    raise ImproperlyConfigured('The SEARCHSTACK_INCLUDE_SPELLING setting is now a per-backend setting & belongs in SEARCHSTACK_CONNECTIONS.')


# Check the 2.X+ bits.
if not hasattr(settings, 'SEARCHSTACK_CONNECTIONS'):
    raise ImproperlyConfigured('The SEARCHSTACK_CONNECTIONS setting is required.')
if DEFAULT_ALIAS not in settings.SEARCHSTACK_CONNECTIONS:
    raise ImproperlyConfigured("The default alias '%s' must be included in the SEARCHSTACK_CONNECTIONS setting." % DEFAULT_ALIAS)

# Load the connections.
connections = loading.ConnectionHandler(settings.SEARCHSTACK_CONNECTIONS)

# Just check SEARCHSTACK_ROUTERS setting validity, routers will be loaded lazily
if hasattr(settings, 'SEARCHSTACK_ROUTERS'):
    if not isinstance(settings.SEARCHSTACK_ROUTERS, (list, tuple)):
        raise ImproperlyConfigured("The SEARCHSTACK_ROUTERS setting must be either a list or tuple.")

# Load the router(s).
connection_router = loading.ConnectionRouter()

# Setup the signal processor.
signal_processor_path = getattr(settings, 'SEARCHSTACK_SIGNAL_PROCESSOR', 'searchstack.signals.BaseSignalProcessor')
signal_processor_class = loading.import_class(signal_processor_path)
signal_processor = signal_processor_class(connections, connection_router)


# Per-request, reset the ghetto query log.
# Probably not extraordinarily thread-safe but should only matter when
# DEBUG = True.
def reset_search_queries(**kwargs):
    for conn in connections.all():
        conn.reset_queries()


if settings.DEBUG:
    from django.core import signals as django_signals
    django_signals.request_started.connect(reset_search_queries)
