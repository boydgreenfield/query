from nose.tools import *  # noqa
from query.core import *  # noqa
from query.helpers import setup_demo_env
import query
import os
import pandas as pd
import sqlalchemy
import warnings


# Global setup function. Download DBs if missing.
def my_setup():
    # Set fake environmental variables, tests this functionality implicitly throughout
    setup_demo_env()
    if not os.path.exists(os.environ.get("QUERY_DB_NAME")):
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
    assert db.test_connection()
    assert db.__repr__() == "Working connection to a remote SQLITE DB: Chinook_Sqlite.sqlite"

    # And test if connection is broken / or _engine.begin() chokes
    def _raise(exc):
        raise exc

    db._engine.begin = lambda: _raise(sqlalchemy.exc.OperationalError("Bad test conn", "", ""))
    assert db.__repr__() == "Inactive connection to a remote SQLITE DB: Chinook_Sqlite.sqlite"
    assert True


# Note no setup, as called in demo=True condition
def test_querydb_demo():
    db = QueryDb(demo=True)
    assert db.test_connection()


@with_setup(my_setup)
def test_getpass():
    os.environ["QUERY_DB_DRIVER"] = "mysql"  # Trick to prompt for PW, disabled for sqlite
    query.core.getpass.getpass = lambda _: "Fake testing password"
    with assert_raises(sqlalchemy.exc.OperationalError):  # can't load bc no mysql db
        QueryDb()

    # Now test interactive path
    pd.core.common.in_ipnb = lambda: True
    with assert_raises(sqlalchemy.exc.OperationalError):  # still fails bc mysql
        QueryDb()

    # And finally test graceful failure w/o IPython
    import sys
    ipy_module = sys.modules['IPython']
    sys.modules['IPython'] = None
    with assert_raises(sqlalchemy.exc.OperationalError):  # still fails bc mysql
        QueryDb()

    sys.modules['IPython'] = ipy_module


@with_setup(my_setup)
def test_querydborm():
    db = QueryDb()
    assert db.inspect.__class__ is QueryDbAttributes
    assert db.inspect._repr_html_() == query.html.QUERY_DB_ATTR_MSG
    assert db._meta.__class__ is QueryDbMeta
    assert db.inspect.Track.__class__ is QueryDbOrm
    assert db.inspect.Track._repr_html_() == db.inspect.Track._html

    # Track is a sqlalchemy Table obj.
    assert db.inspect.Track.__repr__() == db.inspect.Track.table.__repr__()
    assert db.inspect.Track.Composer.__repr__() == db.inspect.Track.Composer.column.__repr__()


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
    with assert_raises(sqlalchemy.exc.ProgrammingError):
        res.fetchall()  # Fails for sqlite

    # And that those are all the values and properly returned by last
    # Note: last takes a DESC index and so we need to reverse the df here
    assert (df.Name.values[::-1] == db.inspect.Genre.last(25).Name.values).all()

    # And test failures:
    # - wrong input
    with assert_raises(QueryDbError):
        db.query(1)

    # - bad return type
    with assert_raises(QueryDbError):
        db.query("SELECT * FROM Tracks", return_as="junk")


@with_setup(my_setup)
def test_querydb_multi_primary_keys():
    db = QueryDb()
    with warnings.catch_warnings(True) as w:
        db.inspect.PlaylistTrack.last()
        assert len(w) >= 1

    db.inspect.Track.table.primary_key.columns = sqlalchemy.sql.base.ColumnCollection()
    with assert_raises(NoPrimaryKeyException):
        db.inspect.Track.last()


@with_setup(my_setup)
def test_query_db_inspect():
    db = QueryDb()

    # Table-wise
    assert db.inspect.Track.__class__ == QueryDbOrm
    assert db.inspect.Track.table.__class__ == sqlalchemy.sql.schema.Table

    # Column-wise
    assert db.inspect.Track.Composer.__class__ == QueryDbOrm  # Potentially subclass in the future
    assert db.inspect.Track.Composer.table.__class__ == sqlalchemy.sql.schema.Table
    assert db.inspect.Track.Composer.column.__class__ == sqlalchemy.sql.schema.Column
    assert db.inspect.Track.Composer.column.name == "Composer"


@with_setup(my_setup)
def test_query_db_attr_methods():
    db = QueryDb()

    # Test last method - note this column .Composer syntax is bc everything is a DataFrame
    assert db.inspect.Track.Composer.last().Composer.values[0] == 'Philip Glass'
    assert (db.inspect.Track.Composer.last().Composer.values[0] ==
            db.inspect.Track.Composer.tail().Composer.values[0])  # equivalency

    # Test head method
    assert db.inspect.Genre.head().Name.values[0] == 'Rock'
    assert db.inspect.Genre.head().Name.values[1] == 'Jazz'

    # Test by= keyword
    assert (db.inspect.Track.head(n=5, by="Milliseconds").Milliseconds.values < 10000).all()

    # Test where
    assert len(db.inspect.Track.where("composer == 'Philip Glass'")) == 1  # :(
