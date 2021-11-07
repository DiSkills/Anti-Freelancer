import datetime
import typing

from pydantic import validator, BaseModel, EmailStr

from app.auth.schemas import Register
from app.schemas import Paginate
from config import SERVER_BACKEND


class UserMinimal(BaseModel):
    """ User minimum """

    id: int
    username: str
    avatar: typing.Optional[str]
    freelancer: bool
    is_superuser: bool
    level: typing.Optional[int]

    @validator('level')
    def set_level(cls, level):
        return level / 100 if level is not None else None

    @validator('avatar')
    def set_avatar(cls, avatar):
        return SERVER_BACKEND + avatar if avatar else 'https://via.placeholder.com/400x400'


class GitHub(BaseModel):
    """ GitHub """

    git_id: int
    id: int
    git_username: str


class UserMaximal(UserMinimal):
    """ User maximum """

    email: EmailStr
    about: typing.Optional[str]
    github: typing.Optional[GitHub]
    is_active: bool
    last_login: datetime.datetime
    date_joined: datetime.datetime
    referral_link: str


class UsersPaginate(Paginate):
    """ Users paginate """

    results: list[UserMinimal]


class RegisterAdmin(Register):
    """ Register user for admin  """

    is_superuser: bool = True
    is_active: bool = True


class UpdateUser(BaseModel):
    """ Update user """

    email: EmailStr
    about: typing.Optional[str]
    freelancer: bool
    is_superuser: bool = False
    level: typing.Optional[int] = None

    @validator('level')
    def set_level(cls, level):
        if (level is not None) and (level <= 0):
            raise ValueError('Level cannot be less than or equal to 0')
        return level
