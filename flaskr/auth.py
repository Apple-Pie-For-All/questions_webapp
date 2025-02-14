import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db_alchemy import db_session
from flaskr.data_model import User
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    '''
    Handles registering users, both displaying the form via GET and entering
    the new user via POST.
    '''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                new_user = User(name=username, password=generate_password_hash(password))
                db_session.add(new_user)
                db_session.commit()
            except IntegrityError:
                error = f'User {username} is already registered.'
                db_session.rollback()
            else:
                return redirect(url_for("auth.login"))
        
        flash(error)
    
    # If POST didn't go anywhere or is GET, render the page
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    '''
    Handles logging in known users. Displays the log in page with GET and
    checks the credentials with POST
    '''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        error = None

        # Load user first
        stmt = select(User).where(User.name == username)
        user = db_session.scalars(stmt).first()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id # Session will persist data in cookie
            return redirect(url_for('index'))

        flash(error)

    # If POST didn't go anywhere or is GET, render the page
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    '''
    Fetches user details from db before loading a request
    '''
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        stmt = select(User).where(User.id == user_id)
        g.user = db_session.scalars(stmt).first() # g is good only for the request? Ok not to strip password? TODO double check.

@bp.route('/logout')
def logout():
    '''
    Place to tie loose ends before logging a user out
    '''
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    '''
    Decorator to ensure logged in user. If not, redirects to log in page
    '''
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view