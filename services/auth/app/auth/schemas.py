import datetime
import re
import typing

from pydantic import BaseModel, validator, EmailStr

from app.schemas import Paginate
from app.skills.schemas import GetSkill
from config import SERVER_BACKEND


class Password(BaseModel):
    """ Password """

    password: str
    confirm_password: str

    @validator('password')
    def validate_password(cls, password):
        """ Validate password """

        reg = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$'
        if not re.search(reg, password):
            raise ValueError('Password invalid')
        return password

    @validator('confirm_password')
    def validate_confirm_password(cls, confirm_password, values, **kwargs):
        """ Validate confirm password """

        if 'password' in values and confirm_password != values['password']:
            raise ValueError('Passwords do not match')
        return confirm_password


class Register(Password):
    """ Register """

    username: str
    email: EmailStr
    freelancer: bool = False


class VerificationCreate(BaseModel):
    """ Verification create """

    user_id: int
    link: str


class AccessToken(BaseModel):
    """ Access token """

    access_token: str
    type: str


class RefreshToken(BaseModel):
    """ Refresh token """

    refresh_token: str
    type: str


class Tokens(AccessToken, RefreshToken):
    """ Tokens """

    pass


class UserChangeData(BaseModel):
    """ User change data """

    username: str
    email: EmailStr
    about: typing.Optional[str]


class ChangePassword(Password):
    """ Change password """

    old_password: str

    @validator('old_password')
    def validate_confirm_password(cls, old_password, values, **kwargs):
        """ Old password and new password mismatch """

        if 'password' in values and old_password == values['password']:
            raise ValueError('Old password and new password match')
        return old_password


class GetFreelancer(BaseModel):
    """ Get freelancer """

    id: int
    username: str
    avatar: typing.Optional[str]
    level: typing.Optional[int]

    @validator('level')
    def set_level(cls, level):
        return level / 100 if level is not None else None

    @validator('avatar')
    def set_avatar(cls, avatar):
        return SERVER_BACKEND + avatar if avatar else 'https://via.placeholder.com/400x400'


class UserPublic(UserChangeData, GetFreelancer):
    """ User data """

    date_joined: datetime.datetime
    last_login: datetime.datetime
    freelancer: bool


class UserSkills(BaseModel):
    """ User skills """

    skills: list[GetSkill]
    other: list[GetSkill]


class Profile(GetFreelancer):
    """ Profile """

    about: typing.Optional[str]
    date_joined: datetime.datetime
    last_login: datetime.datetime
    freelancer: bool
    skills: list[GetSkill]
    github: typing.Optional[str]


class PaginateFreelancers(Paginate):
    """ Paginate freelancers """

    results: list[GetFreelancer]
