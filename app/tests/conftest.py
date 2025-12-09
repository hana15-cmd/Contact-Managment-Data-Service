import pathlib
import sqlite3
import pytest
from unittest import mock
from app import create_app

SCHEMA_FILE = pathlib.Path(__file__).parent.parent / "database_logic" / "schemadb.sql"

def _load_schema(db_file: str):
    with sqlite3.connect(db_file) as con, open(SCHEMA_FILE) as f:
        con.executescript(f.read())

@pytest.fixture(scope="session")
def app(tmp_path_factory):
    # Create a temp DB per test session
    db_path = str(tmp_path_factory.mktemp("db") / "test.db")
    application = create_app()
    application.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="test-secret",
        DATABASE=db_path,
    )
    _load_schema(db_path)
    return application

@pytest.fixture()
def client(app):
    # Ensure schema exists before each test
    _load_schema(app.config["DATABASE"])
    return app.test_client()

def login(client, user_id="1", is_admin=False):
    # Prime the session backend
    client.get("/")
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
    # Mock user resolution for Flask-Login
    patcher = mock.patch(
        "app.user_auth.User.get_by_id",
        return_value=type("U", (), {
            "id": int(user_id),
            "is_authenticated": True,
            "is_active": True,
            "is_anonymous": False,
            "is_admin": is_admin,
            "get_id": lambda self: str(user_id),
        })()
    )
    patcher.start()
    return patcher

def login_admin(client):
    return login(client, user_id="1", is_admin=True)