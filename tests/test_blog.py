import pytest
from flask import g, session
from flaskr.db import get_db
from sqlalchemy import select, update
from flaskr.db_alchemy import db_session
from flaskr.data_model import User, Post


def test_index(client, auth):
    """
    Checks that page displays login credentials correctly
    """
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'Test Post' in response.data
    assert b'A full body of text to test' in response.data
    assert b'href="/1/update"' in response.data

@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    """
    Tests that users are required to login to access CRUDI features
    """
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_author_required(app, client, auth):
    """
    Tests that CRUDI features are specific to users posts
    """
    # change the post author to another user
    with app.app_context():
        other_id = select(User).where(User.name == 'other_tester').first().id
        stmt = update(Post).where(Post.author_id == session['user_id']).values(author_id = other_id)
        session.execute(stmt)

    auth.login()
    # current user can't modify other user's post
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get('/').data


@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404