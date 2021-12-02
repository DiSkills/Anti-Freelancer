from unittest import TestCase, mock

from app.crud import dialogue_crud, message_crud
from app.message.schemas import GetMessage
from config import SERVER_MESSENGER_BACKEND, API
from tests import BaseTest, async_loop


class MessageTestCase(BaseTest, TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.dialogue = async_loop(dialogue_crud.create(self.session, users_ids='1_2'))
        self.dialogue = async_loop(dialogue_crud.create(self.session, users_ids='2_3'))
        self.msg = async_loop(
            message_crud.create(self.session, dialogue_id=1, sender_id=1, msg='Hello world!')
        )
        async_loop(
            message_crud.create(self.session, dialogue_id=1, sender_id=1, msg='Hello world!')
        )

    def test_view_messages(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 2)
        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, False)
        self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, False)

        async_loop(
            message_crud.create(self.session, dialogue_id=2, sender_id=1, msg='Hello world!')
        )
        self.assertEqual(async_loop(message_crud.get(self.session, id=3)).viewed, False)

        headers = {'Authorization': 'Bearer Token'}

        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.put(
                f'{self.url}/messages/view?dialogue_id=1', json=[1], headers=headers
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Messages has been viewed'})
            async_loop(self.session.commit())
            self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, False)
            self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, False)

        with mock.patch('app.permission.permission', return_value=2) as _:
            response = self.client.put(
                f'{self.url}/messages/view?dialogue_id=143', json=[1, 2], headers=headers
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Dialogue not found'})
            async_loop(self.session.commit())
            self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, False)
            self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, False)

        with mock.patch('app.permission.permission', return_value=143) as _:
            response = self.client.put(
                f'{self.url}/messages/view?dialogue_id=1', json=[1, 2], headers=headers
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'You are not in this dialogue'})
            async_loop(self.session.commit())
            self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, False)
            self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, False)

        with mock.patch('app.permission.permission', return_value=2) as _:
            response = self.client.put(
                f'{self.url}/messages/view?dialogue_id=1', json=[1], headers=headers
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Messages has been viewed'})
            async_loop(self.session.commit())
            self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, True)
            self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, False)

            response = self.client.put(
                f'{self.url}/messages/view?dialogue_id=1', json=[1, 2], headers=headers
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Messages has been viewed'})
            async_loop(self.session.commit())
            self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, True)
            self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, True)

            response = self.client.put(
                f'{self.url}/messages/view?dialogue_id=1', json=[3], headers=headers
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Messages has been viewed'})
            async_loop(self.session.commit())
            self.assertEqual(async_loop(message_crud.get(self.session, id=3)).viewed, False)

        with mock.patch('app.permission.permission', return_value=2) as _:
            response = self.client.put(
                f'{self.url}/messages/view?dialogue_id=2', json=[3], headers=headers
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Messages has been viewed'})
            async_loop(self.session.commit())

        self.assertEqual(async_loop(message_crud.get(self.session, id=3)).viewed, True)

    def test_messages_paginate(self):
        headers = {'Authorization': 'Bearer Token'}

        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.get(
                f'{self.url}/messages/dialogue?page=1&page_size=1&dialogue_id=1',
                headers=headers
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()['results']), 1)
            self.assertEqual(
                response.json(), {
                    'next': f'{SERVER_MESSENGER_BACKEND}{API}/messages/dialogue?page=2&page_size=1&dialogue_id=1',
                    'previous': None,
                    'page': 1,
                    'results': [
                        GetMessage(**async_loop(message_crud.get(self.session, id=2)).__dict__).dict()
                    ]
                }
            )

            response = self.client.get(
                f'{self.url}/messages/dialogue?page=2&page_size=1&dialogue_id=1',
                headers=headers
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()['results']), 1)
            self.assertEqual(
                response.json(), {
                    'next': None,
                    'previous': f'{SERVER_MESSENGER_BACKEND}{API}/messages/dialogue?page=1&page_size=1&dialogue_id=1',
                    'page': 2,
                    'results': [
                        GetMessage(**async_loop(message_crud.get(self.session, id=1)).__dict__).dict()
                    ]
                }
            )

            response = self.client.get(
                f'{self.url}/messages/dialogue?page=3&page_size=1&dialogue_id=1',
                headers=headers
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Results not found'})

        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.get(
                f'{self.url}/messages/dialogue?page=1&page_size=1&dialogue_id=2',
                headers=headers
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'You are not in this dialogue'})

        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.get(
                f'{self.url}/messages/dialogue?page=1&page_size=1&dialogue_id=143',
                headers=headers
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Dialogue not found'})
