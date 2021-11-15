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

        # Pay
        with mock.patch('app.requests.pay_request', return_value=f'{SERVER_BACKEND}') as _:
            response = self.client.get(f'{self.url}/pay?amount=1', headers=headers)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json(), {'url': SERVER_BACKEND, 'id': 1})
            self.assertEqual(len(async_loop(payment_crud.all(self.session))), 1)

        self.assertEqual(async_loop(payment_crud.exist(self.session, id=1)), True)

        with mock.patch('app.requests.pay_request', return_value=f'{SERVER_BACKEND}') as _:
            response = self.client.get(f'{self.url}/pay?amount=1', headers=headers)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json(), {'url': SERVER_BACKEND, 'id': 2})
            self.assertEqual(len(async_loop(payment_crud.all(self.session))), 1)

            self.assertEqual(async_loop(payment_crud.exist(self.session, id=1)), False)
            self.assertEqual(async_loop(payment_crud.exist(self.session, id=2)), True)

        # Check
        with mock.patch('app.requests.check_request', return_value={'status': {'value': 'WAITING'}}) as _:
            response = self.client.get(f'{self.url}/check?pk=2')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Payment not paid'})
            self.assertEqual(async_loop(payment_crud.get(self.session, id=2)).is_completed, False)
            self.assertEqual(async_loop(user_crud.get(self.session, id=1)).level, 0)

        with mock.patch('app.requests.check_request', return_value={'status': {'value': 'PAID'}}) as _:
            self.assertEqual(async_loop(payment_crud.get(self.session, id=2)).is_completed, False)
            self.assertEqual(async_loop(user_crud.get(self.session, id=1)).level, 0)

            response = self.client.get(f'{self.url}/check?pk=2')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Level has been up'})

            self.assertEqual(async_loop(user_crud.get(self.session, id=1)).level, 1)
            self.assertEqual(async_loop(payment_crud.get(self.session, id=2)).is_completed, True)

            response = self.client.get(f'{self.url}/check?pk=2')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'The purchase has already been credited'})

            response = self.client.get(f'{self.url}/check?pk=143')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Payment not found'})

        with mock.patch('app.requests.pay_request', return_value=f'{SERVER_BACKEND}') as _:
            response = self.client.get(f'{self.url}/pay?amount=500', headers=headers)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json(), {'url': SERVER_BACKEND, 'id': 3})
            self.assertEqual(len(async_loop(payment_crud.all(self.session))), 2)

        with mock.patch('app.requests.check_request', return_value={'status': {'value': 'PAID'}}) as _:
            self.assertEqual(async_loop(payment_crud.get(self.session, id=3)).is_completed, False)
            self.assertEqual(async_loop(user_crud.get(self.session, id=1)).level, 1)

            response = self.client.get(f'{self.url}/check?pk=3')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Level has been up'})

            self.assertEqual(async_loop(user_crud.get(self.session, id=1)).level, 501)
            self.assertEqual(async_loop(payment_crud.get(self.session, id=3)).is_completed, True)
