"""
``query``
---------

``query`` is a simple module for quickly, interactively exploring a SQL
database. Together with IPython, it supports quick tab-completion of table
and column names, convenience methods for quickly looking at data (e.g.,
``.head()``, ``.tail()``), and the ability to get a rich interactive database
connection up in only 2 lines by setting a few required environmental
variables.

.. image:: https://travis-ci.org/boydgreenfield/query.svg?branch=v0.1.4


Demo in 2 lines
```````````````

Explore the included demo database:

.. code:: python

    from query import QueryDb
    db = QueryDb(demo=True)


Real-world use case in 2 lines
``````````````````````````````

Or set a few environmental variables (``QUERY_DB_DRIVER``,
``QUERY_DB_HOST``, ``QUERY_DB_PORT``, ``QUERY_DB_NAME``, and
``QUERY_DB_PASS``) and get started just as quickly:

.. code:: python

    from query import QueryDB  # capital 'B' is OK too :)
    db = QueryDB()


Interactive example
```````````````````
.. image:: https://github.com/boydgreenfield/query/raw/v0.1.2/docs/images/interactive_demo.gif?raw=True



Links
`````
* `Code and additional details on Github: <http://github.com/boydgreenfield/query/>`_

"""
from setuptools import setup


setup(
    name='query',
    version='0.1.4',  # When incrementing,
                      # make sure to update Travis link above as well
    url='http://github.com/boydgreenfield/query/',
    license='MIT',
    author='Nick Boyd Greenfield',
    author_email='boyd.greenfield@gmail.com',
    description='Quick interactive exploration of SQL databases.',
    long_description=__doc__,
    packages=['query'],
    package_data={'query': ['sample_data/*.sqlite', 'sample_data/*.md']},
    zip_safe=True,
    platforms='any',
    install_requires=[
        'pandas>=0.16',
        'sqlalchemy>=1.3.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: IPython',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Database :: Front-Ends'
    ],
    test_suite='nose.collector'
)
