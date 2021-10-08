import datetime
import typing

from pydantic import validator, BaseModel, EmailStr

from app.schemas import Paginate
from config import SERVER_BACKEND


class UserMinimal(BaseModel):
    """ User minimum """

    id: int
    username: str
    avatar: typing.Optional[str]
    freelancer: bool
    is_superuser: bool

    @validator('avatar')
    def set_avatar(cls, avatar):
        return SERVER_BACKEND + avatar if avatar else 'https://via.placeholder.com/400x400'


class UserMaximal(UserMinimal):
    """ User maximum """

    email: EmailStr
    about: typing.Optional[str]
    github: typing.Optional[str]
    is_active: bool
    last_login: datetime.datetime
    date_joined: datetime.datetime


class UsersPaginate(Paginate):
    """ Users paginate """

    results: list[UserMinimal]
