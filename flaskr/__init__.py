import os

from flask import Flask
from sqlalchemy import create_engine

def create_app(test_config=None):
    '''
    Factory which generates the web app
    '''
    app = Flask(__name__, instance_relative_config=True)

    # Configure settings for local development. Should pull from config file in prod
    app.config.from_mapping(
        SECRET_KEY = 'DEV',
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
        SQLALCHEMY_URI = 'sqlite:///' + os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello World!'
    
    # Register functions and elements from other files. 
    from . import db_alchemy
    db_alchemy.init_app(app)

    from . import db_seed
    db_seed.init_seed_command(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    from . import debug
    app.register_blueprint(debug.bp)
    app.add_url_rule('/debug', endpoint='debug')

    from . import post
    app.register_blueprint(post.bp)

    from flaskr.db_alchemy import db_session
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app