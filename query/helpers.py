import query
import os


def setup_demo_env():
    os.environ["QUERY_DB_DRIVER"] = "sqlite"
    os.environ["QUERY_DB_NAME"] = os.path.join(
        os.path.split(os.path.abspath(query.__file__))[0],
        "sample_data/Chinook_Sqlite.sqlite")

    if os.environ.get("QUERY_DB_HOST") is not None:
        os.environ.pop("QUERY_DB_HOST")
    if os.environ.get("QUERY_DB_PORT") is not None:
        os.environ.pop("QUERY_DB_PORT")
