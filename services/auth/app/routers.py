from fastapi import APIRouter, Depends, status, Form, UploadFile, File, Request
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app import views
from app.models import User
from app.schemas import (
    Register,
    Message,
    Tokens,
    AccessToken,
    PermissionResponse,
    UserChangeData,
    UserPublic,
    ChangePassword,
    Password,
)
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
async def register(schema: Register, db: AsyncSession = Depends(get_db)):
    return await views.register(db, schema)


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


@auth_router.post(
    '/is-authenticated',
    name='Authenticated user',
    description='Authenticated user',
    response_description='User ID',
    status_code=status.HTTP_200_OK,
    response_model=PermissionResponse,
    tags=['permission'],
)
async def is_authenticated(user_id: int = Depends(views.is_authenticated)):
    return {'user_id': user_id}


@auth_router.post(
    '/is-active',
    name='Is activated user',
    description='Is activated user',
    response_description='User ID',
    status_code=status.HTTP_200_OK,
    response_model=PermissionResponse,
    tags=['permission'],
)
async def is_active(user: User = Depends(views.is_active)):
    return {'user_id': user.id}


@auth_router.post(
    '/is-superuser',
    name='Is superuser user',
    description='Is superuser user',
    response_description='User ID',
    status_code=status.HTTP_200_OK,
    response_model=PermissionResponse,
    tags=['permission'],
)
async def is_superuser(user: User = Depends(views.is_superuser)):
    return {'user_id': user.id}


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
        file: UploadFile = File(...), user: User = Depends(views.is_active), db: AsyncSession = Depends(get_db)
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
async def get_data(user: User = Depends(views.is_active)):
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
        schema: UserChangeData, user: User = Depends(views.is_active), db: AsyncSession = Depends(get_db)
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
        schema: ChangePassword, user: User = Depends(views.is_active), db: AsyncSession = Depends(get_db)
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
async def github_unbind(user: User = Depends(views.is_active), db: AsyncSession = Depends(get_db)):
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
async def otp_on(user: User = Depends(views.is_active), db: AsyncSession = Depends(get_db)):
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
async def otp_off(user: User = Depends(views.is_active), db: AsyncSession = Depends(get_db)):
    return await views.otp_off(db, user)
