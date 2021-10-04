import datetime
import typing

import sqlalchemy

from db import Base


class User(Base):
    """ User """

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

    def __str__(self):
        return f'<User {self.username}>'

    def __repr__(self):
        return f'<User {self.username}>'
