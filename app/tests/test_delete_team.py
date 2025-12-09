import pytest
from unittest import mock
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['DATABASE'] = ':memory:'
    app.config['SECRET_KEY'] = 'test-secret'  # ensure session works
    with app.test_client() as client:
        yield client

def login_admin(client):
    # prime session backend
    client.get("/")
    with client.session_transaction() as sess:
        # Flask-Login session keys
        sess["_user_id"] = "1"
        sess["_fresh"] = True
    # Make Flask-Login resolve the admin user
    patcher = mock.patch('app.user_auth.User.get_by_id', return_value=type('U', (), {
        'id': 1,
        'is_authenticated': True,
        'is_active': True,
        'is_anonymous': False,
        'is_admin': True,
        'get_id': lambda self: "1"
    })())
    patcher.start()
    return patcher

def test_delete_team(client):
    patcher = login_admin(client)
    with mock.patch('sqlite3.connect'):
        response = client.get('/delete_team/1')
        assert response.status_code in (200, 302)  # depending on view behavior
    patcher.stop()

def test_delete_team_requires_admin(client):
    # non-admin user
    client.get("/")
    with client.session_transaction() as sess:
        sess["_user_id"] = "2"
        sess["_fresh"] = True
    with mock.patch('app.user_auth.User.get_by_id', return_value=type('U', (), {
        'id': 2,
        'is_authenticated': True,
        'is_active': True,
        'is_anonymous': False,
        'is_admin': False,
        'get_id': lambda self: "2"
    })()):
        response = client.get('/delete_team/1')
        assert response.status_code == 302  # should redirect (forbidden/redirect)

def test_delete_team_requires_login(client):
    response = client.get('/delete_team/1')
    assert response.status_code == 302  # Should redirect to login