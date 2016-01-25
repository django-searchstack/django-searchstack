#!/usr/bin/env python
# encoding: utf-8
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

install_requires = [
    'python-dateutil',
    'Django',
]

tests_require = [
    'elasticsearch>=1.0.0,<2.0.0',
    'pysolr>=3.3.2',
    'whoosh==2.5.4',
    'python-dateutil',
    'geopy==0.95.1',

    'nose',
    'mock',
    'coverage',
]

setup(
    name='django-searchstack',
    version='1.0dev0',
    description='Pluggable search for Django.',
    author='Daniel Lindsley',
    author_email='daniel@toastdriven.com',
    long_description=open('README.rst', 'r').read(),
    url='https://github.com/django-searchstack/django-searchstack',
    packages=[
        'searchstack',
        'searchstack.backends',
        'searchstack.management',
        'searchstack.management.commands',
        'searchstack.templatetags',
        'searchstack.utils',
    ],
    package_data={
        'searchstack': [
            'templates/panels/*',
            'templates/search_configuration/*',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite="test_searchstack.run_tests.run_all",
)
