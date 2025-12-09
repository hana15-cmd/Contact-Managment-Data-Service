import pytest
from app import create_app

@pytest.fixture(scope="session")
def app():
    application = create_app()
    application.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="test-secret",
    )
    return application

@pytest.fixture()
def client(app):
    return app.test_client()

def test_home_route_smoke(client):
    resp = client.get("/")
    assert resp.status_code in (200, 302)

def test_contacts_route_smoke(client):
    # Protected route should not 500; unauth users get redirect
    resp = client.get("/contactManager")
    assert resp.status_code in (200, 302)