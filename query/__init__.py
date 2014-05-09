"""
Module for conveniently exploring and fetching data from a variety of SQL databases.
Is *not* primarily designed for writing to SQL databases, and should be used
principally for read-only data exploration. Use with IPython Notebook is heartily
recommended.

Dependency version note: Because this module relies heavily on both SQLAlchemy
and Pandas, and because Pandas will begin to use SQLAlchemy for its native
.read_sql() methods in v0.14, this module uses the development release of
Pandas v0.14 which is currently scheduled for release in May 2014.
"""
from query.core import QueryDb

# Aliases
from query.core import QueryDb as QueryDB
