import datetime
import typing

import sqlalchemy
from sqlalchemy.orm import relationship

from config import SEND
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
    is_deleted: bool = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)

    dialogue_id: int = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('dialogue.id', ondelete='CASCADE'), nullable=False,
    )
    notification = relationship('Notification', back_populates='message', uselist=False, cascade='all, delete')

    def __str__(self):
        return f'<Message {self.id}>'

    def __repr__(self):
        return f'<Message {self.id}>'


class Dialogue(Base):
    """ Dialogue """

    __tablename__ = 'dialogue'

    id: int = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    users_ids: str = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)

    messages: typing.Union[relationship, list[Message]] = relationship(
        Message, backref='dialogue', cascade='all, delete',
    )

    def __str__(self):
        return f'<Dialogue {self.id}>'

    def __repr__(self):
        return f'<Dialogue {self.id}>'

    def get_recipient_id(self, sender_id: int) -> int:
        """
            Get recipient ID
            :param sender_id: Sender ID
            :type sender_id: int
            :return: Recipient ID
            :rtype: int
        """
        users = self.users_ids.split('_')
        del users[users.index(f'{sender_id}')]
        return int(users[0])


class Notification(Base):
    """ Notification """

    __tablename__ = 'notification'

    id: int = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    type: str = sqlalchemy.Column(sqlalchemy.String, nullable=False, default=SEND)
    sender_id: int = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    recipient_id: int = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    message_id: int = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('message.id', ondelete='CASCADE'), nullable=False,
    )

    message = relationship('Message', back_populates='notification', uselist=False, lazy='selectin')

    def __str__(self):
        return f'<Notification {self.id}>'

    def __repr__(self):
        return f'<Notification {self.id}>'
