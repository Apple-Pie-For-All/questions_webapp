from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import uuid
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from .db_alchemy import db_session
from .data_model import User, Post
from sqlalchemy import select
from sqlalchemy.orm import joinedload

bp = Blueprint("blog", __name__)

@bp.route('/')
def index():
    '''
    Homepage to display posts
    '''

    # Use select() with joinedload to eagerly load the related User objects,
    # reducing queries downstream
    stmt = select(Post).options(joinedload(Post.author)).order_by(Post.created.desc())
    post_list = db_session.scalars(stmt).all()

    return render_template('blog/index.html', posts=post_list)

@bp.route('/create', methods=("GET", "POST"))
@login_required
def create():
    '''
    Allows logged in users to create new posts
    '''
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = "Title is required."
        if error is not None:
            flash(error)
        else:
            new_post = Post(title=title, body=body, author_id=g.user.id)
            db_session.add(new_post)
            db_session.commit()

            return redirect(url_for('blog.index'))
        
    return render_template('blog/create.html')

def get_post(id, check_author=True):
    '''
    Fetches a post from the db by id. Returns 404 if not found. 
    Defaults to verifying that the requester is also the creator. Returns 403
    if the requester is not the creator.
    '''

    stmt = select(Post).where(Post.id == uuid.UUID(id))
    post = db_session.scalars(stmt).first()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post.author_id != g.user.id:
        abort(403)

    return post

@bp.route('/<string:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    '''
    Updates a post for a user
    '''
    post = get_post(id)

    # 
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            # Modify the existing Post object
            post.title = title
            post.body = body

            # Commit the session to persist changes
            db_session.commit()

            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<string:id>/delete', methods=('POST',))
@login_required
def delete(id):
    '''
    Deletes designated post when author requests. 
    Returns 403 if user is not author.
    '''
    post = get_post(id) # get post was implementing the 403 check

    # This never got called when implemented, even with tests looking
    # for the 403 when called. @login_required must cover this (according to coverage.py)
    # if post.author_id != g.user.id:
    #     abort(403)

    # Delete the post from the database
    db_session.delete(post)
    db_session.commit()
    return redirect(url_for('blog.index'))