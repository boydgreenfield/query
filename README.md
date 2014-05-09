# query
Python module for quick, interactive exploration of SQL databases. Designed especially for use with IPython. Light wrapper on top of Pandas (>= 0.14) and SQLAlchemy (>= 0.9.1).

*Please note*: As of May 8, 2014, Pandas v0.14 is still the development version. You must install it from Github, not via `pip`. Installation can be performed via:
`git clone https://github.com/pydata/pandas.git; cd pandas; python setup.py develop`.


## Quickstart
```python
from query import QueryDb
db = QueryDb(demo=True)
```

But the real joy comes when using query interactively:

![Interactive query use demo #1 ](docs/images/interactive_demo.gif?raw=True)

## Key functionality
A few key functions to remember:

* `db`: The main database object. Print it in IPython to see a list of tables and their key attributes.
* `db.inspect.*`: Tab-completion across the database's tables and columns. Print any table to see its columns and their types.
* `db.query()`: Query the database with a raw SQL query. Returns a `pandas DataFrame` object by default, but can return a `sqlalchemy result` object if called with `return_as="result"`.


## Roadmap
Further improvements are planned, including some of the below. Please feel free to open an Issue with desired features or submit a pull request.

* **Plotting**: Graphical display of queried data (some of this can easily be done off the current `DataFrame` object, but it could be better integrated)
* **More Convenience Methods**: Additional convenience methods, like ``.tail()`` and ``.where()``
* **DB Schemas**: Direct output of database schema diagrams
* **Password Input via IPython**: Currently entering a DB password uses `getpass` in the user's terminal. Being able to enter the password directly into IPython would be ideal (while also not writing it into any history)
* **More/Better Documentation**: Enough said.
