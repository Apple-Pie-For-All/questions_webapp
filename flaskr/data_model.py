from typing import List, Optional
import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, func, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flaskr.db_alchemy import Base

class User(Base):
    '''
    Define a User table for the ORM with name and password. 
    id:         uuid assigned by orm
    name:       user name, must be unique
    password:   hashed SHA256, cannot be null

    posts:      orm back-populated list of posts
    '''
    __tablename__ = 'user'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)

    posts = relationship('Post', back_populates='author')

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name})"
    
class Post(Base):
    '''
    Define a Post table for the ORM with author_id, created(datetime), title, and body.
    id:         uuid assigned by orm
    author_id:  user id of author
    created:    datetime, defaults to now()
    title:      title string, cannot be null
    body:       body string, cannot be null

    author:     orm back-populated author user object
    comments:   orm back-populated list of comments associated with posts
    '''
    __tablename__ = 'post'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    created: Mapped[datetime] = mapped_column(insert_default=func.now())
    title: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(String, nullable=False)

    author = relationship('User', back_populates='posts')
    comments: Mapped[List["Comment"]] = relationship()

    def __repr__(self) -> str:
        return f"Post(id={self.id}, author_id={self.author_id}, created={self.created})"
    
class Comment(Base):
    '''
    Define a Comment for the ORM with parent Post, test, author, and date
    id:             uuid assigned by orm
    parent_post_id: post id of parent post
    author_id:      user id of author
    created:        datetime, defaults to now()
    body:           the comment itself, string, cannot be null

    author:         orm back-populated user from author
    '''

    __tablename__ = 'comment'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    parent_post_id: Mapped[int] = mapped_column(ForeignKey('post.id'))
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    created: Mapped[datetime] = mapped_column(insert_default=func.now())
    body: Mapped[str] = mapped_column(String, nullable=False)

    author: Mapped[User] = relationship()
