from nose.tools import *  # noqa
from query.helpers import setup_demo_env
import os


def test_demo_setup():
    setup_demo_env()
    assert os.environ.get("QUERY_DB_DRIVER") is "sqlite"
    assert os.environ.get("QUERY_DB_HOST") is None
    assert os.environ.get("QUERY_DB_PORT") is None

    # Test override of existing host/port params
    os.environ["QUERY_DB_HOST"] = "bad_host"
    os.environ["QUERY_DB_PORT"] = "9999"
    setup_demo_env()
    assert os.environ.get("QUERY_DB_HOST") is None
    assert os.environ.get("QUERY_DB_PORT") is None
