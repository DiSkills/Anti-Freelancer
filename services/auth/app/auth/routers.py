import typing

from fastapi import APIRouter, Depends, status, Form, Request, UploadFile, File, Query
from fastapi.responses import StreamingResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import views
from app.auth.schemas import (
    Register,
    Tokens,
    AccessToken,
    UserPublic,
    UserChangeData,
    ChangePassword,
    Password,
    UserSkills,
    Profile,
    PaginateFreelancers,
)
from app.models import User
from app.schemas import Message
from app.views import is_active, is_freelancer
from db import get_db

auth_router = APIRouter()


@auth_router.post(
    '/register',
    name='Register',
    description='Register user',
    response_description='Message',
    status_code=status.HTTP_201_CREATED,
    response_model=Message,
    tags=['auth'],
)
async def register(
    schema: Register,
    link: typing.Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    return await views.register(db, schema, link)


@auth_router.get(
    '/verify',
    name='Verification account',
    description='Verification user account',
    response_description='Message',
    status_code=status.HTTP_200_OK,
    response_model=Message,
    tags=['auth'],
)
async def verify(link: str, db: AsyncSession = Depends(get_db)):
    return await views.verify(db, link)


@auth_router.post(
    '/login',
    name='Login',
    description='Login user',
    response_description='Tokens',
    status_code=status.HTTP_200_OK,
    response_model=Tokens,
    tags=['auth'],
)
async def login(
    username: str = Form(...),
    password: str = Form(..., min_length=8, max_length=20),
    db: AsyncSession = Depends(get_db),
):
    return await views.login(db, username, password)


@auth_router.get(
    '/username',
    name='Get username',
    description='Get username',
    response_description='Message',
    status_code=status.HTTP_200_OK,
    response_model=Message,
    tags=['auth'],
)
async def get_username(email: str, db: AsyncSession = Depends(get_db)):
    return await views.get_username(db, email)


@auth_router.post(
    '/refresh',
    name='Refresh token',
    description='Refresh token',
    response_description='Access token',
    status_code=status.HTTP_200_OK,
    response_model=AccessToken,
    tags=['auth'],
)
async def refresh(token: str, db: AsyncSession = Depends(get_db)):
    return await views.refresh(db, token)


@auth_router.get(
    '/freelancers',
    name='Freelancers',
    description='Freelancers',
    response_description='Freelancers',
    status_code=status.HTTP_200_OK,
    response_model=PaginateFreelancers,
    tags=['auth'],
)
async def get_freelancers(
    page: int = Query(default=1, gt=0),
    page_size: int = Query(default=1, gt=0),
    db: AsyncSession = Depends(get_db),
):
    return await views.get_freelancers(db=db, page=page, page_size=page_size)


@auth_router.get(
    '/freelancers/search',
    name='Search freelancers',
    description='Search freelancers',
    response_description='Freelancers',
    status_code=status.HTTP_200_OK,
    response_model=PaginateFreelancers,
    tags=['auth'],
)
async def search_freelancers(
    search: str,
    page: int = Query(default=1, gt=0),
    page_size: int = Query(default=1, gt=0),
    db: AsyncSession = Depends(get_db),
):
    return await views.search_freelancers(db=db, page=page, page_size=page_size, search=search)


@auth_router.post(
    f'/profile/ids',
    name='Users profiles by ids',
    description='Users profiles by ids',
    response_description='Profiles',
    status_code=status.HTTP_200_OK,
    response_model=dict[str, Profile],
    tags=['auth'],
)
async def profiles_by_ids(ids: list[int], db: AsyncSession = Depends(get_db)):
    return await views.profiles_by_ids(db, ids)


@auth_router.get(
    '/profile/current',
    name='Current user profile',
    description='Current user profile',
    response_description='Profile',
    status_code=status.HTTP_200_OK,
    response_model=Profile,
    tags=['auth'],
)
async def current_profile(user: User = Depends(is_active), db: AsyncSession = Depends(get_db)):
    return await views.profile(db, user.id)


@auth_router.get(
    '/profile/{user_id}',
    name='Profile',
    description='User profile',
    response_description='Profile',
    status_code=status.HTTP_200_OK,
    response_model=Profile,
    tags=['auth'],
)
async def profile(user_id: int, db: AsyncSession = Depends(get_db)):
    return await views.profile(db, user_id)


@auth_router.post(
    '/avatar',
    name='Avatar',
    description='User avatar',
    response_description='Message',
    status_code=status.HTTP_200_OK,
    response_model=Message,
    tags=['change-data'],
)
async def avatar(
    file: UploadFile = File(...), user: User = Depends(is_active), db: AsyncSession = Depends(get_db)
):
    return await views.avatar(db, user, file)


@auth_router.get(
    '/change-data',
    name='Get data',
    description='Get data',
    response_description='User data',
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
    tags=['change-data'],
)
async def get_data(user: User = Depends(is_active)):
    return user.__dict__


@auth_router.put(
    '/change-data',
    name='Change data',
    description='Change data',
    response_description='User data',
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
    tags=['change-data'],
)
async def change_data(
    schema: UserChangeData, user: User = Depends(is_active), db: AsyncSession = Depends(get_db)
):
    return await views.change_data(db, schema, user)


@auth_router.put(
    '/change-password',
    name='Change password',
    description='Change password',
    response_description='Message',
    status_code=status.HTTP_200_OK,
    response_model=Message,
    tags=['change-data'],
)
async def change_password(
    schema: ChangePassword, user: User = Depends(is_active), db: AsyncSession = Depends(get_db)
):
    return await views.change_password(db, user, schema)


@auth_router.post(
    '/reset-password/request',
    name='Reset password request',
    description='Reset password request',
    response_description='Message',
    status_code=status.HTTP_200_OK,
    response_model=Message,
    tags=['reset-password'],
)
async def reset_password_request(email: str, db: AsyncSession = Depends(get_db)):
    return await views.reset_password_request(db, email)


@auth_router.post(
    '/reset-password',
    name='Reset password',
    description='Reset password',
    response_description='Message',
    status_code=status.HTTP_200_OK,
    response_model=Message,
    tags=['reset-password'],
)
async def reset_password(token: str, schema: Password, db: AsyncSession = Depends(get_db)):
    return await views.reset_password(db, schema, token)


@auth_router.get(
    '/github/request',
    name='GitHub Request',
    description='GitHub Request',
    response_description='Redirect',
    status_code=status.HTTP_302_FOUND,
    response_class=RedirectResponse,
    tags=['github'],
)
async def github_request(request: Request, user_id: int, db: AsyncSession = Depends(get_db)):
    return await views.github_request(db, request, user_id)


@auth_router.get(
    '/github/bind',
    name='GitHub bind',
    description='GitHub bind',
    response_description='Message',
    status_code=status.HTTP_201_CREATED,
    response_model=Message,
    tags=['github'],
)
async def github_bind(request: Request, user_id: int, db: AsyncSession = Depends(get_db)):
    return await views.github_bind(db, request, user_id)


@auth_router.post(
    '/github/unbind',
    name='GitHub unbind',
    description='GitHub unbind',
    response_description='Message',
    status_code=status.HTTP_200_OK,
    response_model=Message,
    tags=['github'],
)
async def github_unbind(user: User = Depends(is_freelancer), db: AsyncSession = Depends(get_db)):
    return await views.github_unbind(db, user)


@auth_router.post(
    '/otp/on',
    name='On 2-step auth',
    description='On 2-step auth',
    response_description='QRCode',
    status_code=status.HTTP_206_PARTIAL_CONTENT,
    response_class=StreamingResponse,
    tags=['OTP'],
)
async def otp_on(user: User = Depends(is_active), db: AsyncSession = Depends(get_db)):
    return await views.otp_on(db, user)


@auth_router.post(
    '/otp/off',
    name='Off 2-step auth',
    description='Off 2-step auth',
    response_description='Message',
    status_code=status.HTTP_200_OK,
    response_model=Message,
    tags=['OTP'],
)
async def otp_off(user: User = Depends(is_active), db: AsyncSession = Depends(get_db)):
    return await views.otp_off(db, user)


@auth_router.post(
    '/otp/login',
    name='OTP login',
    description='OTP login',
    response_description='Tokens',
    status_code=status.HTTP_200_OK,
    response_model=Tokens,
    tags=['OTP'],
)
async def otp_login(
    username: str = Form(...),
    password: str = Form(..., min_length=8, max_length=20),
    code: str = Form(..., min_length=6, max_length=6),
    db: AsyncSession = Depends(get_db),
):
    return await views.otp_login(db, username, password, code)


@auth_router.post(
    '/skills/add',
    name='Skill add',
    description='Skill add',
    response_description='Message',
    status_code=status.HTTP_201_CREATED,
    response_model=Message,
    tags=['user-skills'],
)
async def add_skill(skill_id: int, user: User = Depends(is_freelancer), db: AsyncSession = Depends(get_db)):
    return await views.add_skill(db, user, skill_id)


@auth_router.post(
    '/skills/remove',
    name='Skill remove',
    description='Skill remove',
    response_description='Message',
    status_code=status.HTTP_200_OK,
    response_model=Message,
    tags=['user-skills'],
)
async def remove_skill(skill_id: int, user: User = Depends(is_freelancer), db: AsyncSession = Depends(get_db)):
    return await views.remove_skill(db, user, skill_id)


@auth_router.get(
    '/skills/user',
    name='User skills',
    description='User skills',
    response_description='Skills',
    status_code=status.HTTP_200_OK,
    response_model=UserSkills,
    tags=['user-skills'],
)
async def user_skills(user: User = Depends(is_freelancer), db: AsyncSession = Depends(get_db)):
    return await views.user_skills(db, user)
