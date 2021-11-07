from unittest import TestCase, mock

from fastapi import UploadFile

from app.crud import user_crud, verification_crud, github_crud
from config import SERVER_BACKEND
from tests import BaseTest, async_loop


class AdminTestCase(BaseTest, TestCase):

    def test_unbind_github(self):
        self.client.post(self.url + '/register', json={**self.user_data, 'freelancer': True})
        verification = async_loop(verification_crud.get(self.session, id=1))
        self.client.get(self.url + f'/verify?link={verification.link}')
        async_loop(user_crud.update(self.session, {'id': 1}, is_superuser=True))
        async_loop(self.session.commit())

        tokens = self.client.post(f'{self.url}/login', data={'username': 'test', 'password': 'Test1234!'})
        headers = {'Authorization': f'Bearer {tokens.json()["access_token"]}'}

        with mock.patch('app.auth.views.github_data', return_value={'id': 25, 'login': 'Counter021'}) as _:
            response = self.client.get(f'{self.url}/github/bind?user_id=1')
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json(), {'msg': 'GitHub account has been bind'})

        self.assertEqual(len(async_loop(github_crud.all(self.session))), 1)

        response = self.client.delete(f'{self.url}/admin/github/unbind/1', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'msg': 'GitHub account has been deleted'})

        self.assertEqual(len(async_loop(github_crud.all(self.session))), 0)

        response = self.client.delete(f'{self.url}/admin/github/unbind/143', headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'GitHub account not found'})

    def test_create_user(self):
        self.client.post(self.url + '/register', json={**self.user_data, 'freelancer': True})
        verification = async_loop(verification_crud.get(self.session, id=1))
        self.client.get(self.url + f'/verify?link={verification.link}')
        async_loop(user_crud.update(self.session, {'id': 1}, is_superuser=True))
        async_loop(self.session.commit())

        tokens = self.client.post(f'{self.url}/login', data={'username': 'test', 'password': 'Test1234!'})
        headers = {'Authorization': f'Bearer {tokens.json()["access_token"]}'}

        self.assertEqual(len(async_loop(user_crud.all(self.session))), 1)

        user_data = {
            'password': 'Test1234!',
            'confirm_password': 'Test1234!',
            'username': 'test2',
            'email': 'test2@example.com',
            'freelancer': False,
            'is_superuser': True,
            'is_active': True,
        }
        user_data_2 = {
            'password': 'Test1234!',
            'confirm_password': 'Test1234!',
            'username': 'test3',
            'email': 'test3@example.com',
            'freelancer': True,
            'is_superuser': True,
            'is_active': True,
        }
        response = self.client.post(f'{self.url}/admin/user', json=user_data, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'msg': 'User has been created'})
        self.assertEqual(len(async_loop(user_crud.all(self.session))), 2)

        self.assertEqual(async_loop(user_crud.get(self.session, id=2)).is_superuser, True)
        self.assertEqual(async_loop(user_crud.get(self.session, id=2)).is_active, True)

        response = self.client.post(f'{self.url}/admin/user', json=user_data_2, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'msg': 'User has been created'})
        self.assertEqual(len(async_loop(user_crud.all(self.session))), 3)

        response = self.client.get(f'{self.url}/admin/user/2', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {
                'id': 2,
                'github': None,
                'username': 'test2',
                'email': 'test2@example.com',
                'about': None,
                'avatar': 'https://via.placeholder.com/400x400',
                'freelancer': False,
                'is_superuser': True,
                'is_active': True,
                'level': None,
                'date_joined': response.json()['date_joined'],
                'last_login': response.json()['last_login'],
            }
        )

        response = self.client.get(f'{self.url}/admin/user/3', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {
                'id': 3,
                'github': None,
                'username': 'test3',
                'email': 'test3@example.com',
                'about': None,
                'avatar': 'https://via.placeholder.com/400x400',
                'freelancer': True,
                'is_superuser': True,
                'is_active': True,
                'level': 0.0,
                'date_joined': response.json()['date_joined'],
                'last_login': response.json()['last_login'],
            }
        )

    def test_get_user(self):
        self.client.post(self.url + '/register', json={**self.user_data, 'freelancer': True})
        verification = async_loop(verification_crud.get(self.session, id=1))
        self.client.get(self.url + f'/verify?link={verification.link}')
        async_loop(user_crud.update(self.session, {'id': 1}, is_superuser=True))
        async_loop(self.session.commit())

        tokens = self.client.post(f'{self.url}/login', data={'username': 'test', 'password': 'Test1234!'})
        headers = {'Authorization': f'Bearer {tokens.json()["access_token"]}'}

        self.client.post(
            self.url + '/register', json={**self.user_data, 'username': 'test2', 'email': 'test2@example.com'}
        )

        with mock.patch('app.auth.views.github_data', return_value={'id': 25, 'login': 'Counter021'}) as _:
            response = self.client.get(f'{self.url}/github/bind?user_id=1')
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json(), {'msg': 'GitHub account has been bind'})

        self.client.put(
            self.url + '/change-data', headers=headers, json={
                'username': 'test',
                'email': 'test@example.com',
                'about': 'Hello world!',
            }
        )

        file = UploadFile('image.png', content_type='image/png')
        response = self.client.post(
            f'{self.url}/avatar', headers=headers, files={'file': ('image.png', async_loop(file.read()), 'image/png')}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'msg': 'Avatar has been saved'})
        async_loop(self.session.commit())

        response = self.client.get(f'{self.url}/admin/user/1', headers=headers)
        self.assertEqual(response.status_code, 200)
        user_1 = {
            'about': 'Hello world!',
            'avatar': f'{SERVER_BACKEND}{async_loop(user_crud.get(self.session, id=1)).avatar}',
            'date_joined': response.json()['date_joined'],
            'email': 'test@example.com',
            'freelancer': True,
            'github': {
                'git_username': 'Counter021',
                'git_id': 25,
                'id': 1,
            },
            'id': 1,
            'is_active': True,
            'is_superuser': True,
            'last_login': response.json()['last_login'],
            'username': 'test',
            'level': 0.0,
        }
        self.assertEqual(response.json(), user_1)

        response = self.client.get(f'{self.url}/admin/user/2', headers=headers)
        self.assertEqual(response.status_code, 200)
        user_2 = {
            'about': None,
            'avatar': 'https://via.placeholder.com/400x400',
            'date_joined': response.json()['date_joined'],
            'email': 'test2@example.com',
            'freelancer': False,
            'github': None,
            'id': 2,
            'is_active': False,
            'is_superuser': False,
            'last_login': response.json()['last_login'],
            'username': 'test2',
            'level': None,
        }
        self.assertEqual(response.json(), user_2)

        response = self.client.get(f'{self.url}/admin/user/3', headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'User not found'})

    def test_get_all_users(self):
        self.client.post(self.url + '/register', json=self.user_data)
        verification = async_loop(verification_crud.get(self.session, id=1))
        self.client.get(self.url + f'/verify?link={verification.link}')
        async_loop(user_crud.update(self.session, {'id': 1}, is_superuser=True))
        async_loop(self.session.commit())

        tokens = self.client.post(f'{self.url}/login', data={'username': 'test', 'password': 'Test1234!'})
        headers = {'Authorization': f'Bearer {tokens.json()["access_token"]}'}

        self.client.post(
            self.url + '/register', json={**self.user_data, 'username': 'test2', 'email': 'test2@example.com'}
        )
        self.client.post(
            self.url + '/register', json={**self.user_data, 'username': 'test3', 'email': 'test3@example.com'}
        )

        response = self.client.get(f'{self.url}/admin/users?page=1&page_size=2', headers=headers)
        self.assertEqual(response.status_code, 200)
        page_1 = {
            'next': f'{SERVER_BACKEND}{self.url[1:]}/admin/users?page=2&page_size=2',
            'previous': None,
            'page': 1,
            'results': [
                {
                    'id': 3,
                    'username': 'test3',
                    'avatar': 'https://via.placeholder.com/400x400',
                    'freelancer': False,
                    'is_superuser': False,
                    'level': None,
                },
                {
                    'id': 2,
                    'username': 'test2',
                    'avatar': 'https://via.placeholder.com/400x400',
                    'freelancer': False,
                    'is_superuser': False,
                    'level': None,
                },
            ]
        }
        self.assertEqual(response.json(), page_1)

        response = self.client.get(f'{self.url}/admin/users?page=2&page_size=2', headers=headers)
        self.assertEqual(response.status_code, 200)
        page_2 = {
            'next': None,
            'previous': f'{SERVER_BACKEND}{self.url[1:]}/admin/users?page=1&page_size=2',
            'page': 2,
            'results': [
                {
                    'id': 1,
                    'username': 'test',
                    'avatar': 'https://via.placeholder.com/400x400',
                    'freelancer': False,
                    'is_superuser': True,
                    'level': None,
                },
            ]
        }
        self.assertEqual(response.json(), page_2)

        response = self.client.get(f'{self.url}/admin/users?page=4&page_size=2', headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Results not found'})

    def test_update_user(self):
        self.client.post(self.url + '/register', json={**self.user_data, 'freelancer': True})
        verification = async_loop(verification_crud.get(self.session, id=1))
        self.client.get(self.url + f'/verify?link={verification.link}')
        async_loop(user_crud.update(self.session, {'id': 1}, is_superuser=True))
        async_loop(self.session.commit())

        tokens = self.client.post(f'{self.url}/login', data={'username': 'test', 'password': 'Test1234!'})
        headers = {'Authorization': f'Bearer {tokens.json()["access_token"]}'}

        user_data = {
            'password': 'Test1234!',
            'confirm_password': 'Test1234!',
            'username': 'test2',
            'email': 'test2@example.com',
            'freelancer': False,
            'is_superuser': True,
            'is_active': True,
        }

        self.client.post(f'{self.url}/admin/user', json=user_data, headers=headers)
        response = self.client.get(f'{self.url}/admin/user/2', headers=headers)
        response_data = {
            'id': 2,
            'github': None,
            'username': 'test2',
            'email': 'test2@example.com',
            'about': None,
            'avatar': 'https://via.placeholder.com/400x400',
            'freelancer': False,
            'is_superuser': True,
            'is_active': True,
            'date_joined': response.json()['date_joined'],
            'last_login': response.json()['last_login'],
            'level': None,
        }
        self.assertEqual(response.json(), response_data)

        # Update
        response = self.client.put(
            f'{self.url}/admin/user/2', headers=headers, json={
                'email': 'test2@example.com',
                'about': 'Hello world!',
                'freelancer': True,
                'is_superuser': False,
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.json(), response_data)
        response = self.client.get(f'{self.url}/admin/user/2', headers=headers)
        self.assertEqual(response.json()['email'], 'test2@example.com')
        self.assertEqual(response.json()['about'], 'Hello world!')
        self.assertEqual(response.json()['freelancer'], True)
        self.assertEqual(response.json()['is_superuser'], False)

        response = self.client.put(
            f'{self.url}/admin/user/2', headers=headers, json={
                'email': 'test3@example.com',
                'about': 'Hello world!',
                'freelancer': True,
                'is_superuser': False,
            }
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f'{self.url}/admin/user/2', headers=headers)
        self.assertEqual(response.json()['email'], 'test3@example.com')
        self.assertEqual(response.json()['about'], 'Hello world!')
        self.assertEqual(response.json()['freelancer'], True)
        self.assertEqual(response.json()['is_superuser'], False)
        self.assertEqual(response.json()['level'], 0.0)

        response = self.client.put(
            f'{self.url}/admin/user/2', headers=headers, json={
                'email': 'test@example.com',
                'about': 'Hello world!',
                'freelancer': True,
                'is_superuser': False,
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Email exist'})

        response = self.client.put(
            f'{self.url}/admin/user/143', headers=headers, json={
                'email': 'test@example.com',
                'about': 'Hello world!',
                'freelancer': True,
                'is_superuser': False,
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'User not found'})

        response = self.client.put(
            f'{self.url}/admin/user/2', headers=headers, json={
                'email': 'test3@example.com',
                'about': 'Hello world!',
                'freelancer': False,
                'is_superuser': False,
            }
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f'{self.url}/admin/user/2', headers=headers)
        self.assertEqual(response.json()['email'], 'test3@example.com')
        self.assertEqual(response.json()['about'], 'Hello world!')
        self.assertEqual(response.json()['freelancer'], False)
        self.assertEqual(response.json()['is_superuser'], False)
        self.assertEqual(response.json()['level'], None)

        response = self.client.put(
            f'{self.url}/admin/user/2', headers=headers, json={
                'email': 'test3@example.com',
                'about': 'Hello world!',
                'freelancer': False,
                'is_superuser': False,
                'level': 200,
            }
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f'{self.url}/admin/user/2', headers=headers)
        self.assertEqual(response.json()['email'], 'test3@example.com')
        self.assertEqual(response.json()['about'], 'Hello world!')
        self.assertEqual(response.json()['freelancer'], False)
        self.assertEqual(response.json()['is_superuser'], False)
        self.assertEqual(response.json()['level'], None)

        response = self.client.put(
            f'{self.url}/admin/user/2', headers=headers, json={
                'email': 'test3@example.com',
                'about': 'Hello world!',
                'freelancer': True,
                'is_superuser': False,
                'level': 200,
            }
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f'{self.url}/admin/user/2', headers=headers)
        self.assertEqual(response.json()['email'], 'test3@example.com')
        self.assertEqual(response.json()['about'], 'Hello world!')
        self.assertEqual(response.json()['freelancer'], True)
        self.assertEqual(response.json()['is_superuser'], False)
        self.assertEqual(response.json()['level'], 2.0)
