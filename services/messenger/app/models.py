import datetime

import sqlalchemy

from db import Base


class Message(Base):
    """ Message """

    __tablename__ = 'message'

    id: int = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    msg: str = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_at: datetime.datetime = sqlalchemy.Column(
        sqlalchemy.DateTime, default=datetime.datetime.utcnow, nullable=False,
    )
    sender_id: int = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    recipient_id: int = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    def __str__(self):
        return f'<Message {self.id}>'

    def __repr__(self):
        return f'<Message {self.id}>'
