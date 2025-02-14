from flaskr.data_model import User, Post, Comment
from flaskr.db_alchemy import Base, init_db, db_session
from sqlalchemy import select
import click
import uuid
from werkzeug.security import generate_password_hash

def seed_db(session):
    '''
    Creates dummy data to test app with. Wipes any pre-existing data
    '''
    Base.metadata.drop_all(bind=session.bind)
    init_db(session.bind)

    user1 = User(name='admin', password=generate_password_hash('password'))
    user2 = User(name='beta_tester', password=generate_password_hash('other_password'))
    session.add(user1)
    session.add(user2)
    session.commit()

    # Need to get primary key from the database (SQLalchemy lets the db handle this)
    stmt = select(User).where(User.name=='admin')
    committed_user1 = session.scalars(stmt).first()
    stmt = select(User).where(User.name=='beta_tester')
    committed_user2 = session.scalars(stmt).first()
    post1 = Post(author_id=committed_user1.id, title='Test Post', body='A full body of text to test')
    post2 = Post(author_id=committed_user2.id, title='Automation is good', body='Hello fellow humans.')
    session.add(post1)
    session.add(post2)
    session.commit()

    stmt = select(Post).where(Post.title == 'Test Post')
    committed_post = session.scalars(stmt).first()
    comment1 = Comment(parent_post_id=committed_post.id, author_id=committed_user1.id, body='Ooo, I do love more content.')
    comment2 = Comment(parent_post_id=committed_post.id, author_id=committed_user2.id, body='Content or riot!')
    session.add(comment1)
    session.add(comment2)
    session.commit()

@click.command('seed-db')
def seed_db_command():
    '''
    Define cmdline arg to init database per ORM model.
    '''
    seed_db(db_session)
    click.echo('Seeded the database with test posts.')

def init_seed_command(app):
    app.cli.add_command(seed_db_command)