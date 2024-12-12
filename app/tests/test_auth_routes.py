import pytest
from app.user_auth import User
import app from 

@pytest.fixture
def test_signup(app,auth):
    auth.signup('Test','test@outlook.com','Password123!','Password123!','regular')
    assert User.query.count() == 1
    assert User.query.first().email == 'test@outlook.com'
