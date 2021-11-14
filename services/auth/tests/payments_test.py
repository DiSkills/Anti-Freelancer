from unittest import TestCase, mock

from app.crud import verification_crud, user_crud, payment_crud
from config import SERVER_BACKEND
from tests import BaseTest, async_loop


class PaymentsTestCase(BaseTest, TestCase):

    def test_pay(self):
        self.client.post(self.url + '/register', json={**self.user_data, 'freelancer': True})
        verification = async_loop(verification_crud.get(self.session, id=1))
        self.client.get(self.url + f'/verify?link={verification.link}')
        async_loop(user_crud.update(self.session, {'id': 1}, is_superuser=True))
        async_loop(self.session.commit())

        tokens = self.client.post(f'{self.url}/login', data={'username': 'test', 'password': 'Test1234!'})
        headers = {'Authorization': f'Bearer {tokens.json()["access_token"]}'}

        self.assertEqual(len(async_loop(payment_crud.all(self.session))), 0)

        with mock.patch('app.payments.views.pay_request', return_value=f'{SERVER_BACKEND}') as _:
            response = self.client.get(f'{self.url}/pay?amount=1', headers=headers)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json(), {'url': SERVER_BACKEND})
            self.assertEqual(len(async_loop(payment_crud.all(self.session))), 1)

        self.assertEqual(async_loop(payment_crud.exist(self.session, id=1)), True)

        with mock.patch('app.payments.views.pay_request', return_value=f'{SERVER_BACKEND}') as _:
            response = self.client.get(f'{self.url}/pay?amount=1', headers=headers)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json(), {'url': SERVER_BACKEND})
            self.assertEqual(len(async_loop(payment_crud.all(self.session))), 1)

            self.assertEqual(async_loop(payment_crud.exist(self.session, id=1)), False)
            self.assertEqual(async_loop(payment_crud.exist(self.session, id=2)), True)
