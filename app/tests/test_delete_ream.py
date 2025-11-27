import pytest
from unittest import mock
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['DATABASE'] = ':memory:'
    with app.test_client() as client:
        yield client

def login_admin(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    patcher = mock.patch('flask_login.utils._get_user', return_value=mock.Mock(is_authenticated=True, is_admin=True))
    patcher.start()
    return patcher

def test_delete_team(client):
    patcher = login_admin(client)
    with mock.patch('sqlite3.connect'):
        response = client.get('/delete_team/1')
        assert response.status_code == 302
    patcher.stop()