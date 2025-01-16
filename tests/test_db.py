import sqlite3

import pytest
from flaskr.db import get_db
from flaskr.db_alchemy import db_session


def test_db_session_lifecycle(app):
    # Ensure the app is in the correct context
    with app.app_context():
        session1 = db_session
        session2 = db_session

        # Assert that sessions within the same context are the same
        assert session1 is session2

        # Perform an operation to confirm session functionality
        session1.execute("SELECT 1") 

        # Close the session
        session1.remove()
        
        with pytest.raises(Exception) as e:
            session1.execute("SELECT 1") 
        assert "closed" in str(e.value).lower()

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