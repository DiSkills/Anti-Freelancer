from unittest import TestCase, mock

from fastapi import UploadFile

from app.crud import user_crud, verification_crud
from config import SERVER_BACKEND
from tests import BaseTest, async_loop


class AdminTestCase(BaseTest, TestCase):

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

        self.client.put(self.url + '/change-data', headers=headers, json={
            'username': 'test',
            'email': 'test@example.com',
            'about': 'Hello world!',
        })

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
            'github': 'Counter021',
            'id': 1,
            'is_active': True,
            'is_superuser': True,
            'last_login': response.json()['last_login'],
            'username': 'test'
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
            'username': 'test2'
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
            'next': 'http://localhost:8000/api/v1/admin/users?page=2&page_size=2',
            'previous': None,
            'page': 1,
            'results': [
                {
                    'id': 3,
                    'username': 'test3',
                    'avatar': 'https://via.placeholder.com/400x400',
                    'freelancer': False,
                    'is_superuser': False,
                },
                {
                    'id': 2,
                    'username': 'test2',
                    'avatar': 'https://via.placeholder.com/400x400',
                    'freelancer': False,
                    'is_superuser': False,
                },
            ]
        }
        self.assertEqual(response.json(), page_1)

        response = self.client.get(f'{self.url}/admin/users?page=2&page_size=2', headers=headers)
        self.assertEqual(response.status_code, 200)
        page_2 = {
            'next': None,
            'previous': 'http://localhost:8000/api/v1/admin/users?page=1&page_size=2',
            'page': 2,
            'results': [
                {
                    'id': 1,
                    'username': 'test',
                    'avatar': 'https://via.placeholder.com/400x400',
                    'freelancer': False,
                    'is_superuser': True,
                },
            ]
        }
        self.assertEqual(response.json(), page_2)

        response = self.client.get(f'{self.url}/admin/users?page=4&page_size=2', headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Results not found'})