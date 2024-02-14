import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = current_app.alchemy_engine.connect()
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    
    # Other code that needs to execute on start up.
    # Mostly here as legacy for load sql schema in sqlite3

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialed the database with SQLalchemy.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)