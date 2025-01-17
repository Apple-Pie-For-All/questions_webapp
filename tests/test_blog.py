import pytest
from flaskr.db import get_db


def test_index(client, auth):
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'Test Post' in response.data
    assert b'A full body of text to test' in response.data
    assert b'href="/1/update"' in response.data