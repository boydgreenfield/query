"""
Module for conveniently exploring and fetching data from a variety of SQL databases.
Is *not* primarily designed for writing to SQL databases, and should be used
principally for read-only data exploration. Use with IPython Notebook is heartily
recommended.
"""
from query.core import QueryDb  # noqa

# Aliases
from query.core import QueryDb as QueryDB  # noqa
