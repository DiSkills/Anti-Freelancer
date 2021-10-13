import typing

import sqlalchemy
from sqlalchemy.orm import relationship

from db import Base


class SubCategory(Base):

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
