from unittest import TestCase, mock

from app.crud import message_crud
from config import SERVER_MESSENGER_BACKEND, API
from tests import BaseTest, async_loop


class GetMessagesTestCase(BaseTest, TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.message1 = async_loop(message_crud.create(self.session, msg='Hello world!', sender_id=1, recipient_id=2))

        self.message2 = async_loop(message_crud.create(self.session, msg='Hello python!', sender_id=1, recipient_id=2))

        self.message3 = async_loop(message_crud.create(self.session, msg='Hello FastAPI!', sender_id=2, recipient_id=1))

        self.message4 = async_loop(message_crud.create(self.session, msg='Hello Django!', sender_id=1, recipient_id=3))
        async_loop(self.session.commit())

    def test_bad_get_messages(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 4)
        self.assertEqual(async_loop(message_crud.get(self.session, id=4)).viewed, False)
        self.assertEqual(async_loop(message_crud.get(self.session, id=3)).viewed, False)
        self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, False)
        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, False)

        headers = {'Authorization': 'Bearer Token'}

        with mock.patch('app.permission.permission', return_value=1) as _:
            with mock.patch('app.message.views.get_sender', return_value=self.user) as _:
                with mock.patch('app.message.views.get_recipient', return_value=self.user2) as _:
                    response = self.client.get(
                        f'{self.url}/messages/dialog?recipient_id=143&page=1&page_size=1', headers=headers
                    )
                    self.assertEqual(response.status_code, 400)
                    self.assertEqual(response.json(), {'detail': 'Results not found'})

    def test_only_4_message(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 4)
        self.assertEqual(async_loop(message_crud.get(self.session, id=4)).viewed, False)
        self.assertEqual(async_loop(message_crud.get(self.session, id=3)).viewed, False)
        self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, False)
        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, False)

        headers = {'Authorization': 'Bearer Token'}

        with mock.patch('app.permission.permission', return_value=3) as _:
            with mock.patch('app.message.views.get_sender', return_value={**self.user, 'id': 3}) as _:
                with mock.patch('app.message.views.get_recipient', return_value=self.user) as _:
                    response = self.client.get(
                        f'{self.url}/messages/dialog?recipient_id=1&page=1&page_size=1', headers=headers
                    )
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(
                        response.json(),
                        {
                            'next': None,
                            'page': 1,
                            'previous': None,
                            'results': [{
                                'created_at': f'{self.message4.created_at}Z'.replace(' ', 'T'),
                                'id': 4,
                                'msg': 'Hello Django!',
                                'recipient': {
                                    'avatar': 'http://localhost:8000/media/test/lol.png',
                                    'id': 3,
                                    'username': 'test'
                                },
                                'recipient_id': 3,
                                'sender': {
                                    'avatar': 'http://localhost:8000/media/test/lol.png',
                                    'id': 1,
                                    'username': 'test'
                                },
                                'sender_id': 1,
                                'viewed': False
                            }]
                        }
                    )
                    async_loop(self.session.commit())
                    self.assertEqual(async_loop(message_crud.get(self.session, id=4)).viewed, True)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=3)).viewed, False)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, False)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, False)

    def test_get_messages(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 4)
        self.assertEqual(async_loop(message_crud.get(self.session, id=4)).viewed, False)
        self.assertEqual(async_loop(message_crud.get(self.session, id=3)).viewed, False)
        self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, False)
        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, False)

        headers = {'Authorization': 'Bearer Token'}

        with mock.patch('app.permission.permission', return_value=1) as _:
            with mock.patch('app.message.views.get_sender', return_value=self.user) as _:
                with mock.patch('app.message.views.get_recipient', return_value=self.user2) as _:
                    # 3 Message
                    response = self.client.get(
                        f'{self.url}/messages/dialog?recipient_id=2&page=1&page_size=1', headers=headers
                    )
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(
                        response.json(),
                        {
                            'next': f'{SERVER_MESSENGER_BACKEND}{API}/messages/dialog?page=2&page_size=1&sender_id=1&recipient_id=2',
                            'page': 1,
                            'previous': None,
                            'results': [{
                                'created_at': f'{self.message3.created_at}Z'.replace(' ', 'T'),
                                'id': 3,
                                'msg': 'Hello FastAPI!',
                                'recipient': {
                                    'avatar': 'http://localhost:8000/media/test/lol.png',
                                    'id': 1,
                                    'username': 'test'
                                },
                                'recipient_id': 1,
                                'sender': {
                                    'avatar': 'http://localhost:8000/media/test2/lol.png',
                                    'id': 2,
                                    'username': 'test2'
                                },
                                'sender_id': 2,
                                'viewed': False
                            }]
                        }
                    )
                    async_loop(self.session.commit())
                    self.assertEqual(async_loop(message_crud.get(self.session, id=4)).viewed, False)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=3)).viewed, True)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, False)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, False)

                    # 2 Message
                    response = self.client.get(
                        f'{self.url}/messages/dialog?recipient_id=2&page=2&page_size=1', headers=headers
                    )
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(
                        response.json(),
                        {
                            'next': f'{SERVER_MESSENGER_BACKEND}{API}/messages/dialog?page=3&page_size=1&sender_id=1&recipient_id=2',
                            'page': 2,
                            'previous': f'{SERVER_MESSENGER_BACKEND}{API}/messages/dialog?page=1&page_size=1&sender_id=1&recipient_id=2',
                            'results': [{
                                'created_at': f'{self.message2.created_at}Z'.replace(' ', 'T'),
                                'id': 2,
                                'msg': 'Hello python!',
                                'recipient': {
                                    'avatar': 'http://localhost:8000/media/test2/lol.png',
                                    'id': 2,
                                    'username': 'test2'
                                },
                                'recipient_id': 2,
                                'sender': {
                                    'avatar': 'http://localhost:8000/media/test/lol.png',
                                    'id': 1,
                                    'username': 'test'
                                },
                                'sender_id': 1,
                                'viewed': False
                            }]
                        }
                    )
                    async_loop(self.session.commit())
                    self.assertEqual(async_loop(message_crud.get(self.session, id=4)).viewed, False)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=3)).viewed, True)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, True)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, False)

                    # 1 Message
                    response = self.client.get(
                        f'{self.url}/messages/dialog?recipient_id=2&page=3&page_size=1', headers=headers
                    )
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(
                        response.json(),
                        {
                            'next': None,
                            'page': 3,
                            'previous': f'{SERVER_MESSENGER_BACKEND}{API}/messages/dialog?page=2&page_size=1&sender_id=1&recipient_id=2',
                            'results': [{
                                'created_at': f'{self.message1.created_at}Z'.replace(' ', 'T'),
                                'id': 1,
                                'msg': 'Hello world!',
                                'recipient': {
                                    'avatar': 'http://localhost:8000/media/test2/lol.png',
                                    'id': 2,
                                    'username': 'test2'
                                },
                                'recipient_id': 2,
                                'sender': {
                                    'avatar': 'http://localhost:8000/media/test/lol.png',
                                    'id': 1,
                                    'username': 'test'
                                },
                                'sender_id': 1,
                                'viewed': False
                            }]
                        }
                    )
                    async_loop(self.session.commit())
                    self.assertEqual(async_loop(message_crud.get(self.session, id=4)).viewed, False)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=3)).viewed, True)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, True)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, True)

        # 4 Message
        with mock.patch('app.permission.permission', return_value=3) as _:
            with mock.patch('app.message.views.get_sender', return_value={**self.user, 'id': 3}) as _:
                with mock.patch('app.message.views.get_recipient', return_value=self.user) as _:
                    response = self.client.get(
                        f'{self.url}/messages/dialog?recipient_id=1&page=1&page_size=1', headers=headers
                    )
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(
                        response.json(),
                        {
                            'next': None,
                            'page': 1,
                            'previous': None,
                            'results': [{
                                'created_at': f'{self.message4.created_at}Z'.replace(' ', 'T'),
                                'id': 4,
                                'msg': 'Hello Django!',
                                'recipient': {
                                    'avatar': 'http://localhost:8000/media/test/lol.png',
                                    'id': 3,
                                    'username': 'test'
                                },
                                'recipient_id': 3,
                                'sender': {
                                    'avatar': 'http://localhost:8000/media/test/lol.png',
                                    'id': 1,
                                    'username': 'test'
                                },
                                'sender_id': 1,
                                'viewed': False
                            }]
                        }
                    )
                    async_loop(self.session.commit())
                    self.assertEqual(async_loop(message_crud.get(self.session, id=4)).viewed, True)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=3)).viewed, True)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, True)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, True)

        # 3, 2, 1 messages (viewed)
        with mock.patch('app.permission.permission', return_value=1) as _:
            with mock.patch('app.message.views.get_sender', return_value=self.user) as _:
                with mock.patch('app.message.views.get_recipient', return_value=self.user2) as _:
                    response = self.client.get(
                        f'{self.url}/messages/dialog?recipient_id=2&page=1&page_size=4', headers=headers
                    )
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(
                        response.json(),
                        {
                            'next': None,
                            'page': 1,
                            'previous': None,
                            'results': [
                                {
                                    'created_at': f'{self.message3.created_at}Z'.replace(' ', 'T'),
                                    'id': 3,
                                    'msg': 'Hello FastAPI!',
                                    'recipient': {
                                        'avatar': 'http://localhost:8000/media/test/lol.png',
                                        'id': 1,
                                        'username': 'test'
                                    },
                                    'recipient_id': 1,
                                    'sender': {
                                        'avatar': 'http://localhost:8000/media/test2/lol.png',
                                        'id': 2,
                                        'username': 'test2'
                                    },
                                    'sender_id': 2,
                                    'viewed': True
                                },
                                {
                                    'created_at': f'{self.message2.created_at}Z'.replace(' ', 'T'),
                                    'id': 2,
                                    'msg': 'Hello python!',
                                    'recipient': {
                                        'avatar': 'http://localhost:8000/media/test2/lol.png',
                                        'id': 2,
                                        'username': 'test2'
                                    },
                                    'recipient_id': 2,
                                    'sender': {
                                        'avatar': 'http://localhost:8000/media/test/lol.png',
                                        'id': 1,
                                        'username': 'test'
                                    },
                                    'sender_id': 1,
                                    'viewed': True
                                },
                                {
                                    'created_at': f'{self.message1.created_at}Z'.replace(' ', 'T'),
                                    'id': 1,
                                    'msg': 'Hello world!',
                                    'recipient': {
                                        'avatar': 'http://localhost:8000/media/test2/lol.png',
                                        'id': 2,
                                        'username': 'test2'
                                    },
                                    'recipient_id': 2,
                                    'sender': {
                                        'avatar': 'http://localhost:8000/media/test/lol.png',
                                        'id': 1,
                                        'username': 'test'
                                    },
                                    'sender_id': 1,
                                    'viewed': True
                                }
                            ]
                        }
                    )
                    async_loop(self.session.commit())
                    self.assertEqual(async_loop(message_crud.get(self.session, id=4)).viewed, True)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=3)).viewed, True)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, True)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, True)

    def test_3_2_1_messages_un_viewed(self):
        # 3, 2, 1 messages (un viewed)
        headers = {'Authorization': 'Bearer Token'}
        self.assertEqual(async_loop(message_crud.get(self.session, id=4)).viewed, False)
        self.assertEqual(async_loop(message_crud.get(self.session, id=3)).viewed, False)
        self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, False)
        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, False)

        with mock.patch('app.permission.permission', return_value=1) as _:
            with mock.patch('app.message.views.get_sender', return_value=self.user) as _:
                with mock.patch('app.message.views.get_recipient', return_value=self.user2) as _:
                    response = self.client.get(
                        f'{self.url}/messages/dialog?recipient_id=2&page=1&page_size=4', headers=headers
                    )
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(
                        response.json(),
                        {
                            'next': None,
                            'page': 1,
                            'previous': None,
                            'results': [
                                {
                                    'created_at': f'{async_loop(message_crud.get(self.session, id=3)).created_at}Z'.replace(
                                        ' ',
                                        'T'
                                    ),
                                    'id': 3,
                                    'msg': 'Hello FastAPI!',
                                    'recipient': {
                                        'avatar': 'http://localhost:8000/media/test/lol.png',
                                        'id': 1,
                                        'username': 'test'
                                    },
                                    'recipient_id': 1,
                                    'sender': {
                                        'avatar': 'http://localhost:8000/media/test2/lol.png',
                                        'id': 2,
                                        'username': 'test2'
                                    },
                                    'sender_id': 2,
                                    'viewed': False
                                },
                                {
                                    'created_at': f'{async_loop(message_crud.get(self.session, id=2)).created_at}Z'.replace(
                                        ' ',
                                        'T'
                                    ),
                                    'id': 2,
                                    'msg': 'Hello python!',
                                    'recipient': {
                                        'avatar': 'http://localhost:8000/media/test2/lol.png',
                                        'id': 2,
                                        'username': 'test2'
                                    },
                                    'recipient_id': 2,
                                    'sender': {
                                        'avatar': 'http://localhost:8000/media/test/lol.png',
                                        'id': 1,
                                        'username': 'test'
                                    },
                                    'sender_id': 1,
                                    'viewed': False
                                },
                                {
                                    'created_at': f'{async_loop(message_crud.get(self.session, id=1)).created_at}Z'.replace(
                                        ' ',
                                        'T'
                                    ),
                                    'id': 1,
                                    'msg': 'Hello world!',
                                    'recipient': {
                                        'avatar': 'http://localhost:8000/media/test2/lol.png',
                                        'id': 2,
                                        'username': 'test2'
                                    },
                                    'recipient_id': 2,
                                    'sender': {
                                        'avatar': 'http://localhost:8000/media/test/lol.png',
                                        'id': 1,
                                        'username': 'test'
                                    },
                                    'sender_id': 1,
                                    'viewed': False
                                }
                            ]
                        }
                    )
                    async_loop(self.session.commit())
                    self.assertEqual(async_loop(message_crud.get(self.session, id=4)).viewed, False)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=3)).viewed, True)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, True)
                    self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, True)
