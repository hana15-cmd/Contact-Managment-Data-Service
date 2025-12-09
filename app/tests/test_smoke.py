import pytest
from app import create_app

@pytest.fixture(scope="session")
def app():
    application = create_app()
    application.config.update(TESTING=True, WTF_CSRF_ENABLED=False, SECRET_KEY="test-secret")
    return application

@pytest.fixture()
def client(app):
    return app.test_client()

def test_home_route_smoke(client):
    resp = client.get("/")
    assert resp.status_code in (200, 302)

def test_contacts_route_smoke(client):
    resp = client.get("/contactManager")
    assert resp.status_code in (200, 302)

def test_login_page_smoke(client):
    # Ensure login view renders
    resp = client.get("/login/")
    assert resp.status_code in (200, 302)

def test_static_css_exists(client):
    # Static path should not 404 if styles.css is present
    resp = client.get("/static/styles.css")
    assert resp.status_code in (200, 304, 404)  # allow 404 if no CSS, but won’t 500

def test_not_found_smoke(client):
    # Unknown route returns 404 (no 500s)
    resp = client.get("/this-route-does-not-exist")
    assert resp.status_code == 404

def test_delete_team_requires_auth(client):
    resp = client.get("/delete_team/1")
    assert resp.status_code == 302
    loc = resp.headers.get("Location", "")
    assert ("/login" in loc) or (loc == "/")

def test_init_db_smoke(client):
    # init route should not 500; often redirects with flash
    resp = client.get("/init_db")
    assert resp.status_code in (200, 302)