from unittest import TestCase, mock

from app.crud import message_crud
from tests import BaseTest, async_loop


class SendMessageTestCase(BaseTest, TestCase):

    def test_bad_type(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)

        with mock.patch('app.requests.get_user_request', return_value=self.user2) as _:
            with mock.patch('app.requests.sender_profile_request', return_value=self.user) as _:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                    socket.send_json({'msg': 'Hello world!', 'recipient_id': 2, 'type': 'Hello world!'})
                    self.assertEqual(
                        socket.receive_json(), {
                            'type': 'ERROR',
                            'data': {'msg': 'Bad request type'}
                        }
                    )

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        socket.close()

    def test_not_type(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)

        with mock.patch('app.requests.get_user_request', return_value=self.user2) as _:
            with mock.patch('app.requests.sender_profile_request', return_value=self.user) as _:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                    socket.send_json({'msg': 'Hello world!', 'recipient_id': 2})
                    self.assertEqual(
                        socket.receive_json(), {
                            'type': 'ERROR',
                            'data': {'msg': 'Request type not found'}
                        }
                    )

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        socket.close()

    def test_send_message(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)

        with mock.patch('app.requests.get_user_request', return_value={**self.user2, 'id': 4}) as _:
            with mock.patch('app.requests.sender_profile_request', return_value=self.user) as _:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                    socket.send_json({'msg': 'Hello world!', 'recipient_id': 4, 'type': 'SEND'})
                    self.assertEqual(
                        socket.receive_json(), {
                            'type': 'SUCCESS',
                            'data': {'msg': 'Message has been send'}
                        }
                    )

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        socket.close()
        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, False)

    def test_recipient_not_found(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)

        with mock.patch('app.requests.get_user_request') as recipient:
            recipient.side_effect = ValueError('User not found')
            with mock.patch('app.requests.sender_profile_request', return_value=self.user) as _:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                    socket.send_json({'msg': 'Hello world!', 'recipient_id': 42, 'type': 'SEND'})
                    self.assertEqual(
                        socket.receive_json(), {
                            'type': 'ERROR',
                            'data': {'msg': 'Recipient not found'},
                        }
                    )

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        socket.close()

    def test_sender_not_found(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request') as sender:
            sender.side_effect = ValueError('User not found')
            with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                self.assertEqual(
                    socket.receive_json(), {
                        'type': 'ERROR',
                        'data': {'msg': 'User not found'},
                    }
                )

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        socket.close()

    def test_send_message_2_connection(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.user2) as _:
            with self.client.websocket_connect(f'{self.url}/ws/token') as socket_2:
                with mock.patch('app.requests.sender_profile_request', return_value=self.user) as _:
                    with self.client.websocket_connect(f'{self.url}/ws/token') as socket_1:
                        socket_1.send_json({'msg': 'Hello world!', 'recipient_id': 2, 'type': 'SEND'})

                created_at = f'{async_loop(message_crud.get(self.session, id=1)).created_at}Z'.replace(' ', 'T')
                self.assertEqual(
                    socket_2.receive_json(),
                    {
                        'type': 'SEND_MESSAGE',
                        'data': {
                            'sender_id': 1, 'recipient_id': 2, 'msg': 'Hello world!', 'id': 1, 'created_at': created_at,
                            'sender': self.user, 'viewed': False
                        }
                    }
                )

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, True)
        socket_1.close()
        socket_2.close()

    def test_send_message_2_sender_connection(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.user2) as _:
            with self.client.websocket_connect(f'{self.url}/ws/token') as socket_2:
                with mock.patch('app.requests.sender_profile_request', return_value=self.user) as _:
                    with self.client.websocket_connect(f'{self.url}/ws/token') as socket_3:
                        with self.client.websocket_connect(f'{self.url}/ws/token') as socket_1:
                            socket_1.send_json({'msg': 'Hello world!', 'recipient_id': 2, 'type': 'SEND'})
                            self.assertEqual(
                                socket_1.receive_json(), {
                                    'type': 'SUCCESS',
                                    'data': {'msg': 'Message has been send'}
                                }
                            )
                            created_at = f'{async_loop(message_crud.get(self.session, id=1)).created_at}Z'.replace(
                                ' ',
                                'T'
                            )
                            self.assertEqual(
                                socket_1.receive_json(),
                                {
                                    'type': 'SEND_MESSAGE',
                                    'data': {
                                        'sender_id': 1, 'recipient_id': 2, 'msg': 'Hello world!', 'id': 1,
                                        'created_at': created_at, 'sender': self.user, 'viewed': False
                                    }
                                }
                            )
                        self.assertEqual(
                            socket_3.receive_json(), {
                                'type': 'SUCCESS',
                                'data': {'msg': 'Message has been send'}
                            }
                        )
                        created_at = f'{async_loop(message_crud.get(self.session, id=1)).created_at}Z'.replace(' ', 'T')
                        self.assertEqual(
                            socket_3.receive_json(),
                            {
                                'type': 'SEND_MESSAGE',
                                'data': {
                                    'sender_id': 1, 'recipient_id': 2, 'msg': 'Hello world!', 'id': 1,
                                    'created_at': created_at, 'sender': self.user, 'viewed': False
                                }
                            }
                        )

                self.assertEqual(
                    socket_2.receive_json(),
                    {
                        'type': 'SEND_MESSAGE',
                        'data': {
                            'sender_id': 1, 'recipient_id': 2, 'msg': 'Hello world!', 'id': 1, 'created_at': created_at,
                            'sender': self.user, 'viewed': False
                        }
                    }
                )

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        socket_1.close()
        socket_2.close()
        socket_3.close()
        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, True)

    def test_send_message_yourself(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.user) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.user) as _:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                    socket.send_json({'msg': 'Hello world!', 'recipient_id': 1, 'type': 'SEND'})
                    self.assertEqual(
                        socket.receive_json(), {
                            'type': 'ERROR',
                            'data': {'msg': 'User can\'t send yourself message'}
                        }
                    )

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        socket.close()

    def test_send_message_3_connection(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.user2) as _:
            with self.client.websocket_connect(f'{self.url}/ws/token') as socket_3:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket_2:
                    with mock.patch('app.requests.sender_profile_request', return_value=self.user) as _:
                        with self.client.websocket_connect(f'{self.url}/ws/token') as socket_1:
                            socket_1.send_json({'msg': 'Hello world!', 'recipient_id': 2, 'type': 'SEND'})

                    created_at = f'{async_loop(message_crud.get(self.session, id=1)).created_at}Z'.replace(' ', 'T')
                    self.assertEqual(
                        socket_2.receive_json(),
                        {
                            'type': 'SEND_MESSAGE',
                            'data': {
                                'sender_id': 1, 'recipient_id': 2, 'msg': 'Hello world!', 'id': 1,
                                'created_at': created_at, 'sender': self.user, 'viewed': False
                            }
                        }
                    )
                self.assertEqual(
                    socket_3.receive_json(),
                    {
                        'type': 'SEND_MESSAGE',
                        'data': {
                            'sender_id': 1, 'recipient_id': 2, 'msg': 'Hello world!', 'id': 1, 'created_at': created_at,
                            'sender': self.user, 'viewed': False
                        }
                    }
                )

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        socket_1.close()
        socket_2.close()
        socket_3.close()
        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, True)

    def test_invalid_data(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.user) as _:
            with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                socket.send_json({'msg': 'Hello world!', 'type': 'SEND'})
                self.assertEqual(
                    socket.receive_json(), {
                        'type': 'ERROR',
                        'data': {'msg': 'Invalid data'}
                    }
                )

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        socket.close()

        with mock.patch('app.requests.sender_profile_request', return_value=self.user) as _:
            with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                socket.send_json({'recipient_id': 2, 'type': 'SEND'})
                self.assertEqual(
                    socket.receive_json(), {
                        'type': 'ERROR',
                        'data': {'msg': 'Invalid data'}
                    }
                )

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        socket.close()

        with mock.patch('app.requests.sender_profile_request', return_value=self.user) as _:
            with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                socket.send_json({'data': 'Hello world!', 'type': 'SEND'})
                self.assertEqual(
                    socket.receive_json(), {
                        'type': 'ERROR',
                        'data': {'msg': 'Invalid data'}
                    }
                )

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        socket.close()
