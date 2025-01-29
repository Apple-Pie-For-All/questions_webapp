import sqlite3

import pytest
import warnings
from sqlalchemy import select
from flaskr.db_alchemy import db_session
from flaskr.data_model import User
from sqlalchemy.exc import IntegrityError


def test_db_session_lifecycle(app):
    # Ensure the app is in the correct context
    with app.app_context():
        session1 = db_session
        session2 = db_session

        # Assert that sessions within the same context are the same
        assert session1 is session2

        # Perform an operation to confirm session functionality
        stmt = select(User)
        result = session1.execute(stmt) 
        assert result is not None
        # Close the session
        session1.remove()
        
        # sqlalchemy sessions will re-open when called. By default, session.close()
        # is closer to session.reset(). The following assert does not apply.
        # with pytest.raises(Exception) as e:
        #     session1.execute(stmt) 
        # assert "closed" in str(e.value).lower()

def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False
    def fake_init_db(*args, **kwargs): # the @click decorator adds hidden args which need to be captured
        Recorder.called = True

    # Replace the true init_db command with the fake defined above
    monkeypatch.setattr('flaskr.db_alchemy.init_db', fake_init_db)
    # Runner mimics clicking on the button (triggers @click)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output # From @click
    assert Recorder.called # From patched fake_init_db

def test_unique_username_constraint(test_session):
    """
    Ensure that adding a duplicate username raises an IntegrityError.
    Mostly a sanity check on a different bug
    """
    user1 = User(name='tester_common_name', password='password1')
    user2 = User(name='tester_common_name', password='password2')

    test_session.add(user1)
    test_session.commit()

    with pytest.raises(IntegrityError):
        test_session.add(user2)
        test_session.commit()