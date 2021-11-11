import datetime

import sqlalchemy

from config import NEW
from db import Base


class Feedback(Base):
    """ Feedback """

    __tablename__ = 'feedback'

    id: int = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_id: int = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    text: str = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    status: bool = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=NEW)
    created_at: datetime.datetime = sqlalchemy.Column(
        sqlalchemy.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
    )

    def __str__(self):
        return f'<Feedback {self.id}>'

    def __repr__(self):
        return f'<Feedback {self.id}>'
