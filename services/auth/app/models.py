import datetime
import typing

import sqlalchemy
from pyotp import random_base32
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


class GitHub(Base):
    """ GitHub """

    __tablename__ = 'github'

    id: int = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    git_id: int = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, unique=True)
    git_username: str = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)

    user_id: int = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, unique=True,
    )

    def __str__(self):
        return f'<GitHub {self.git_username}>'

    def __repr__(self):
        return f'<GitHub {self.git_username}>'


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
    otp: bool = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)
    otp_secret: str = sqlalchemy.Column(sqlalchemy.String, nullable=False, default=random_base32)
    date_joined: datetime.datetime = sqlalchemy.Column(
        sqlalchemy.DateTime, default=datetime.datetime.utcnow, nullable=False
    )
    last_login: datetime.datetime = sqlalchemy.Column(
        sqlalchemy.DateTime, default=datetime.datetime.utcnow, nullable=False
    )

    verification: typing.Union[relationship, Verification] = relationship(
        Verification, backref='user', lazy='selectin', cascade='all, delete', uselist=False,
    )
    github: typing.Union[relationship, GitHub] = relationship(
        GitHub, backref='user', lazy='selectin', cascade='all, delete', uselist=False,
    )

    def __str__(self):
        return f'<User {self.username}>'

    def __repr__(self):
        return f'<User {self.username}>'
