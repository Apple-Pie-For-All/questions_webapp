from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from .db_alchemy import db_session
from .data_model import User, Post
from sqlalchemy import select
from sqlalchemy.orm import joinedload

bp = Blueprint("debug", __name__)

@bp.route('/debug')
def debug():
    """
    Here to display background info on the live site. Should obviously be deleted before hitting prod
    """
    stmt = select(User).order_by(User.name.asc())
    user_list = db_session.scalars(stmt).all()

    return render_template('debug/debug.html', users=user_list)