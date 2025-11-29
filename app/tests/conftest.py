import pathlib
import sqlite3
import pytest
from app import create_app

SCHEMA_FILE = pathlib.Path(__file__).parent.parent / "database_logic" / "schemadb.sql"

def _load_schema(db_file):
    with sqlite3.connect(db_file) as con, open(SCHEMA_FILE) as f:
        con.executescript(f.read())

@pytest.fixture(scope="session")
def app(tmp_path_factory):
    db_path = str(tmp_path_factory.mktemp("db") / "test.db")
    application = create_app()
    application.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="test",
        DATABASE=db_path,
    )
    _load_schema(db_path)
    return application

@pytest.fixture
def client(app):
    _load_schema(app.config["DATABASE"])
    with app.test_client() as c:
        yield c