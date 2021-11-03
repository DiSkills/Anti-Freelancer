from unittest import mock, TestCase

from app.crud import message_crud, dialogue_crud, notification_crud
from app.message.schemas import GetMessage, CreateMessage, UserData
from config import ERROR, SUCCESS, SEND
from tests import BaseTest, async_loop


class SendMessageTestCase(BaseTest, TestCase):

    def test_only_1_sender_connection_first_message(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(1)) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.get_new_user(2)) as _:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                    socket.send_json({'msg': 'Hello world!', 'recipient_id': 2, 'type': SEND})
                    response = socket.receive_json()
                    self.assertEqual(
                        response,
                        {'data': {'msg': 'Message has been send'}, 'type': SUCCESS}
                    )

                    response = socket.receive_json()
                    self.assertEqual(
                        response,
                        {
                            'data': GetMessage(
                                **{**async_loop(message_crud.get(self.session, id=1)).__dict__, 'viewed': False},
                                sender=UserData(**self.get_new_user(1))
                            ).dict(), 'type': SEND
                        }
                    )
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)

        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, False)
        self.assertEqual(async_loop(dialogue_crud.get(self.session, id=1)).users_ids, '1_2')
        socket.close()
        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).dialogue_id, 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 1)

    def test_only_2_sender_connections(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(1)) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.get_new_user(2)) as _:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket_1:
                    with self.client.websocket_connect(f'{self.url}/ws/token') as socket_2:
                        socket_1.send_json(
                            {'msg': 'Hello world!', 'recipient_id': 2, 'type': SEND}
                        )
                        response = socket_1.receive_json()
                        self.assertEqual(
                            response,
                            {'data': {'msg': 'Message has been send'}, 'type': SUCCESS}
                        )

                        response = socket_1.receive_json()
                        self.assertEqual(
                            response,
                            {
                                'data': GetMessage(
                                    **{**async_loop(message_crud.get(self.session, id=1)).__dict__, 'viewed': False},
                                    sender=UserData(**self.get_new_user(1))
                                ).dict(), 'type': SEND
                            }
                        )

                        response = socket_2.receive_json()
                        self.assertEqual(
                            response,
                            {'data': {'msg': 'Message has been send'}, 'type': SUCCESS}
                        )

                        response = socket_2.receive_json()
                        self.assertEqual(
                            response,
                            {
                                'data': GetMessage(
                                    **{**async_loop(message_crud.get(self.session, id=1)).__dict__, 'viewed': False},
                                    sender=UserData(**self.get_new_user(1)),
                                ).dict(), 'type': SEND
                            }
                        )
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)

        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, False)
        self.assertEqual(async_loop(dialogue_crud.get(self.session, id=1)).users_ids, '1_2')
        socket_1.close()
        socket_2.close()
        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).dialogue_id, 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 1)

    def test_sender_and_recipient_connections(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(1)) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.get_new_user(2)) as _:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket_sender:
                    with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(2)) as _:
                        with self.client.websocket_connect(f'{self.url}/ws/token') as socket_recipient:
                            socket_sender.send_json(
                                {'msg': 'Hello world!', 'recipient_id': 2, 'type': SEND}
                            )
                            response = socket_sender.receive_json()
                            self.assertEqual(
                                response,
                                {'data': {'msg': 'Message has been send'}, 'type': SUCCESS}
                            )

                            response = socket_sender.receive_json()
                            self.assertEqual(
                                response,
                                {
                                    'data': GetMessage(
                                        **{
                                            **async_loop(message_crud.get(self.session, id=1)).__dict__, 'viewed': False
                                        },
                                        sender=UserData(**self.get_new_user(1)),
                                    ).dict(), 'type': SEND
                                }
                            )

                            response = socket_recipient.receive_json()
                            self.assertEqual(
                                response,
                                {
                                    'data': GetMessage(
                                        **{
                                            **async_loop(message_crud.get(self.session, id=1)).__dict__, 'viewed': False
                                        },
                                        sender=UserData(**self.get_new_user(1)),
                                    ).dict(), 'type': SEND
                                }
                            )
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 1)

        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, False)
        self.assertEqual(async_loop(dialogue_crud.get(self.session, id=1)).users_ids, '1_2')
        socket_sender.close()
        socket_recipient.close()
        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).dialogue_id, 1)

    def test_2_sender_and_2_recipient_connections(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(1)) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.get_new_user(2)) as _:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket_sender_1:
                    with self.client.websocket_connect(f'{self.url}/ws/token') as socket_sender_2:
                        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(2)) as _:
                            with self.client.websocket_connect(f'{self.url}/ws/token') as socket_recipient_1:
                                with self.client.websocket_connect(f'{self.url}/ws/token') as socket_recipient_2:
                                    socket_sender_1.send_json(
                                        {'msg': 'Hello world!', 'recipient_id': 2, 'type': SEND}
                                    )
                                    response = socket_sender_1.receive_json()
                                    self.assertEqual(
                                        response,
                                        {'data': {'msg': 'Message has been send'}, 'type': SUCCESS}
                                    )

                                    response = socket_sender_1.receive_json()
                                    self.assertEqual(
                                        response,
                                        {
                                            'data': GetMessage(
                                                **{
                                                    **async_loop(message_crud.get(self.session, id=1)).__dict__,
                                                    'viewed': False
                                                }, sender=UserData(**self.get_new_user(1)),
                                            ).dict(), 'type': SEND
                                        }
                                    )

                                    response = socket_recipient_1.receive_json()
                                    self.assertEqual(
                                        response,
                                        {
                                            'data': GetMessage(
                                                **{
                                                    **async_loop(message_crud.get(self.session, id=1)).__dict__,
                                                    'viewed': False
                                                }, sender=UserData(**self.get_new_user(1)),
                                            ).dict(), 'type': SEND
                                        }
                                    )

                                    response = socket_sender_2.receive_json()
                                    self.assertEqual(
                                        response,
                                        {'data': {'msg': 'Message has been send'}, 'type': SUCCESS}
                                    )

                                    response = socket_sender_2.receive_json()
                                    self.assertEqual(
                                        response,
                                        {
                                            'data': GetMessage(
                                                **{
                                                    **async_loop(message_crud.get(self.session, id=1)).__dict__,
                                                    'viewed': False
                                                }, sender=UserData(**self.get_new_user(1)),
                                            ).dict(), 'type': SEND
                                        }
                                    )

                                    response = socket_recipient_2.receive_json()
                                    self.assertEqual(
                                        response,
                                        {
                                            'data': GetMessage(
                                                **{
                                                    **async_loop(message_crud.get(self.session, id=1)).__dict__,
                                                    'viewed': False
                                                }, sender=UserData(**self.get_new_user(1)),
                                            ).dict(), 'type': SEND
                                        }
                                    )

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 1)

        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, False)
        self.assertEqual(async_loop(dialogue_crud.get(self.session, id=1)).users_ids, '1_2')
        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).dialogue_id, 1)
        socket_sender_1.close()
        socket_recipient_1.close()
        socket_sender_2.close()
        socket_recipient_2.close()

    def test_only_1_sender_connection_second_message_after_recipient(self):
        schema = CreateMessage(sender_id=1, msg='Hello world!', recipient_id=2)

        async_loop(dialogue_crud.create(self.session, users_ids=f'1_2'))
        del schema.recipient_id
        async_loop(message_crud.create(self.session, **schema.dict(), dialogue_id=1))
        async_loop(notification_crud.create(self.session, sender_id=schema.sender_id, message_id=1))

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 1)

        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(2)) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.get_new_user(1)) as _:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                    socket.send_json({'msg': 'Hello world!', 'recipient_id': 1, 'type': SEND})
                    response = socket.receive_json()
                    self.assertEqual(
                        response,
                        {'data': {'msg': 'Message has been send'}, 'type': SUCCESS}
                    )

                    response = socket.receive_json()
                    self.assertEqual(
                        response,
                        {
                            'data': GetMessage(
                                **{**async_loop(message_crud.get(self.session, id=2)).__dict__, 'viewed': False},
                                sender=UserData(**self.get_new_user(2)),
                            ).dict(), 'type': SEND
                        }
                    )
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 2)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)

        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, False)
        self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, False)
        self.assertEqual(async_loop(dialogue_crud.get(self.session, id=1)).users_ids, '1_2')
        socket.close()
        self.assertEqual(async_loop(message_crud.get(self.session, id=2)).dialogue_id, 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 2)

    def test_only_1_sender_connection_second_message_after_sender(self):
        schema = CreateMessage(sender_id=1, msg='Hello world!', recipient_id=2)

        async_loop(dialogue_crud.create(self.session, users_ids=f'1_2'))
        del schema.recipient_id
        async_loop(message_crud.create(self.session, **schema.dict(), dialogue_id=1))
        async_loop(notification_crud.create(self.session, sender_id=schema.sender_id, message_id=1))

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 1)

        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(1)) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.get_new_user(2)) as _:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                    socket.send_json({'msg': 'Hello world!', 'recipient_id': 2, 'type': SEND})
                    response = socket.receive_json()
                    self.assertEqual(
                        response,
                        {'data': {'msg': 'Message has been send'}, 'type': SUCCESS}
                    )

                    response = socket.receive_json()
                    self.assertEqual(
                        response,
                        {
                            'data': GetMessage(
                                **{**async_loop(message_crud.get(self.session, id=2)).__dict__, 'viewed': False},
                                sender=UserData(**self.get_new_user(1)),
                            ).dict(), 'type': SEND
                        }
                    )
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 2)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)

        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).viewed, False)
        self.assertEqual(async_loop(message_crud.get(self.session, id=2)).viewed, False)
        self.assertEqual(async_loop(dialogue_crud.get(self.session, id=1)).users_ids, '1_2')
        socket.close()
        self.assertEqual(async_loop(message_crud.get(self.session, id=2)).dialogue_id, 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 2)


class BadSendMessageTestCase(BaseTest, TestCase):

    def test_yourself(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(1)) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.get_new_user(1)) as _:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                    socket.send_json({'recipient_id': 1, 'type': SEND, 'msg': 'Hello world!'})
                    response = socket.receive_json()
                    self.assertEqual(
                        response,
                        {'data': {'detail': {'msg': 'You cannot send yourself message'}}, 'type': ERROR}
                    )
        socket.close()
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

    def test_bad_recipient(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(1)) as _:
            with mock.patch('app.requests.get_user_request') as recipient:
                recipient.side_effect = ValueError()
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                    socket.send_json({'msg': 'Hello world!', 'recipient_id': 2, 'type': SEND})
                    response = socket.receive_json()
                    self.assertEqual(
                        response,
                        {'data': {'detail': {'msg': 'Recipient not found'}}, 'type': ERROR}
                    )
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        socket.close()

    def test_invalid_data_schema(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(1)) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.get_new_user(2)) as _:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                    socket.send_json({'recipient_id': 2, 'type': SEND})
                    response = socket.receive_json()
                    self.assertEqual(
                        response,
                        {'data': {'detail': {'msg': 'Invalid SEND data'}}, 'type': ERROR}
                    )
        socket.close()

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

    def test_not_type(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(1)) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.get_new_user(2)) as _:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                    socket.send_json({'recipient_id': 2})
                    response = socket.receive_json()
                    self.assertEqual(
                        response,
                        {'data': {'detail': {'msg': 'Request type not found'}}, 'type': ERROR}
                    )
        socket.close()

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

    def test_bad_type(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request', return_value=self.get_new_user(1)) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.get_new_user(2)) as _:
                with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                    socket.send_json({'recipient_id': 2, 'type': 'Hello world!'})
                    response = socket.receive_json()
                    self.assertEqual(
                        response,
                        {'data': {'detail': {'msg': 'Bad request type'}}, 'type': ERROR}
                    )
        socket.close()

        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

    def test_bad_sender(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        with mock.patch('app.requests.sender_profile_request') as sender:
            sender.side_effect = ValueError('Token lifetime ended')
            with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                response = socket.receive_json()
                self.assertEqual(
                    response,
                    {'data': {'detail': {'msg': 'Token lifetime ended'}}, 'type': ERROR}
                )
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 0)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        socket.close()
