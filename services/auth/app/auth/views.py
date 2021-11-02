import io
import os
import typing
from datetime import datetime
from uuid import uuid4

import qrcode
from fastapi import HTTPException, status, UploadFile, Request
from fastapi.responses import RedirectResponse, StreamingResponse
from pyotp import TOTP
from qrcode.image.pil import PilImage
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import Register, UserChangeData, ChangePassword, Password, VerificationCreate
from app.crud import user_crud, verification_crud, github_crud, skill_crud, user_skill_crud
from app.models import User
from app.security import get_password_hash, verify_password_hash
from app.send_email import send_register_email, send_reset_password_email, send_username_email
from app.service import validate_login, remove_file, write_file, github_data, paginate
from app.tokens import create_login_tokens, verify_token, create_access_token, create_reset_password_token
from config import SERVER_BACKEND, API, MEDIA_ROOT, social_auth, redirect_url, PROJECT_NAME


async def register(db: AsyncSession, schema: Register) -> dict[str, str]:
    """
        Register
        :param db: DB
        :type db: AsyncSession
        :param schema: Register data
        :type schema: Register
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Username or email exist
    """

    if await user_crud.exist(db, username=schema.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username exist')

    if await user_crud.exist(db, email=schema.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email exist')

    del schema.confirm_password
    user = await user_crud.create(db, **{**schema.dict(), 'password': get_password_hash(schema.password)})

    verification = await verification_crud.create(db, **VerificationCreate(user_id=user.id, link=str(uuid4())).dict())

    await send_register_email(user.id, user.email, user.username, f'{SERVER_BACKEND}{API}/verify?link={verification.link}')

    return {'msg': 'Send email for activate your account'}


async def verify(db: AsyncSession, link: str) -> dict[str, str]:
    """
        Verification account
        :param db: DB
        :type db: AsyncSession
        :param link: Link
        :type link: str
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Verification not found
    """

    if not await verification_crud.exist(db, link=link):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification not exist')

    verification = await verification_crud.get(db, link=link)
    await user_crud.update(db, {'id': verification.user_id}, is_active=True)
    await verification_crud.remove(db, id=verification.id)
    return {'msg': 'Your account has been activated'}


async def login(db: AsyncSession, username: str, password: str) -> dict[str, str]:
    """
        Login user
        :param db: DB
        :type db: AsyncSession
        :param username: Username
        :type username: str
        :param password: Password
        :type password: str
        :return: Tokens
        :rtype: dict
        :raise HTTPException 403: User have 2-step auth
    """
    user = await validate_login(db, username, password)

    if user.otp:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have 2-step auth')

    return create_login_tokens(user.id)


async def get_username(db: AsyncSession, email: str) -> dict[str, str]:
    """
        Get username
        :param db: DB
        :type db: AsyncSession
        :param email: Email
        :type email: str
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Email not found
    """

    if not await user_crud.exist(db, email=email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User not found')

    user = await user_crud.get(db, email=email)
    await send_username_email(user.id, user.email, user.username)

    return {'msg': 'Email send'}


async def refresh(db: AsyncSession, token: str) -> dict[str, str]:
    """
        Refresh
        :param db: DB
        :type db: AsyncSession
        :param token: Refresh token
        :type token: str
        :return: Access token and token type
        :rtype: dict
    """

    user_id = await verify_token(db, token, 'refresh', 'Refresh token not found')

    return create_access_token(user_id)


@paginate(user_crud.freelancers, user_crud.freelancers_exist, f'{SERVER_BACKEND}{API}/freelancers')
async def get_freelancers(*, db: AsyncSession, page: int, page_size: int, queryset: list[User]):
    """
        Get freelancers
        :param db: DB
        :type db: AsyncSession
        :param page: Page
        :type page: int
        :param page_size: Page size
        :type page_size: int
        :param queryset: Freelancers
        :type queryset: list
        :return: Freelancers
    """
    return (user.__dict__ for user in queryset)


@paginate(user_crud.search, user_crud.search_exist, f'{SERVER_BACKEND}{API}/freelancers/search', 'search')
async def search_freelancers(*, db: AsyncSession, page: int, page_size: int, search: str, queryset: list[User]):
    """
        Search freelancers
        :param db: DB
        :type db: AsyncSession
        :param page: Page
        :type page: int
        :param page_size: Page size
        :type page_size: int
        :param search: Search
        :type search: str
        :param queryset: Freelancers
        :type queryset: list
        :return: Freelancers
    """
    return (user.__dict__ for user in queryset)


async def profile(db: AsyncSession, user_id: int) -> dict[str, typing.Any]:
    """
        Profile
        :param db: DB
        :type db: AsyncSession
        :param user_id: User ID
        :type user_id: int
        :return: Profile data
        :rtype: dict
        :raise HTTPException 400: User not found
    """

    if not await user_crud.exist(db, id=user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User not found')
    user = await user_crud.get(db, id=user_id)
    return {
        **user.__dict__,
        'skills': [skill.__dict__ for skill in user.skills],
        'github': user.github.git_username if user.github else None,
    }


async def avatar(db: AsyncSession, user: User, file: UploadFile) -> dict[str, str]:
    """
        Avatar
        :param db: DB
        :type db: AsyncSession
        :param user: User
        :type user: User
        :param file: File
        :type file: UploadFile
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Avatar only in png format
    """

    if file.content_type != 'image/png':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Avatar only in png format')

    if (user.avatar is not None) and (MEDIA_ROOT in user.avatar):
        remove_file(user.avatar)

    if not os.path.exists(MEDIA_ROOT + user.username):
        os.mkdir(MEDIA_ROOT + user.username)

    avatar_name = f'{MEDIA_ROOT}{user.username}/{datetime.utcnow().timestamp()}.png'

    await write_file(avatar_name, file)
    await user_crud.update(db, {'id': user.id}, avatar=avatar_name)
    return {'msg': 'Avatar has been saved'}


async def change_data(db: AsyncSession, schema: UserChangeData, user: User) -> dict:
    """
        Change data
        :param db: DB
        :type db: AsyncSession
        :param schema: Changed data
        :type schema: UserChangeData
        :param user: User
        :type user: User
        :return: User data
        :rtype: dict
        :raise HTTPException 400: Email or username exist
    """

    if user.username != schema.username:
        if await user_crud.exist(db, username=schema.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username exist')
    else:
        del schema.username

    if user.email != schema.email:
        if await user_crud.exist(db, email=schema.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email exist')
    else:
        del schema.email

    user = await user_crud.update(db, {'id': user.id}, **schema.dict())
    return user.__dict__


async def change_password(db: AsyncSession, user: User, schema: ChangePassword) -> dict[str, str]:
    """
        Change password
        :param db: DB
        :type db: AsyncSession
        :param user: User
        :type user: User
        :param schema: New passwords and old password
        :type schema: ChangePassword
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Old password mismatch
    """

    if not verify_password_hash(schema.old_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Old password mismatch')

    await user_crud.update(db, {'id': user.id}, password=get_password_hash(schema.password))
    return {'msg': 'Password has been changed'}


async def reset_password_request(db: AsyncSession, email: str) -> dict[str, str]:
    """
        Reset password request
        :param db: DB
        :type db: AsyncSession
        :param email: Email
        :type email: str
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Email not found
    """

    if not await user_crud.exist(db, email=email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email not found')

    user = await user_crud.get(db, email=email)
    token = create_reset_password_token(user.id)
    link = SERVER_BACKEND + f'{API}/reset-password?token={token}'
    await send_reset_password_email(user.id, user.email, user.username, link)
    return {'msg': 'Send reset password email. Check your email address'}


async def reset_password(db: AsyncSession, schema: Password, token: str) -> dict[str, str]:
    """
        Reset password
        :param db: DB
        :type db: AsyncSession
        :param schema: New password
        :type schema: Password
        :param token: Reset token
        :type token: str
        :return: Message
        :rtype: dict
        :raise HTTPException 400: User not found
        :raise HTTPException 400: The new password cannot be the same as the old one
    """

    user_id = await verify_token(db, token, 'reset', 'Reset token not found')

    if not await user_crud.exist(db, id=user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User not found')

    user = await user_crud.get(db, id=user_id)

    if verify_password_hash(schema.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='The new password cannot be the same as the old one',
        )

    await user_crud.update(db, {'id': user_id}, password=get_password_hash(schema.password), otp=False)
    return {'msg': 'Password has been reset'}


async def github_request(db: AsyncSession, request: Request, user_id: int) -> RedirectResponse:
    """
        GitHub request
        :param db: DB
        :type db: AsyncSession
        :param request: Request
        :type request: Request
        :param user_id: User ID
        :type user_id: int
        :return: Redirect
        :rtype: RedirectResponse
        :raise HTTPException 400: User not found
        :raise HTTPException 403: User is customer
    """

    if not await user_crud.exist(db, id=user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User not found')

    if not await user_crud.exist(db, id=user_id, freelancer=True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User is customer')

    github = social_auth.create_client('github')
    return await github.authorize_redirect(request, redirect_url + f'?user_id={user_id}')


async def github_bind(db: AsyncSession, request: Request, user_id: int) -> dict[str, str]:
    """
        GitHub
        :param db: DB
        :type db: AsyncSession
        :param request: Request
        :type request: Request
        :param user_id: User ID
        :type user_id: int
        :return: Message
        :rtype: dict
        :raise HTTPException 400: User not found
        :raise HTTPException 400: GitHub account exist
        :raise HTTPException 403: User is customer
    """

    if not await user_crud.exist(db, id=user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User not found')

    if not await user_crud.exist(db, id=user_id, freelancer=True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User is customer')

    github_profile = await github_data(request)

    git_id = github_profile['id']

    if (not await github_crud.exist(db, git_id=git_id)) and (not await github_crud.exist(db, user_id=user_id)):
        await github_crud.create(db, git_id=git_id, git_username=github_profile['login'], user_id=user_id)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='GitHub account exist')

    return {'msg': 'GitHub account has been bind'}


async def github_unbind(db: AsyncSession, user: User) -> dict[str, str]:
    """
        GitHub unbind
        :param db: DB
        :type db: AsyncSession
        :param user: User
        :type user: User
        :return: Message
        :rtype: dict
        :raise HTTPException 400: GitHub not exist
    """

    if not await github_crud.exist(db, user_id=user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='GitHub not exist')

    await github_crud.remove(db, user_id=user.id)
    return {'msg': 'GitHub account has been deleted'}


async def otp_on(db: AsyncSession, user: User) -> StreamingResponse:
    """
        2-step auth on
        :param db: DB
        :type db: AsyncSession
        :param user: User
        :type user: User
        :return: QRCode
        :rtype: StreamingResponse
        :raise HTTPException 400: User already have 2-step auth
    """

    if user.otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already have 2-step auth')
    img: PilImage = qrcode.make(TOTP(user.otp_secret).provisioning_uri(user.username, PROJECT_NAME))
    byte_io = io.BytesIO()
    img.save(byte_io, format='PNG')

    await user_crud.update(db, {'id': user.id}, otp=True)

    return StreamingResponse(
        io.BytesIO(byte_io.getvalue()), media_type='image/png', status_code=status.HTTP_206_PARTIAL_CONTENT,
    )


async def otp_off(db: AsyncSession, user: User) -> dict[str, str]:
    """
        2-step auth off
        :param db: DB
        :type db: AsyncSession
        :param user: User
        :type user: User
        :return: Message
        :rtype: dict
        :raise HTTPException 400: User already haven't 2-step auth
    """

    if not user.otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already haven\'t 2-step auth')

    await user_crud.update(db, {'id': user.id}, otp=False)
    return {'msg': '2-step auth off'}


async def otp_login(db: AsyncSession, username: str, password: str, code: str) -> dict[str, str]:
    """
        OTP login
        :param db: DB
        :type db: AsyncSession
        :param username: Username
        :type username: str
        :param password: Password
        :type password: str
        :param code: Code
        :type code: str
        :return: Tokens
        :rtype: dict
        :raise HTTPException 403: User don't have 2-step auth
        :raise HTTPException 403: Bad code
    """

    user = await validate_login(db, username, password)

    if not user.otp:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You don\'t have 2-step auth')

    totp = TOTP(user.otp_secret)

    if not totp.verify(code):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Bad code')

    return create_login_tokens(user.id)


async def add_skill(db: AsyncSession, user: User, skill_id: int) -> dict[str, str]:
    """
        Add skill
        :param db: DB
        :type db: AsyncSession
        :param user: User
        :type user: User
        :param skill_id: Skill ID
        :type skill_id: int
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Skill not found
        :raise HTTPException 400: User already have this skill
    """

    if not await skill_crud.exist(db, id=skill_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Skill not found')

    if await user_skill_crud.exist(db, user_id=user.id, skill_id=skill_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You already have this skill')

    await user_skill_crud.create(db, user_id=user.id, skill_id=skill_id)
    return {'msg': 'Skill has been added'}


async def remove_skill(db: AsyncSession, user: User, skill_id: int) -> dict[str, str]:
    """
        Remove skill
        :param db: DB
        :type db: AsyncSession
        :param user: User
        :type user: User
        :param skill_id: Skill ID
        :type skill_id: int
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Skill not found
        :raise HTTPException 400: User already haven't this skill
    """

    if not await skill_crud.exist(db, id=skill_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Skill not found')

    if not await user_skill_crud.exist(db, user_id=user.id, skill_id=skill_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You already haven\'t this skill')

    await user_skill_crud.remove(db, user_id=user.id, skill_id=skill_id)
    return {'msg': 'Skill has been deleted'}


async def user_skills(db: AsyncSession, user: User) -> dict[str, typing.Any]:
    """
        User skills
        :param db: DB
        :type db: AsyncSession
        :param user: User
        :type user: User
        :return: Skills user
        :rtype: dict
    """

    user = await user_crud.get(db, id=user.id)
    return {
        'skills': (skill.__dict__ for skill in user.skills),
        'other': (
            skill.__dict__ for skill in filter(
                lambda skill: skill not in user.skills, await skill_crud.all(db, limit=1000),
            )
        ),
    }
