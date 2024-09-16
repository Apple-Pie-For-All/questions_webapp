from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
import click

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db(engine):
    # import all modules here that might define models so that
    # they will be registered properly in the metadata.
    from . import data_model
    Base.metadata.create_all(bind=engine)

@click.command('init-db')
def init_db_command():
    '''
    Define cmdline arg to init database per ORM model. Might be obsolete.
    '''
    init_db(db_session.bind)
    click.echo('Initialized the database with SQLalchemy.')

def init_app(app):
    # Setup
    engine = create_engine(app.config['SQLALCHEMY_URI'])
    db_session.configure(bind=engine)

    # app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)