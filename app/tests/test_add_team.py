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

def login(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1

def test_add_team_get(client):
    login(client)
    response = client.get('/add_team', follow_redirects=True)
    assert response.status_code == 200

def test_add_team_post(client):
    login(client)
    with mock.patch('app.forms.AddTeamForm.validate_on_submit', return_value=True), \
         mock.patch('app.forms.AddTeamForm.team_name', new_callable=mock.PropertyMock, return_value=mock.Mock(data='Team')), \
         mock.patch('app.forms.AddTeamForm.team_location', new_callable=mock.PropertyMock, return_value=mock.Mock(data='Location')), \
         mock.patch('app.forms.AddTeamForm.number_of_team_members', new_callable=mock.PropertyMock, return_value=mock.Mock(data=5)), \
         mock.patch('app.forms.AddTeamForm.team_email_address', new_callable=mock.PropertyMock, return_value=mock.Mock(data='team@email.com')), \
         mock.patch('sqlite3.connect'):
        response = client.post('/add_team', follow_redirects=True)
        assert response.status_code == 200