import sqlite3

import pytest
from flaskr.db import get_db


def test_get_close_db(app):

    # Expect the db to be the same with each call
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    # Expect db to be closed
    assert 'closed' in str(e.value)

def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False
    def fake_init_db():
        Recorder.called = True

    # Replace the true init_db command with the fake defined above
    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    # Runner mimics clicking on the button (triggers @click)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output # From @click
    assert Recorder.called # From patched fake_init_db