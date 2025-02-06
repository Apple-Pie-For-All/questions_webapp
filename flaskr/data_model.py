from typing import List, Optional
from datetime import datetime
from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flaskr.db_alchemy import Base

class User(Base):
    '''
    Define a User table for the ORM with name and password. 
    Password should be a SHA256 hash
    '''
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str]

    posts = relationship('Post', back_populates='author')

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name})"
    
class Post(Base):
    '''
    Define a Post table for the ORM with author_id, created(datetime), title, and body.
    '''
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(primary_key=True)
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
    Define a Comment for the ORM with parrent Post, test, author, and date
    '''

    __tablename__ = 'comment'

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_post_id: Mapped[int] = mapped_column(ForeignKey('post.id'))
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    created: Mapped[datetime] = mapped_column(insert_default=func.now())
    text: Mapped[str] = mapped_column(String, nullable=False)

    author: Mapped[User] = relationship()
