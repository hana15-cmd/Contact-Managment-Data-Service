import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.user_auth import User

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user(app):
    # If your app uses a DB, add the user to the DB here.
    # Otherwise, ensure your login route can find this user.
    password_hash = generate_password_hash('password')
    user = User(id=1, email='test@example.com', password=password_hash, first_name='Test', is_admin=True)
    # If needed: db.session.add(user); db.session.commit()
    return user

def test_login(client, user):
    response = client.post('/login/', data={'email': user.email, 'password': 'password'}, follow_redirects=False)
    # If your login route redirects after login, expect 302/303
    # If it renders a page, expect 200
    assert response.status_code in (200, 302, 303)
    if response.status_code in (302, 303) and 'Location' in response.headers:
        # Follow the redirect and check for a successful page load
        response = client.get(response.headers['Location'], follow_redirects=True)
        assert response.status_code == 200

def test_login_invalid(client):
    response = client.post('/login/', data={'email': 'incorrect@email.com', 'password': 'incorrectpassword1'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_successful_signup(client):
    response = client.post('/signup', data={
        'email': 'newuser@example.com',
        'first_name': 'NewUser',
        'password': 'Password123!',
        'user_type': 'admin'
    }, follow_redirects=True)
    assert response.status_code == 200
    # assert b'Registration successful' in response.data  # Uncomment if your template shows this

def test_signup_duplicate_email(client, user):
    # Try to sign up with an email that already exists
    response = client.post('/signup', data={
        'email': user.email,
        'first_name': 'Test',
        'password': 'Password123!',
        'user_type': 'admin'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Email already registered' in response.data  # Adjust message as per your app

def test_successful_logout(client, user):
    # Log in first (simulate session)
    with client.session_transaction() as session:
        session['_user_id'] = user.id
        session['user_name'] = user.first_name
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You were successfully logged out' in response.data
    with client.session_transaction() as session:
        assert '_user_id' not in session
        assert 'user_name' not in session

def test_login_missing_fields(client):
    response = client.post('/login/', data={'email': '', 'password': ''}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data  # Or your app's error message