import os
import tempfile

from werkzeug.security import check_password_hash, generate_password_hash

import pytest
from flaskr import create_app
from sqlalchemy import event, select
from sqlalchemy.orm import sessionmaker
from flaskr.data_model import User, Post
from flaskr.db_alchemy import Base, db_session, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    '''
    Prep app for testing
    '''
    db_fd, db_path = tempfile.mkstemp() # setup test db

    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_URI': 'sqlite:///:memory:',  # In-memory SQLite for tests
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'DATABASE': db_path,
    })

    # Create tables for tests
    with app.app_context():
        # Base.metadata.create_all(bind=db_session.bind)
        # init_db(app)
        Base.metadata.create_all(bind=db_session.bind)


    yield app

    # Drop all tables after tests
    with app.app_context():
        Base.metadata.drop_all(bind=db_session.bind)

@pytest.fixture
def test_session(app):
    """
    Returns an active SQLAlchemy session for testing. 
    Ensures a clean connection.
    """
    # Create a new session for each test
    connection = db_session.bind.connect()
    transaction = connection.begin()

    # Use sessionmaker to bind the session to the connection
    Session = sessionmaker(bind=connection)
    session = Session()

    fill_db(session)

    yield session

    # Rollback after each test
    transaction.rollback()
    connection.close()

    # Clean up the session
    session.close()

def fill_db(session):
    '''
    Creates dummy data to test app with
    '''
    user1 = User(name='tester', password=generate_password_hash('test_password'))
    user2 = User(name='other_tester', password=generate_password_hash('other_password'))
    session.add(user1)
    session.add(user2)
    session.commit()

    # Need to get primary key from the database (SQLalchemy lets the db handle this)
    stmt = select(User).where(User.name=='tester')
    committed_user1 = session.scalars(stmt).first()
    post1 = Post(author_id=committed_user1.id, title='Test Post', body='A full body of text to test')
    session.add(post1)
    session.commit()

@pytest.fixture
def client(app):
    return app.test_client()

# Mimics clicking on buttons
@pytest.fixture
def runner(app):
    return app.test_cli_runner()

# Automatically logs in for testing auth protected features
class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='tester', password='test_password'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')
    
@pytest.fixture
def auth(client):
    return AuthActions(client)