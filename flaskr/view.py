from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from .db_alchemy import db_session
from .data_model import User, Post
from sqlalchemy import select
from sqlalchemy.orm import joinedload

bp = Blueprint("view", __name__)

@bp.route('/<int:id>/view')
def view(id):
    """
    Show a specified post in detail
    """
    stmt = select(Post).where(Post.id == id)
    post_for_page = db_session.scalars(stmt).first()

    return render_template('view/view.html', post=post_for_page)
