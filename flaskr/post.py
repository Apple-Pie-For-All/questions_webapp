from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import uuid
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from .db_alchemy import db_session
from .data_model import User, Post, Comment
from sqlalchemy import select
from sqlalchemy.orm import joinedload

bp = Blueprint("post", __name__)

@bp.route('/<string:id>')
def view(id):
    """
    Show a specified post in detail
    """
    stmt = select(Post).where(Post.id == uuid.UUID(id))
    post_for_page = db_session.scalars(stmt).first()

    return render_template('post/post.html', post=post_for_page)

@bp.route('/<string:post_id>/comment', methods=("POST",))
@login_required
def add_comment(post_id):
    """
    Add a comment to a post
    """
    comment_body = request.form['text']
    if comment_body == '':
        flash("Comment text is required")
    else:
        new_comment = Comment(parent_post_id=uuid.UUID(post_id), author_id=g.user.id, body=comment_body)
        db_session.add(new_comment)
        db_session.commit()

    return redirect(url_for("post.view", id=post_id))

@bp.route('/edit-comment/<string:id>', methods=("POST",))
@login_required
def edit_comment(id):
    """
    Edit a pre-existing comment
    """
    stmt = select(Comment).where(Comment.id == uuid.UUID(id))
    revised_comment = db_session.scalars(stmt).first()

    if revised_comment == None:
        abort(403) # Should this be 404?

    if revised_comment.author_id != g.user.id:
        abort(403)

    revised_comment.body = request.form['text']
    db_session.commit
    
