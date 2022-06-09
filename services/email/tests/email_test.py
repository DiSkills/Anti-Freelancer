from unittest import TestCase, mock

from app.crud import client_crud
from tests import BaseTest, async_loop


class EmailTestCase(BaseTest, TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.data = {
            'recipient': 'test@example.com',
            'subject': 'Register account',
            'template': 'register.html',
            'data': {
                'username': 'test',
            },
        }
        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.post(
                f'{self.url}/clients/?client_name=auth',
                headers={'Authorization': 'Bearer Token'}
            )
        self.data['client_name'] = 'auth'
        self.data['secret'] = response.json()['secret']

    def test_email_send(self):
        self.assertEqual(len(async_loop(client_crud.all(self.session))), 1)
        response = self.client.post(f'{self.url}/send', json=self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'msg': 'Email has been send'})

    def test_template_not_found(self):
        self.data['template'] = 'test.html'
        response = self.client.post(f'{self.url}/send', json=self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Template not found'})

    def test_client_not_found(self):
        self.data['client_name'] = 'test'
        response = self.client.post(f'{self.url}/send', json=self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Client not found'})

    def test_bad_client_secret(self):
        self.data['secret'] = 'test'
        response = self.client.post(f'{self.url}/send', json=self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Bad client secret'})

    def test_bad_email(self):
        self.data['recipient'] = 'test'
        response = self.client.post(f'{self.url}/send', json=self.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()['detail'][0]['msg'], 'value is not a valid email address')
