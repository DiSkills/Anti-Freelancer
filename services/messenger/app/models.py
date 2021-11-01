import datetime
import typing

import sqlalchemy
from sqlalchemy.orm import relationship

from db import Base


class Message(Base):
    """ Message """

    __tablename__ = 'message'

    id: int = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    sender_id: int = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    msg: str = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_at: datetime.datetime = sqlalchemy.Column(
        sqlalchemy.DateTime, default=datetime.datetime.utcnow, nullable=False,
    )
    viewed: bool = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)

    dialog_id: int = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('dialog.id', ondelete='CASCADE'), nullable=False,
    )

    def __str__(self):
        return f'<Message {self.id}>'

    def __repr__(self):
        return f'<Message {self.id}>'


class Dialog(Base):
    """ Dialog """

    __tablename__ = 'dialog'

    id: int = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    users_ids: str = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    messages: typing.Union[relationship, list[Message]] = relationship(
        Message, backref='dialog', cascade='all, delete',
    )

    def __str__(self):
        return f'<Dialog {self.id}>'

    def __repr__(self):
        return f'<Dialog {self.id}>'
