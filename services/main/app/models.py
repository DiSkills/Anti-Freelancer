import datetime
import typing

import sqlalchemy
from sqlalchemy.orm import relationship

from db import Base


class SubCategory(Base):
    """ Sub category """

    __tablename__ = 'subcategory'

    id: int = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name: str = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    super_category_id: int = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('supercategory.id', ondelete='CASCADE'), nullable=False,
    )

    def __str__(self):
        return f'<SubCategory {self.name}>'

    def __repr__(self):
        return f'<SubCategory {self.name}>'


class SuperCategory(Base):
    """ Super category """

    __tablename__ = 'supercategory'

    id: int = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name: str = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    sub_categories: typing.Union[relationship, list[SubCategory]] = relationship(
        SubCategory, backref='super_category', order_by='SubCategory.name', lazy='selectin', cascade='all, delete',
    )

    def __str__(self):
        return f'<SuperCategory {self.name}>'

    def __repr__(self):
        return f'<SuperCategory {self.name}>'


class Attachment(Base):
    """ Attachment """

    __tablename__ = 'attachment'

    id: int = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    path: str = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    job_id: int = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('job.id', ondelete='CASCADE'), nullable=False,
    )


class Job(Base):
    """ Job """

    __tablename__ = 'job'

    id: int = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title: str = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description: str = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    price: int = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=False)
    order_date: datetime.datetime = sqlalchemy.Column(
        sqlalchemy.DateTime, default=datetime.datetime.utcnow, nullable=False,
    )
    customer_id: int = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    completed: bool = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)
    executor_id: typing.Optional[int] = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    category_id: int = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('subcategory.id', ondelete='CASCADE'), nullable=False,
    )

    attachments: typing.Union[relationship, list[Attachment]] = relationship(
        Attachment, backref='jobs', lazy='selectin', cascade='all, delete',
    )
