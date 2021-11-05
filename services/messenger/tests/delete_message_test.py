from unittest import mock, TestCase

from app.crud import message_crud, dialogue_crud, notification_crud
from app.schemas import UserData
from config import ERROR, SUCCESS, DELETE
from tests import BaseTest, async_loop


class DeleteMessageTestCase(BaseTest, TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.dialogue = async_loop(dialogue_crud.create(self.session, users_ids='1_2'))
        self.msg = async_loop(message_crud.create(self.session, dialogue_id=1, sender_id=1, msg='Hello world!'))

    def test_only_1_sender_connection(self):
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(1)) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.get_new_user(2)) as _:
                with mock.patch('app.requests.get_sender_data_request', return_value=self.get_new_user(1)) as _:
                    with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                        socket.send_json({'id': 1, 'type': DELETE})
                        response = socket.receive_json()
                        self.assertEqual(
                            response,
                            {'data': {'msg': 'Message has been deleted'}, 'type': SUCCESS}
                        )

                        response = socket.receive_json()
                        self.assertEqual(
                            response,
                            {
                                'data': {
                                    'sender': UserData(**self.get_new_user(1)).dict(),
                                    'id': 1,
                                },
                                'type': DELETE
                            }
                        )
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        socket.close()

    def test_only_2_sender_connections(self):
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(1)) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.get_new_user(2)) as _:
                with mock.patch('app.requests.get_sender_data_request', return_value=self.get_new_user(1)) as _:
                    with self.client.websocket_connect(f'{self.url}/ws/token') as socket_1:
                        with self.client.websocket_connect(f'{self.url}/ws/token') as socket_2:
                            socket_1.send_json(
                                {'id': 1, 'type': DELETE}
                            )
                            response = socket_1.receive_json()
                            self.assertEqual(
                                response,
                                {'data': {'msg': 'Message has been deleted'}, 'type': SUCCESS}
                            )

                            response = socket_1.receive_json()
                            self.assertEqual(
                                response,
                                {
                                    'data': {
                                        'sender': UserData(**self.get_new_user(1)).dict(),
                                        'id': 1,
                                    },
                                    'type': DELETE
                                }
                            )

                            response = socket_2.receive_json()
                            self.assertEqual(
                                response,
                                {'data': {'msg': 'Message has been deleted'}, 'type': SUCCESS}
                            )

                            response = socket_2.receive_json()
                            self.assertEqual(
                                response,
                                {
                                    'data': {
                                        'sender': UserData(**self.get_new_user(1)).dict(),
                                        'id': 1,
                                    },
                                    'type': DELETE
                                }
                            )
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        socket_1.close()
        socket_2.close()

    def test_sender_and_recipient_connections(self):
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(1)) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.get_new_user(2)) as _:
                with mock.patch('app.requests.get_sender_data_request', return_value=self.get_new_user(1)) as _:
                    with self.client.websocket_connect(f'{self.url}/ws/token') as socket_sender:
                        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(2)) as _:
                            with self.client.websocket_connect(f'{self.url}/ws/token') as socket_recipient:
                                socket_sender.send_json(
                                    {'id': 1, 'type': DELETE}
                                )
                                response = socket_sender.receive_json()
                                self.assertEqual(
                                    response,
                                    {'data': {'msg': 'Message has been deleted'}, 'type': SUCCESS}
                                )

                                response = socket_sender.receive_json()
                                self.assertEqual(
                                    response,
                                    {
                                        'data': {
                                            'sender': UserData(**self.get_new_user(1)).dict(),
                                            'id': 1,
                                        },
                                        'type': DELETE
                                    }
                                )

                                response = socket_recipient.receive_json()
                                self.assertEqual(
                                    response,
                                    {
                                        'data': {
                                            'sender': UserData(**self.get_new_user(1)).dict(),
                                            'id': 1,
                                        },
                                        'type': DELETE
                                    }
                                )
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        socket_sender.close()
        socket_recipient.close()

    def test_2_sender_and_2_recipient_connections(self):
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(1)) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.get_new_user(2)) as _:
                with mock.patch('app.requests.get_sender_data_request', return_value=self.get_new_user(1)) as _:
                    with self.client.websocket_connect(f'{self.url}/ws/token') as socket_sender_1:
                        with self.client.websocket_connect(f'{self.url}/ws/token') as socket_sender_2:
                            with mock.patch(
                                    'app.requests.sender_profile_request',
                                    return_value=self.get_new_user(2)
                            ) as _:
                                with self.client.websocket_connect(f'{self.url}/ws/token') as socket_recipient_1:
                                    with self.client.websocket_connect(f'{self.url}/ws/token') as socket_recipient_2:
                                        socket_sender_1.send_json(
                                            {'id': 1, 'type': DELETE}
                                        )
                                        response = socket_sender_1.receive_json()
                                        self.assertEqual(
                                            response,
                                            {'data': {'msg': 'Message has been deleted'}, 'type': SUCCESS}
                                        )

                                        response = socket_sender_1.receive_json()
                                        self.assertEqual(
                                            response,
                                            {
                                                'data': {
                                                    'sender': UserData(**self.get_new_user(1)).dict(),
                                                    'id': 1,
                                                },
                                                'type': DELETE
                                            }
                                        )

                                        response = socket_recipient_1.receive_json()
                                        self.assertEqual(
                                            response,
                                            {
                                                'data': {
                                                    'sender': UserData(**self.get_new_user(1)).dict(),
                                                    'id': 1,
                                                },
                                                'type': DELETE
                                            }
                                        )

                                        response = socket_sender_2.receive_json()
                                        self.assertEqual(
                                            response,
                                            {'data': {'msg': 'Message has been deleted'}, 'type': SUCCESS}
                                        )

                                        response = socket_sender_2.receive_json()
                                        self.assertEqual(
                                            response,
                                            {
                                                'data': {
                                                    'sender': UserData(**self.get_new_user(1)).dict(),
                                                    'id': 1,
                                                },
                                                'type': DELETE
                                            }
                                        )

                                        response = socket_recipient_2.receive_json()
                                        self.assertEqual(
                                            response,
                                            {
                                                'data': {
                                                    'sender': UserData(**self.get_new_user(1)).dict(),
                                                    'id': 1,
                                                },
                                                'type': DELETE
                                            }
                                        )

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        socket_sender_1.close()
        socket_recipient_1.close()
        socket_sender_2.close()
        socket_recipient_2.close()


class BadDeleteMessageTestCase(BaseTest, TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.dialogue = async_loop(dialogue_crud.create(self.session, users_ids='1_2'))
        self.msg = async_loop(message_crud.create(self.session, dialogue_id=1, sender_id=1, msg='Hello world!'))

    def test_invalid_data_schema(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(1)) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.get_new_user(2)) as _:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                    socket.send_json({'type': DELETE})
                    response = socket.receive_json()
                    self.assertEqual(
                        response,
                        {'data': {'detail': {'msg': 'Invalid DELETE data'}}, 'type': ERROR}
                    )

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        socket.close()

    def test_bad_sender(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(2)) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.get_new_user(1)) as _:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                    socket.send_json({'id': 1, 'type': DELETE})
                    response = socket.receive_json()
                    self.assertEqual(
                        response,
                        {'data': {'detail': {'msg': 'You not send this message'}}, 'type': ERROR}
                    )

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        socket.close()

    def test_bad_message_id(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(1)) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.get_new_user(2)) as _:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                    socket.send_json({'id': 143, 'type': DELETE})
                    response = socket.receive_json()
                    self.assertEqual(
                        response,
                        {'data': {'detail': {'msg': 'Message not found'}}, 'type': ERROR}
                    )

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        socket.close()
