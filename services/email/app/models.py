import sqlalchemy

from db import Base


class Client(Base):
    """ Client """

    __tablename__ = 'client'

    id: int = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    secret: str = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    client_name: str = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)

    def __str__(self):
        return f'<Client {self.id}>'

    def __repr__(self):
        return f'<Client {self.id}>'
