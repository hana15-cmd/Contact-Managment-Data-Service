import os
import sys
import pytest

# Ensure the app package is discoverable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

def login(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1

def test_home_not_logged_in(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'homepage' in response.data or b'Home' in response.data

def test_home_logged_in_redirects(client):
    login(client)
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/contactManager' in response.headers['Location']

def test_contacts_requires_login(client):
    response = client.get('/contactManager')
    assert response.status_code == 302  # Should redirect to login

def test_contacts_page_loads(client):
    login(client)
    response = client.get('/contactManager', follow_redirects=True)
    assert response.status_code == 200
    assert b'Team' in response.data or b'Contact' in response.data