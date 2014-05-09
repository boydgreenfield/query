from nose.tools import *
from query.core import *
from query.helpers import setup_demo_env
import os
import pandas as pd
import sqlalchemy



# Global setup function. Download DBs if missing.
def my_setup():
    # Set fake environmental variables, tests this functionality implicitly througout
    setup_demo_env()
    if not os.path.exists("sample_data/Chinook_Sqlite.sqlite"):
        raise Exception("Necessary Chinook SQLite test database not found.")


@with_setup(my_setup)
def test_querydb_init_sqlite():
    # Test that init w/ environmental variables works
    db = QueryDb()
    assert db.__class__ is QueryDb

    # Test normal initialization
    db = QueryDb(drivername="sqlite", database="sample_data/Chinook_Sqlite.sqlite")

    # Basic proper initialization tests
    assert db.__class__ is QueryDb
    assert db.inspect.__class__ is QueryDbAttributes
    assert db._meta.__class__ is QueryDbMeta
    assert db.test_connection()
    assert db.__repr__() == "Working connection to a remote SQLITE DB: Chinook_Sqlite.sqlite"


# Note no setup, as called in demo=True condition
def test_querydb_demo():
    db = QueryDb(demo=True)
    assert db.test_connection()


@with_setup(my_setup)
def test_querydb_query():
    db = QueryDb()

    with assert_raises(sqlalchemy.exc.OperationalError):
        db.query("SELECT * FROM genres")  # table is genre
    df = db.query("SELECT * FROM genre")
    assert df.__class__ is pd.DataFrame  # Default result
    assert df.shape == (25, 2)

    res = db.query("SELECT * FROM genre", return_as="result")
    assert res.__class__ == sqlalchemy.engine.result.ResultProxy
    with assert_raises(sqlalchemy.exc.ResourceClosedError):
        res.fetchall()  # Fails for sqlite

    # And that those are all the values and properly returned by last
    # Note: last takes a DESC index and so we need to reverse the df here
    assert (df.Name.values[::-1] == db.i.Genre.last(25).Name.values).all()

    # Finally test .q() shorthand
    assert (df == db.q("SELECT * FROM genre")).all().all()


@with_setup(my_setup)
def test_query_db_inspect():
    db = QueryDb()

    # Table-wise
    assert db.inspect.Track.__class__ == QueryDbOrm
    assert db.inspect.Track.table.__class__ == sqlalchemy.sql.schema.Table

    # Column-wise
    assert db.inspect.Track.Composer.__class__ == QueryDbOrm  # Yes, maybe subclass these in the future
    assert db.inspect.Track.Composer.table.__class__ == sqlalchemy.sql.schema.Table
    assert db.inspect.Track.Composer.column.__class__ == sqlalchemy.sql.schema.Column
    assert db.inspect.Track.Composer.column.name == "Composer"


@with_setup(my_setup)
def test_query_db_attr_methods():
    db = QueryDb()

    # Test last method - note this column .Composer syntax is bc everything is a DataFrame, not a Series
    assert db.inspect.Track.Composer.last().Composer.values[0] == 'Philip Glass'
    assert (db.inspect.Track.Composer.last().Composer.values[0] ==
            db.inspect.Track.Composer.tail().Composer.values[0])  # equivalency

    # Test head method
    assert db.inspect.Genre.head().Name.values[0] == 'Rock'
    assert db.inspect.Genre.head().Name.values[1] == 'Jazz'

    # Test by= keyword
    assert (db.inspect.Track.head(n=5, by="Milliseconds").Milliseconds.values < 10000).all()  # Some very short tunes

    # Test where
    assert len(db.inspect.Track.where("composer == 'Philip Glass'")) == 1 # :(
