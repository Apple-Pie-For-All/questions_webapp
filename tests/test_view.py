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
    response = client.get('/' + str(post.id) + "/view")
    
    assert b"Log Out" in response.data

    assert post.title.encode() in response.data
    assert post.body.encode() in response.data