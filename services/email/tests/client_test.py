from unittest import TestCase, mock

from fastapi import HTTPException, status

from app.crud import client_crud
from tests import BaseTest, async_loop


class ClientTestCase(BaseTest, TestCase):

    def test_client(self):
        # Create
        self.assertEqual(len(async_loop(client_crud.all(self.session))), 0)

        headers = {'Authorization': 'Bearer Token'}

        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.post(f'{self.url}/clients/?client_name=auth', headers=headers)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(
                response.json(),
                {'id': 1, 'secret': async_loop(client_crud.get(self.session, id=1)).secret, 'client_name': 'auth'}
            )

            self.assertEqual(len(async_loop(client_crud.all(self.session))), 1)

            response = self.client.post(f'{self.url}/clients/?client_name=main', headers=headers)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(
                response.json(),
                {'id': 2, 'secret': async_loop(client_crud.get(self.session, id=2)).secret, 'client_name': 'main'}
            )

            response = self.client.post(f'{self.url}/clients/?client_name=main', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Client exist'})
        self.assertEqual(len(async_loop(client_crud.all(self.session))), 2)
        self.assertNotEqual(
            async_loop(client_crud.get(self.session, id=2)).secret,
            async_loop(client_crud.get(self.session, id=1)).secret
        )

        with mock.patch('app.permission.permission', return_value=1) as user:
            user.side_effect = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User not superuser')
            response = self.client.post(f'{self.url}/clients/?client_name=auth', headers=headers)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json(), {'detail': 'User not superuser'})
        self.assertEqual(len(async_loop(client_crud.all(self.session))), 2)

        # Get
        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.get(f'{self.url}/clients/1', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(),
                {'id': 1, 'secret': async_loop(client_crud.get(self.session, id=1)).secret, 'client_name': 'auth'}
            )

            response = self.client.get(f'{self.url}/clients/143', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Client not found'})

        with mock.patch('app.permission.permission', return_value=1) as user:
            user.side_effect = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User not superuser')
            response = self.client.get(f'{self.url}/clients/1', headers=headers)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json(), {'detail': 'User not superuser'})

        # Get by client name or create
        self.assertEqual(len(async_loop(client_crud.all(self.session))), 2)
        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.post(f'{self.url}/clients/name?client_name=email', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(),
                {'id': 3, 'secret': async_loop(client_crud.get(self.session, id=3)).secret, 'client_name': 'email'}
            )
            self.assertEqual(len(async_loop(client_crud.all(self.session))), 3)

            response = self.client.post(f'{self.url}/clients/name?client_name=auth', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(),
                {'id': 1, 'secret': async_loop(client_crud.get(self.session, id=1)).secret, 'client_name': 'auth'}
            )

        with mock.patch('app.permission.permission', return_value=1) as user:
            user.side_effect = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User not superuser')
            response = self.client.post(f'{self.url}/clients/name?client_name=auth', headers=headers)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json(), {'detail': 'User not superuser'})
        self.assertEqual(len(async_loop(client_crud.all(self.session))), 3)

        async_loop(client_crud.remove(self.session, id=3))
        async_loop(self.session.commit())

        # Get all
        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.get(f'{self.url}/clients/', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(),
                [
                    {'id': 2, 'secret': async_loop(client_crud.get(self.session, id=2)).secret, 'client_name': 'main'},
                    {'id': 1, 'secret': async_loop(client_crud.get(self.session, id=1)).secret, 'client_name': 'auth'}
                ]
            )

        with mock.patch('app.permission.permission', return_value=1) as user:
            user.side_effect = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User not superuser')
            response = self.client.get(f'{self.url}/clients/', headers=headers)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json(), {'detail': 'User not superuser'})

        # Update
        old_secret = async_loop(client_crud.get(self.session, id=1)).secret
        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.put(f'{self.url}/clients/1', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(),
                {'id': 1, 'secret': async_loop(client_crud.get(self.session, id=1)).secret, 'client_name': 'auth'}
            )
            self.assertNotEqual(old_secret, async_loop(client_crud.get(self.session, id=1)).secret)

            response = self.client.put(f'{self.url}/clients/143', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Client not found'})

        with mock.patch('app.permission.permission', return_value=1) as user:
            user.side_effect = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User not superuser')
            response = self.client.put(f'{self.url}/clients/1', headers=headers)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json(), {'detail': 'User not superuser'})
            
        # Delete
        self.assertEqual(len(async_loop(client_crud.all(self.session))), 2)
        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.delete(f'{self.url}/clients/1', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Client has been deleted'})
            self.assertEqual(len(async_loop(client_crud.all(self.session))), 1)

            response = self.client.delete(f'{self.url}/clients/143', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Client not found'})

        with mock.patch('app.permission.permission', return_value=1) as user:
            user.side_effect = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User not superuser')
            response = self.client.delete(f'{self.url}/clients/1', headers=headers)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json(), {'detail': 'User not superuser'})
        self.assertEqual(len(async_loop(client_crud.all(self.session))), 1)
