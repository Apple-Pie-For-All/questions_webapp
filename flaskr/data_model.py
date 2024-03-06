from typing import List, Optional
from datetime import datetime
from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flaskr.db_alchemy import Base

class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    password: Mapped[str]

    posts = relationship('Post', back_populates='author')

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name})"
    
class Post(Base):
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    created: Mapped[datetime] = mapped_column(insert_default=func.now())
    title: Mapped[str]
    body: Mapped[str]

    author = relationship('User', back_populates='posts')

    def __repr__(self) -> str:
        return f"Post(id={self.id}, author_id={self.author_id}, created={self.created})"
    
