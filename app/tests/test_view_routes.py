import pytest
from flask import url_for

from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config.update( {
        "TESTING": True,
        "WTF_CSRF_ENABLED": False  # Disable CSRF for testing
    } )

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_add_team(client):
    response = client.post( '/signup', data={
        'email': 'test@example.com',
        'first_name': 'Test',
        'password': 'Password123!',
        'user_type': 'admin'
    }, follow_redirects=True )
    assert response.status_code == 200

    response = client.post( '/login/', data={
        'email': 'test@example.com',
        'password': 'Password123!',
    }, follow_redirects=True )
    assert response.status_code == 200

    response = client.post( '/add_team', data={
        "team_name": "test_team",
        "team_location": "London",
        "number_of_team_members": 1,
        "team_email_address": "test_team@outlook.com"
    }, follow_redirects=True )
    assert response.status_code == 200

    assert response is not None


