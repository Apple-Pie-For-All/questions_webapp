import pytest
from flask import g, session
from sqlalchemy import select, update, func
from flaskr.db_alchemy import db_session
from flaskr.data_model import User, Post


def test_view(client, auth):
    """
    Checks that view page displays a post correctly
    """
    with client:
        auth.login()
        post = db_session.scalars(select(Post)).first()
    response = client.get('/' + str(post.id))

    assert b"Log Out" in response.data

    assert post.title.encode() in response.data
    assert post.body.encode() in response.data

def test_commenting_requires_text(client, auth):
    with client:
        auth.login()
        stmt = select(Post)
        post_to_comment = db_session.scalars(stmt).first().id
        url_for_comment = '/' + str(post_to_comment) + '/comment'

        response = client.post(url_for_comment, data={'text': ''}, follow_redirects=True)
        assert b'Comment text is required' in response.data
