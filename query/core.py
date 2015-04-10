import getpass
import sqlalchemy
import numpy as np
import pandas as pd
import os
import warnings

import query
from query.html import df_to_html, GETPASS_USE_WARNING, QUERY_DB_ATTR_MSG


# Exceptions
class QueryDbError(Exception):
    pass


class NoPrimaryKeyException(Exception):
    pass


# Helper classes
class QueryDbAttributes(object):
    def _repr_html_(self):
        return QUERY_DB_ATTR_MSG


class QueryDbMeta(sqlalchemy.schema.MetaData):
    pass


# Main classes
class QueryDbOrm(object):
    """
    A helper class for QueryDb -- allows making Sqlalchemy schema
    (Tables and Columns) more accessible via the QueryDb interface
    and exposing additional helper methods, e.g., .last().
    """
    def __init__(self, orm_object, db):
        self._db = db
        if orm_object.__class__ == sqlalchemy.schema.Table:
            self._is_table = True
            self.table = orm_object
            self.column = None

            # Support custom styling of Pandas dataframe by calling .to_html() over _repr_html()
            # incl. not displaying dimensions, for example
            self._column_df = pd.DataFrame(
                [(c.name, c.type, c.primary_key) for c in self.table.columns.values()],
                columns=["Column", "Type", "Primary Key"]
            )
            self._html = df_to_html(self._column_df, ("Column Information for the %s Table"
                                                      % self.table.name))

        else:
            self._is_table = False
            self.table = orm_object.table
            self.column = orm_object
            self._html = ("<em>Inspecting column %s of the %s table. "
                          "Try the .head(), .tail(), and .where() "
                          "methods to further explore.<em>" %
                          (self.column.name, self.table.name))

    def _repr_html_(self):
        return self._html

    def __repr__(self):
        if self._is_table:
            return self.table.__repr__()
        else:
            return self.column.__repr__()

    def _query_helper(self, by=None):
        """
        Internal helper for preparing queries.
        """
        if by is None:
            primary_keys = self.table.primary_key.columns.keys()

            if len(primary_keys) > 1:
                warnings.warn("WARNING: MORE THAN 1 PRIMARY KEY FOR TABLE %s. "
                              "USING THE FIRST KEY %s." %
                              (self.table.name, primary_keys[0]))

            if not primary_keys:
                raise NoPrimaryKeyException("Table %s needs a primary key for"
                                            "the .last() method to work properly. "
                                            "Alternatively, specify an ORDER BY "
                                            "column with the by= argument. " %
                                            self.table.name)
            id_col = primary_keys[0]
        else:
            id_col = by

        if self.column is None:
            col = "*"
        else:
            col = self.column.name

        return col, id_col

    def head(self, n=10, by=None, **kwargs):
        """
        Get the first n entries for a given Table/Column. Additional keywords
        passed to QueryDb.query().

        Requires that the given table has a primary key specified.
        """
        col, id_col = self._query_helper(by=by)

        select = ("SELECT %s FROM %s ORDER BY %s ASC LIMIT %d" %
                  (col, self.table.name, id_col, n))

        return self._db.query(select, **kwargs)

    def tail(self, n=10, by=None, **kwargs):
        """
        Get the last n entries for a given Table/Column. Additional keywords
        passed to QueryDb.query().

        Requires that the given table has a primary key specified.
        """
        col, id_col = self._query_helper(by=by)

        select = ("SELECT %s FROM %s ORDER BY %s DESC LIMIT %d" %
                  (col, self.table.name, id_col, n))

        return self._db.query(select, **kwargs)

    def first(self, n=10, by=None, **kwargs):
        """
        Alias for .head().
        """

    def last(self, n=10, by=None, **kwargs):
        """
        Alias for .tail().
        """
        return self.tail(n=n, by=by, **kwargs)

    def where(self, where_string, **kwargs):
        """
        Select from a given Table or Column with the specified WHERE clause
        string. Additional keywords are passed to ExploreSqlDB.query(). For
        convenience, if there is no '=', '>', '<', 'like', or 'LIKE' clause
        in the WHERE statement .where() tries to match the input string
        against the primary key column of the Table.

        Args:
            where_string (str): Where clause for the query against the Table
            or Column

        Kwars:
            **kwargs: Optional **kwargs passed to the QueryDb.query() call

        Returns:
            result (pandas.DataFrame or sqlalchemy ResultProxy): Query result
            as a DataFrame (default) or sqlalchemy result.
        """
        col, id_col = self._query_helper(by=None)

        where_string = str(where_string)  # Coerce here, for .__contains___
        where_operators = ["=", ">", "<", "LIKE", "like"]
        if np.any([where_string.__contains__(w) for w in where_operators]):
            select = ("SELECT %s FROM %s WHERE %s" %
                      (col, self.table.name, where_string))
        else:
            select = ("SELECT %s FROM %s WHERE %s = %s" %
                      (col, self.table.name, id_col, where_string))

        return self._db.query(select, **kwargs)


class QueryDb(object):
    """
    A database object for interactively exploring a SQL database.
    """
    def __init__(self, drivername=None, database=None,
                 host=None, port=None,
                 password=None, username=None,
                 use_env_vars=True, demo=False):
        """
        Initialize and test the connection.

        Kwargs:
           drivername (str): Drivername passed to sqlalchemy.

           database (str): Name of the database.

           host (str): IP address for the host to connect to.

           port (int): Port to connect on.

           username (str): Username for the database.

           password (str): Optionally specify a password. Defaults to None,
           which prompts the user for a password using getpass.

           use_env_vars (bool): Use environmental variables if specified?

        Returns:
           engine: The sqlalchemy database engine.

        Raises:
            OperationalError
        """
        # Demo mode w/ included dummy database
        if demo:
            drivername = "sqlite"
            database = os.path.join(
                os.path.split(os.path.abspath(query.__file__))[0],
                "sample_data/Chinook_Sqlite.sqlite")
            use_env_vars = False

        # Check if the host, port. or database name options are overwritten
        # by environmental variables
        environ_driver = os.environ.get('QUERY_DB_DRIVER')
        environ_host = os.environ.get('QUERY_DB_HOST')
        environ_port = os.environ.get('QUERY_DB_PORT')
        environ_name = os.environ.get('QUERY_DB_NAME')
        if environ_driver is not None and use_env_vars:
            drivername = environ_driver
        if environ_host is not None and use_env_vars:
            host = environ_host
        if environ_port is not None and use_env_vars:
            port = environ_port
        if environ_name is not None and use_env_vars:
            database = environ_name

        # Note: This will require the user's terminal to be open. In the
        # case of IPython QtConsole or Notebook, this will be the terminal
        # from which the kernel was launched
        if password is None and drivername != "sqlite":  # sqlite does not support pwds
            password = os.environ.get('QUERY_DB_PASS')
            if password is None:
                if pd.core.common.in_ipnb():
                    # Display a somewhat obnoxious warning to the user
                    try:
                        from IPython.display import display, HTML
                        display(HTML(GETPASS_USE_WARNING))
                    except ImportError:
                        pass
                password = getpass.getpass(
                    "Please enter the %s server password:" % drivername)

        # Connection
        url = sqlalchemy.engine.url.URL(
            drivername=drivername,
            username=username,
            password=password,
            host=host,
            port=port,
            database=database)
        engine = sqlalchemy.create_engine(url)

        # Tests the connection
        with engine.begin():
            pass

        # Set the engine ane metadata
        self._engine = engine
        self._summary_info = []
        self._set_metadata()

        # Finally, set some pretty printing params
        # (schema diagram setup to go here)
        self._db_name = database.split("/")[-1].split(":")[0]
        self._summary_info = pd.DataFrame(self._summary_info,
                                          columns=["Table", "Primary Key(s)",
                                                   "# of Columns", "# of Column Types"])
        self._html = df_to_html(self._summary_info, "%s Database Summary" % self._db_name,
                                bold=True)

    def _repr_html_(self):
        return self._html

    def __repr__(self):
        if self.test_connection():
            c = "Working connection"
        else:
            c = "Inactive connection"
        return ("%s to a remote %s DB: %s" %
                (c, self._engine.name.upper(), self._db_name))

    def test_connection(self):
        """
        Test the connection to the QueryDb. Returns True if working.

        Returns:
            test_result (bool): Did the test pass?
        """
        try:
            with self._engine.begin():
                pass
            return True
        except sqlalchemy.exc.OperationalError:
            return False

    def query(self, sql_query, return_as="dataframe"):
        """
        Execute a raw SQL query against the the SQL DB.

        Args:
            sql_query (str): A raw SQL query to execute.

        Kwargs:
            return_as (str): Specify what type of object should be
            returned. The following are acceptable types:
            - "dataframe": pandas.DataFrame or None if no matching query
            - "result": sqlalchemy.engine.result.ResultProxy

        Returns:
            result (pandas.DataFrame or sqlalchemy ResultProxy): Query result
            as a DataFrame (default) or sqlalchemy result (specified with
            return_as="result")

        Raises:
            QueryDbError
        """
        if isinstance(sql_query, str):
            pass
        elif isinstance(sql_query, unicode):
            sql_query = str(sql_query)
        else:
            raise QueryDbError("query() requires a str or unicode input.")

        query = sqlalchemy.sql.text(sql_query)

        if return_as.upper() in ["DF", "DATAFRAME"]:
            return self._to_df(query, self._engine)
        elif return_as.upper() in ["RESULT", "RESULTPROXY"]:
            with self._engine.connect() as conn:
                result = conn.execute(query)
                return result
        else:
            raise QueryDbError("Other return types not implemented.")

    def _set_metadata(self):
        """
        Internal helper to set metadata attributes.
        """
        meta = QueryDbMeta()
        with self._engine.connect() as conn:
            meta.bind = conn
            meta.reflect()
            self._meta = meta

        # Set an inspect attribute, whose subattributes
        # return individual tables / columns. Tables and columns
        # are special classes with .last() and other convenience methods
        self.inspect = QueryDbAttributes()
        for table in self._meta.tables:
            setattr(self.inspect, table,
                    QueryDbOrm(self._meta.tables[table], self))

            table_attr = getattr(self.inspect, table)
            table_cols = table_attr.table.columns

            for col in table_cols.keys():
                setattr(table_attr, col,
                        QueryDbOrm(table_cols[col], self))

            # Finally add some summary info:
            #   Table name
            #   Primary Key item or list
            #   N of Cols
            #   Distinct Col Values (class so NVARCHAR(20) and NVARCHAR(30) are not different)
            primary_keys = table_attr.table.primary_key.columns.keys()
            self._summary_info.append((
                table,
                primary_keys[0] if len(primary_keys) == 1 else primary_keys,
                len(table_cols),
                len(set([x.type.__class__ for x in table_cols.values()])),
                ))

    def _to_df(self, query, conn, index_col=None, coerce_float=True, params=None,
               parse_dates=None, columns=None):
        """
        Internal convert-to-DataFrame convenience wrapper.
        """
        return pd.io.sql.read_sql(str(query), conn, index_col=index_col,
                                  coerce_float=coerce_float, params=params,
                                  parse_dates=parse_dates, columns=columns)
