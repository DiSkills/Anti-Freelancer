import typing

from pydantic import validator, BaseModel

from app.schemas import Paginate
from config import SERVER_BACKEND


class UserGetAdmin(BaseModel):
    """ Users get for admin """

    id: int
    username: str
    avatar: typing.Optional[str]
    freelancer: bool
    is_superuser: bool

    @validator('avatar')
    def set_avatar(cls, avatar):
        return SERVER_BACKEND + avatar if avatar else 'https://via.placeholder.com/400x400'


class UsersPaginate(Paginate):
    """ Users paginate """

    results: list[UserGetAdmin]
