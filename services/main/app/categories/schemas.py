import typing

from pydantic import BaseModel


class CreateCategory(BaseModel):
    """ Create category """

    name: str
    super_category_id: typing.Optional[int] = None


class GetCategory(CreateCategory):
    """ Get category """

    id: int


class GetSuperCategory(GetCategory):
    """ Get super category """

    sub_categories: list[GetCategory]
