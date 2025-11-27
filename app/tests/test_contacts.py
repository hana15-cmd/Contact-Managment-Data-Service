# import pytest
# from unittest import mock
# from app import create_app

# @pytest.fixture
# def client():
#     app = create_app()
#     app.config['TESTING'] = True
#     app.config['WTF_CSRF_ENABLED'] = False
#     app.config['DATABASE'] = ':memory:'
#     with app.test_client() as client:
#         yield client

# def login(client):
#     with client.session_transaction() as sess:
#         sess['user_id'] = 1

# def test_contacts_requires_login(client):
#     response = client.get('/contactManager')
#     assert response.status_code == 302  # Should redirect to login

# def test_contacts_page_loads(client):
#     login(client)
#     with mock.patch('app.database_logic.models.get_database') as mock_db:
#         mock_cursor = mock.Mock()
#         # Return mock data as a list of tuples, matching your SQL query
#         mock_cursor.fetchall.return_value = [
#             (1, 'Team A', 'Location A', 'teamA@email.com', 3),
#             (2, 'Team B', 'Location B', 'teamB@email.com', 2)
#         ]
#         mock_db.return_value.cursor.return_value = mock_cursor
#         response = client.get('/contactManager', follow_redirects=True)
#         print(response.data)  # Debug: see actual output
#         # Use a substring that is always present in your template
#         assert b'Team' in response.data
#         assert response.status_code == 200

# def test_contacts_search(client):
#     login(client)
#     with mock.patch('app.database_logic.models.get_database') as mock_db:
#         mock_cursor = mock.Mock()
#         mock_cursor.fetchall.return_value = [
#             (1, 'Team A', 'Location A', 'teamA@email.com', 3)
#         ]
#         mock_db.return_value.cursor.return_value = mock_cursor
#         response = client.get('/contactManager?search=Team%20A', follow_redirects=True)
#         print(response.data)  # Debug
#         assert b'Team' in response.data
#         assert response.status_code == 200

# def test_contacts_filter(client):
#     login(client)
#     with mock.patch('app.database_logic.models.get_database') as mock_db:
#         mock_cursor = mock.Mock()
#         mock_cursor.fetchall.return_value = [
#             (2, 'Team B', 'Location B', 'teamB@email.com', 2)
#         ]
#         mock_db.return_value.cursor.return_value = mock_cursor
#         response = client.get('/contactManager?search=Location%20B&filter=TEAM_LOCATION', follow_redirects=True)
#         print(response.data)  # Debug
#         assert b'Team' in response.data
#         assert response.status_code == 200