from unittest import TestCase

from app.crud import user_crud, verification_crud
from tests import BaseTest, async_loop


class AdminTestCase(BaseTest, TestCase):

    def test_admin_users_all(self):
        self.client.post(self.url + '/register', json=self.user_data)
        verification = async_loop(verification_crud.get(self.session, id=1))
        self.client.get(self.url + f'/verify?link={verification.link}')
        async_loop(user_crud.update(self.session, {'id': 1}, is_superuser=True))
        async_loop(self.session.commit())

        tokens = self.client.post(f'{self.url}/login', data={'username': 'test', 'password': 'Test1234!'})
        headers = {'Authorization': f'Bearer {tokens.json()["access_token"]}'}

        self.client.post(self.url + '/register', json={**self.user_data, 'username': 'test2', 'email': 'test2@example.com'})
        self.client.post(self.url + '/register', json={**self.user_data, 'username': 'test3', 'email': 'test3@example.com'})

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
