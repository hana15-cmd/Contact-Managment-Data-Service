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

def test_edit_team_get(client):
    login(client)
    with mock.patch('sqlite3.connect') as mock_con:
        mock_cur = mock.Mock()
        mock_cur.fetchone.side_effect = [{'TEAM_NAME':'Team','TEAM_LOCATION':'Loc','EMAIL_ADDRESS':'team@email.com'}, [5]]
        mock_con.return_value.cursor.return_value = mock_cur
        mock_con.return_value.row_factory = None
        response = client.get('/edit_team/1', follow_redirects=True)
        assert response.status_code == 200

def test_edit_team_post(client):
    login(client)
    with mock.patch('sqlite3.connect') as mock_con, \
         mock.patch('app.forms.EditTeamForm.validate_on_submit', return_value=True), \
         mock.patch('app.forms.EditTeamForm.team_name', new_callable=mock.PropertyMock, return_value=mock.Mock(data='Team')), \
         mock.patch('app.forms.EditTeamForm.team_location', new_callable=mock.PropertyMock, return_value=mock.Mock(data='Loc')), \
         mock.patch('app.forms.EditTeamForm.team_email_address', new_callable=mock.PropertyMock, return_value=mock.Mock(data='team@email.com')):
        mock_cur = mock.Mock()
        mock_cur.fetchone.side_effect = [{'TEAM_NAME':'Team','TEAM_LOCATION':'Loc','EMAIL_ADDRESS':'team@email.com'}, [5], [5]]
        mock_con.return_value.cursor.return_value = mock_cur
        mock_con.return_value.row_factory = None
        response = client.post('/edit_team/1', follow_redirects=True)
        assert response.status_code == 200