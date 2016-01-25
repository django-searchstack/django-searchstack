========
Django-Searchstack
========

.. image:: https://img.shields.io/travis/rust-lang/rust.svg?style=flat-square  
   :target: https://travis-ci.org/django-searchstack/django-searchstack
.. image:: https://img.shields.io/coveralls/jekyll/jekyll.svg?style=flat-square
   :target: https://coveralls.io/github/django-searchstack/django-searchstack

Django-Searchstack is a fork of Django-Haystack the aim of which is to
deprecate a lot of unused/barely-used features, fix long standing bugs
and add new substantial features. Currently it is under heavy development
but whenever version 1.0 comes out, it will be mostly backwards-compatible
with Haystack with clear migration instructions.

Django-Searchstack provides modular search for Django. It features a unified, familiar
API that allows you to plug in different search backends (such as Solr_ and
Elasticsearch_). The current plan is to only have two full-featured backends
whereas Whoosh backend (which exists in Haystack) is removed.

.. _Solr: http://lucene.apache.org/solr/
.. _Elasticsearch: http://elasticsearch.org/

Django-Searchstack is BSD licensed, plays nicely with third-party apps without needing to
modify the source and supports advanced features like faceting, More Like This,
highlighting, spatial search and spelling suggestions.


Getting Help
============

Please file issues on GitHub.

Documentation
=============

Currently in development.

Requirements
============

Haystack has a relatively easily-met set of requirements.

* Python 2.7+ or Python 3.3+
* A supported version of Django: https://www.djangoproject.com/download/#supported-versions

Additionally, each backend has its own requirements.
