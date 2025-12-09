from flask.testing import FlaskClient
import pytest
from unittest import mock
from app import create_app

class FakeUser:
    def __init__(self, id=1, is_admin=False):
        self.id = id
        self.is_admin = is_admin
    @property
    def is_authenticated(self): return True
    @property
    def is_active(self): return True
    @property
    def is_anonymous(self): return False
    def get_id(self): return str(self.id)

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret'  # ensure session works
    app.config['DATABASE'] = ':memory:'
    with app.test_client() as client:
        yield client

def login(client):
    client.get("/")  # prime session backend
    with client.session_transaction() as sess:
        sess["_user_id"] = "1"
        sess["_fresh"] = True

# def test_add_team_get(client: FlaskClient):
#     with mock.patch('app.user_auth.User.get_by_id', return_value=FakeUser(1)):
#         login(client)
#         response = client.get('/add_team')
#         assert response.status_code == 200

def test_add_team_post(client: FlaskClient):
    with mock.patch('app.user_auth.User.get_by_id', return_value=FakeUser(1)):
        login(client)
        with mock.patch('app.forms.AddTeamForm.validate_on_submit', return_value=True), \
             mock.patch('app.forms.AddTeamForm.team_name', new_callable=mock.PropertyMock, return_value=mock.Mock(data='Team')), \
             mock.patch('app.forms.AddTeamForm.team_location', new_callable=mock.PropertyMock, return_value=mock.Mock(data='Location')), \
             mock.patch('app.forms.AddTeamForm.number_of_team_members', new_callable=mock.PropertyMock, return_value=mock.Mock(data=5)), \
             mock.patch('app.forms.AddTeamForm.team_email_address', new_callable=mock.PropertyMock, return_value=mock.Mock(data='team@email.com')), \
             mock.patch('sqlite3.connect'):
            response = client.post('/add_team')
            # Success may redirect
            assert response.status_code in (200, 302)

# def test_add_team_post_invalid(client: FlaskClient):
#     with mock.patch('app.user_auth.User.get_by_id', return_value=FakeUser(1)):
#         login(client)
#         with mock.patch('app.forms.AddTeamForm.validate_on_submit', return_value=False):
#             response = client.post('/add_team')
#             # Invalid submission should re-render the form
#             assert response.status_code == 200

def test_add_team_requires_login(client: FlaskClient):
    # No mock/login → should redirect
    response = client.get('/add_team')
    assert response.status_code == 302
    response = client.post('/add_team')
    assert response.status_code == 302