import pytest
from flask import g, session
from flaskr.db import get_db
from flaskr.data_model import User, Post
from sqlalchemy import event, select


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert select(User).where(User.name=='a').one() is not None