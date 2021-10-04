import re

from pydantic import BaseModel, validator, EmailStr


class Password(BaseModel):
    """ Password """

    password: str
    confirm_password: str

    @validator('password')
    def validate_password(cls, password):
        """ Validate password """

        reg = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$'
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


class VerificationCreate(BaseModel):
    """ Verification create """

    user_id: int
    link: str


class ActivateUser(BaseModel):
    """ User activate """

    is_active: bool = True
