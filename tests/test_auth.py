import pytest
from flask import g, session
from flaskr.db_alchemy import db_session
from flaskr.data_model import User, Post
from sqlalchemy import event, select


def test_register(client, app):
    """
    Test that the register page is reachable and allows new users to regist
    """
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert db_session.scalars(select(User).where(User.name=='a')).first() is not None

# Parametrized arguements for next function args
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('tester', 'test_password', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    """
    Test that various mis-inputs for the register page return the appropiate error
    """
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data

def test_login(client, auth):
    """
    Test that users can login successfully
    """
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        assert session['user_id'] == db_session.scalars(select(User).where(User.name == 'tester')).first().id
        assert g.user.name == 'tester'

def test_logout_works(client, auth):
    with client:
        auth.login()
        assert session['user_id'] is not None
        auth.logout()
        assert session.get('user_id') is None # direct key access results in error if not there
        response = client.get('/')
        assert b'Log In' in response.data


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test_password', b'Incorrect username.'),
    ('tester', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    """
    Test that incorrect logins get the appropiate error
    """
    response = auth.login(username, password)
    assert message in response.data