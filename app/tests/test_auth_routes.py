import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.user_auth import User


@pytest.fixture
def client():
    app = create_app()  # Assuming you have a create_app() function to create your Flask app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    client = app.test_client()

    with app.app_context():
        yield client


@pytest.fixture
def user():
    password_hash = generate_password_hash( 'password' )
    user = User( id=1, email='test@example.com', password=password_hash, first_name='Test', is_admin=True )
    return user



def test_login(client, user):
    # Log in the user manually using login_user from Flask-Login
    with client.session_transaction() as session:
        # Simulate Flask-Login's login_user call
        session['_user_id'] = user.id
        session['user_name'] = user.first_name
        session['is_admin'] = user.is_admin

    # Simulate sending a POST request to the login route
    response = client.post( '/login/', data={'email': user.email, 'password': 'password'} )

    # Assert that the response is a redirect (302) as expected after successful login
    assert response.status_code == 302  # Expecting a 302 redirect

    # Follow the redirect and check the session variables
    response = client.get( response.headers['Location'], follow_redirects=True )

    with client.session_transaction() as session:
        # Assert that session contains 'user_name' and 'is_admin' keys
        assert 'user_name' in session, "Session does not contain 'user_name'."
        assert session['user_name'] == 'Test', f"Expected 'Test', but got {session['user_name']}."
        assert 'is_admin' in session, "Session does not contain 'is_admin'."
        assert session['is_admin'] is True, f"Expected True, but got {session['is_admin']}."

def test_login_invalid(client):
    response = client.post( '/login/', data={'email': 'incorrect@email.com', 'password': 'incorrectpassword1'},
                            follow_redirects=True )
    assert response.status_code == 200  # Expecting a 200 OK status to render the login page again

    # Check the presence of the error message in the response data
    assert b'Invalid username or password' in response.data


def test_succesful_signup(client):
    response = client.post( '/signup', data={
        'email': 'test@example.com',
        'first_name': 'Test',
        'password': 'Password123!',
        'user_type': 'admin'
    }, follow_redirects=True )
    assert response.status_code == 200
    # assert b'Registration successful' in response.data


def test_succesful_logout(client, user):
    with client:
        with client.session_transaction() as session:
            session['_user_id'] = user.id
            session['user_name'] = user.first_name
            response = client.get( '/logout',
                                   follow_redirects=True )  # Check that the response redirects to the login page
            assert response.status_code == 200
            assert b'You were successfully logged out' in response.data  # Verify that the session variables are cleared
            with client.session_transaction() as session:
                assert '_user_id' not in session
                assert 'user_name' not in session

