import asyncio
import datetime
import os
import shutil
from unittest import TestCase

import jwt
from fastapi import UploadFile
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import user_crud, verification_crud
from app.tokens import ALGORITHM
from config import SECRET_KEY, MEDIA_ROOT, API
from db import engine, Base
from main import app


async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def async_loop(function):
    loop = asyncio.get_event_loop()
    try:
        return loop.run_until_complete(function)
    finally:
        pass


class AuthTestCase(TestCase):

    def setUp(self) -> None:
        self.session = AsyncSession(engine)
        self.client = TestClient(app)
        self.data = {
            'password': 'Test1234!',
            'confirm_password': 'Test1234!',
            'username': 'test',
            'email': 'test@example.com',
            'freelancer': False,
        }
        self.url = f'/{API}'
        async_loop(create_all())
        os.makedirs(MEDIA_ROOT)

    def tearDown(self) -> None:
        async_loop(self.session.close())
        async_loop(drop_all())
        shutil.rmtree(MEDIA_ROOT)

    def test_register(self):
        self.assertEqual(len(async_loop(user_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(verification_crud.all(self.session))), 0)

        # Invalid passwords
        response = self.client.post(f'{self.url}/register', json={**self.data, 'password': 'test'})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()['detail'][0]['msg'], 'Password invalid')
        self.assertEqual(len(async_loop(user_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(verification_crud.all(self.session))), 0)

        response = self.client.post(f'{self.url}/register', json={**self.data, 'password': 'test241fg'})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()['detail'][0]['msg'], 'Password invalid')
        self.assertEqual(len(async_loop(user_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(verification_crud.all(self.session))), 0)

        response = self.client.post(f'{self.url}/register', json={**self.data, 'password': 'test241fg!'})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()['detail'][0]['msg'], 'Password invalid')
        self.assertEqual(len(async_loop(user_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(verification_crud.all(self.session))), 0)

        response = self.client.post(f'{self.url}/register', json={**self.data, 'confirm_password': 'test241fg!'})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()['detail'][0]['msg'], 'Passwords do not match')
        self.assertEqual(len(async_loop(user_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(verification_crud.all(self.session))), 0)

        # Register
        response = self.client.post(f'{self.url}/register', json=self.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'msg': 'Send email for activate your account'})
        self.assertEqual(len(async_loop(user_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(verification_crud.all(self.session))), 1)

        response = self.client.post(f'{self.url}/register', json=self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Username exist'})
        self.assertEqual(len(async_loop(user_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(verification_crud.all(self.session))), 1)

        response = self.client.post(f'{self.url}/register', json={**self.data, 'username': 'test2'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Email exist'})
        self.assertEqual(len(async_loop(user_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(verification_crud.all(self.session))), 1)

        self.assertEqual(async_loop(verification_crud.get(self.session, id=1)).user_id, 1)
        self.assertEqual(async_loop(user_crud.get(self.session, id=1)).freelancer, False)

    def test_verification(self):
        self.client.post(f'{self.url}/register', json={**self.data, 'freelancer': True})
        self.assertEqual(async_loop(user_crud.get(self.session, id=1)).freelancer, True)
        self.assertEqual(len(async_loop(verification_crud.all(self.session))), 1)
        self.assertEqual(async_loop(user_crud.get(self.session, id=1)).is_active, False)

        verification = async_loop(verification_crud.get(self.session, id=1))
        response = self.client.get(f'{self.url}/verify?link={verification.link}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'msg': 'Your account has been activated'})

        self.assertEqual(len(async_loop(verification_crud.all(self.session))), 0)
        self.assertEqual(async_loop(user_crud.get(self.session, id=1)).is_active, True)

        response = self.client.get(f'{self.url}/verify?link={verification.link}')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Verification not exist'})

    def test_login(self):
        self.client.post(f'{self.url}/register', json=self.data)

        response = self.client.post(f'{self.url}/login', data={'username': 'test', 'password': 'Test1234!'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'detail': 'You not activated'})

        verification = async_loop(verification_crud.get(self.session, id=1))
        self.client.get(f'{self.url}/verify?link={verification.link}')

        response = self.client.post(f'{self.url}/login', data={'username': 'test', 'password': 'Test1234!'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'bearer')
        self.assertEqual('access_token' in response.json(), True)
        self.assertEqual('refresh_token' in response.json(), True)

        access = jwt.decode(response.json()['access_token'], SECRET_KEY, algorithms=[ALGORITHM])
        self.assertEqual(access['user_id'], 1)
        self.assertEqual(access['sub'], 'access')

        refresh = jwt.decode(response.json()['refresh_token'], SECRET_KEY, algorithms=[ALGORITHM])
        self.assertEqual(refresh['user_id'], 1)
        self.assertEqual(refresh['sub'], 'refresh')

        response = self.client.post(f'{self.url}/login', data={'username': 'test2', 'password': 'Test1234!'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Username not found'})

        response = self.client.post(f'{self.url}/login', data={'username': 'test', 'password': 'Test1234!!'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Password mismatch'})

        response = self.client.post(f'{self.url}/login', data={'username': 'test', 'password': 't'})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()['detail'][0]['msg'], 'ensure this value has at least 8 characters')

        response = self.client.post(f'{self.url}/login', data={'username': 'test', 'password': 't' * 25})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()['detail'][0]['msg'], 'ensure this value has at most 20 characters')

    def test_refresh(self):
        self.client.post(f'{self.url}/register', json=self.data)
        verification = async_loop(verification_crud.get(self.session, id=1))
        self.client.get(f'{self.url}/verify?link={verification.link}')

        tokens = self.client.post(f'{self.url}/login', data={'username': 'test', 'password': 'Test1234!'}).json()

        response = self.client.post(f'{self.url}/refresh?token={tokens["refresh_token"]}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'bearer')
        self.assertEqual('access_token' in response.json(), True)
        access = jwt.decode(response.json()['access_token'], SECRET_KEY, algorithms=[ALGORITHM])
        self.assertEqual(access['user_id'], 1)
        self.assertEqual(access['sub'], 'access')

        response = self.client.post(f'{self.url}/refresh?token={tokens["access_token"]}')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Refresh token not found'})

        refresh = jwt.encode(
            {'user_id': 2, 'sub': 'refresh', 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=3)},
            SECRET_KEY,
            ALGORITHM,
        )
        response = self.client.post(f'{self.url}/refresh?token={refresh}')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'User not found'})

        refresh = jwt.encode(
            {'user_id': 1, 'sub': 'refresh', 'exp': datetime.datetime.utcnow() - datetime.timedelta(minutes=1)},
            SECRET_KEY,
            ALGORITHM,
        )
        response = self.client.post(f'{self.url}/refresh?token={refresh}')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Token lifetime ended'})

        response = self.client.post(f'{self.url}/refresh?token={refresh + "gf"}')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'detail': 'Could not validate credentials'})

    def test_permission_urls(self):
        self.client.post(f'{self.url}/register', json=self.data)

        last_login_register = async_loop(user_crud.get(self.session, id=1)).last_login

        verification = async_loop(verification_crud.get(self.session, id=1))
        self.client.get(f'{self.url}/verify?link={verification.link}')

        tokens = self.client.post(f'{self.url}/login', data={'username': 'test', 'password': 'Test1234!'}).json()

        last_login_login = async_loop(user_crud.get(self.session, id=1)).last_login
        self.assertNotEqual(last_login_login, last_login_register)

        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}

        # Is authenticated
        response = self.client.post(f'{self.url}/is-authenticated', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'user_id': 1})

        last_login_is_auth = async_loop(user_crud.get(self.session, id=1)).last_login
        self.assertNotEqual(last_login_is_auth, last_login_login)

        response = self.client.post(
            f'{self.url}/is-authenticated', headers={'Authorization': f'Bearer {tokens["refresh_token"]}'}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Access token not found'})

        response = self.client.post(f'{self.url}/is-authenticated')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Not authenticated'})

        # Is active
        async_loop(user_crud.update(self.session, {'id': 1}, is_active=False))
        response = self.client.post(f'{self.url}/is-active', headers=headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'detail': 'User not activated'})

        async_loop(user_crud.update(self.session, {'id': 1}, is_active=True))
        response = self.client.post(f'{self.url}/is-active', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'user_id': 1})

        last_login_is_active = async_loop(user_crud.get(self.session, id=1)).last_login
        self.assertNotEqual(last_login_is_active, last_login_is_auth)

        response = self.client.post(
            f'{self.url}/is-active', headers={'Authorization': f'Bearer {tokens["refresh_token"]}'}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Access token not found'})

        response = self.client.post(f'{self.url}/is-active')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Not authenticated'})

        # Is superuser
        response = self.client.post(f'{self.url}/is-superuser', headers=headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'detail': 'User not superuser'})

        async_loop(user_crud.update(self.session, {'id': 1}, is_superuser=True))
        response = self.client.post(f'{self.url}/is-superuser', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'user_id': 1})

        last_login_is_superuser = async_loop(user_crud.get(self.session, id=1)).last_login
        self.assertNotEqual(last_login_is_superuser, last_login_is_active)

        response = self.client.post(
            f'{self.url}/is-superuser', headers={'Authorization': f'Bearer {tokens["refresh_token"]}'}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Access token not found'})

        response = self.client.post(f'{self.url}/is-superuser')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Not authenticated'})

    def test_avatar(self):
        self.client.post(f'{self.url}/register', json=self.data)
        verification = async_loop(verification_crud.get(self.session, id=1))
        self.client.get(f'{self.url}/verify?link={verification.link}')

        tokens = self.client.post(f'{self.url}/login', data={'username': 'test', 'password': 'Test1234!'}).json()
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}

        user = async_loop(user_crud.get(self.session, id=1))

        self.assertEqual(user.avatar, None)

        file = UploadFile('image.png', content_type='image/png')
        response = self.client.post(
            f'{self.url}/avatar', headers=headers, files={'file': ('image.png', async_loop(file.read()), 'image/png')}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'msg': 'Avatar has been saved'})
        async_loop(self.session.commit())

        user = async_loop(user_crud.get(self.session, id=1))
        avatar = user.avatar
        self.assertEqual(os.path.exists(avatar), True)

        file = UploadFile('image.png', content_type='image/png')
        response = self.client.post(
            f'{self.url}/avatar', headers=headers, files={'file': ('image.png', async_loop(file.read()), 'image/png')}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'msg': 'Avatar has been saved'})
        async_loop(self.session.commit())

        user = async_loop(user_crud.get(self.session, id=1))
        self.assertEqual(os.path.exists(avatar), False)
        self.assertEqual(os.path.exists(user.avatar), True)

        self.assertNotEqual(avatar, user.avatar)

        # Errors
        file = UploadFile('image.gif', content_type='image/gif')
        response = self.client.post(
            f'{self.url}/avatar', headers=headers, files={'file': ('image.gif', async_loop(file.read()), 'image/gif')}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Avatar only in png format'})

        async_loop(self.session.commit())
        user = async_loop(user_crud.get(self.session, id=1))
        self.assertEqual(os.path.exists(user.avatar), True)

        # Media
        avatar = user.avatar.replace('media/tests/', '')
        response = self.client.get(f'/media/{avatar}')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/media/test2/image.png')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'detail': 'File not found'})
