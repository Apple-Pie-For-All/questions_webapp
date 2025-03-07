import pytest, uuid
from flask import g, session, url_for
from sqlalchemy import select, update, func
from flaskr.db_alchemy import db_session
from flaskr.data_model import User, Post


def test_index(client, auth):
    """
    Checks that page displays login credentials correctly
    """
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    with client:
        auth.login()
        user_post = db_session.scalars(select(Post)
                                          .where(Post.author_id == session['user_id'])
                                          ).first()
        update_url = ('href="/' + str(user_post.id) + '/update"').encode()
        response = client.get('/')
    assert b'Log Out' in response.data
    assert b'Test Post' in response.data
    assert b'A full body of text to test' in response.data
    assert update_url in response.data

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


def test_author_required(client, auth):
    """
    Tests that CRUDI features are specific to users posts
    """
    # change the post author to another user
    with client:
        auth.login()
        user_post = db_session.scalars(select(Post)
                                          .where(Post.author_id == session['user_id'])
                                          ).first()
        other_id = db_session.scalars(select(User)
                                      .where(User.name == 'other_tester')
                                     ).first().id
        stmt = update(Post).where(Post.author_id == session['user_id'])\
                           .values(author_id = other_id)
        db_session.execute(stmt)
        db_session.commit()

        # current user can't modify other user's post
        assert client.post(url_for('blog.update', id=user_post.id)).status_code == 403
        assert client.post(url_for('blog.delete', id=user_post.id)).status_code == 403
        # current user doesn't see edit link
        update_url = ('href="/' + str(user_post.id) + '/update"').encode()
        assert update_url not in client.get('/').data


@pytest.mark.parametrize('path', (
    'update',
    'delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    url = '/' + str(uuid.uuid4()) + '/' + path
    assert client.post(url).status_code == 404

def test_create(client, auth, app):
    """
    Tests create post function
    """
    stmt = select(func.count(Post.id))
    prev_count = db_session.scalar(stmt)
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': ''})

    stmt = select(func.count(Post.id))
    count = db_session.scalar(stmt)
    assert count == prev_count + 1


def test_update(client, auth, app):
    """
    Tests update post function
    """
    with client:
        auth.login()
        stmt = select(Post).where(Post.author_id == session['user_id'])
        post_to_update = db_session.scalars(stmt).first().id
        url_for_update = '/' + str(post_to_update) + '/update'
        assert client.get(url_for_update).status_code == 200
        client.post(url_for_update, data={'title': 'updated', 'body': ''})

    stmt = select(Post).where(Post.id == post_to_update)
    post = db_session.scalars(stmt).first()
    # db = get_db()
    # post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
    assert post.title == 'updated'

@pytest.mark.parametrize('path_func', (
    '/create',
    lambda test_session: f"/{str(test_session.scalars(select(Post).where(Post.author_id == session['user_id'])).first().id)}/update",
))
def test_create_update_validate(client, auth, path_func, test_session):
    """
    Tests validation of create/update forms with UUID-based IDs
    """
    with client:
        auth.login()
        path = path_func(test_session) if callable(path_func) else path_func
        response = client.post(path, data={'title': '', 'body': ''})
        assert b'Title is required.' in response.data


def test_delete(client, auth, app):
    """
    Tests delete functionality
    """
    with client:
        auth.login()
        stmt = select(Post).where(Post.author_id == session['user_id'])
        post_to_delete = db_session.scalars(stmt).first().id
        url_for_delete = '/' + str(post_to_delete) + '/delete'
        response = client.post(url_for_delete)

    # Should redirect to index when successful
    assert response.headers["Location"] == "/"

    with client:
        stmt = select(Post).where(Post.id == post_to_delete)
        post = db_session.scalars(stmt).first()
        # db = get_db()
        # post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()

        # Post should no longer exist
        assert post is None

def test_delete_requires_login(client, auth):
    """
    Not coming up in test coverage report, otherwise redundant with test_author_required
    """
    with client:
        auth.login()
        stmt = select(Post).where(Post.author_id != session['user_id'])
        post_to_delete = db_session.scalars(stmt).first().id
        url_for_delete = '/' + str(post_to_delete) + '/delete'
        response = client.post(url_for_delete)

    assert response.status_code == 403
