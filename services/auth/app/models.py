import datetime
import typing

import sqlalchemy
from sqlalchemy.orm import relationship

from db import Base


class Verification(Base):
    """ Verification """

    __tablename__ = 'verification'

    id: int = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    link: str = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    user_id: int = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )

    def __str__(self):
        return f'<Verification {self.id}>'

    def __repr__(self):
        return f'<Verification {self.id}>'


class User(Base):
    """ User """

    __tablename__ = 'user'

    id: int = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    username: str = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    email: str = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    password: str = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    is_superuser: bool = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)
    is_active: bool = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)
    about: typing.Optional[str] = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    freelancer: bool = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    avatar: typing.Optional[str] = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    date_joined: datetime.datetime = sqlalchemy.Column(
        sqlalchemy.DateTime, default=datetime.datetime.utcnow, nullable=False
    )
    last_login: datetime.datetime = sqlalchemy.Column(
        sqlalchemy.DateTime, default=datetime.datetime.utcnow, nullable=False
    )

    verification: typing.Union[relationship, Verification] = relationship(
        Verification, backref='user', lazy='selectin', cascade='all, delete', uselist=False,
    )

    def __str__(self):
        return f'<User {self.username}>'

    def __repr__(self):
        return f'<User {self.username}>'
