from unittest import TestCase, mock

from app.crud import message_crud, dialogue_crud, notification_crud
from app.message.schemas import GetMessage
from app.schemas import UserData
from tests import BaseTest, async_loop


class NotificationTestCase(BaseTest, TestCase):

    def test_notifications(self):
        async_loop(dialogue_crud.create(self.session, users_ids='1_2'))
        async_loop(message_crud.create(self.session, sender_id=1, msg='Hello world!', dialogue_id=1))
        async_loop(
            notification_crud.create(
                self.session,
                sender_id=1,
                recipient_id=2,
                message_id=1,
            )
        )
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 1)

        async_loop(message_crud.create(self.session, sender_id=1, msg='Hello world!', dialogue_id=1))
        async_loop(
            notification_crud.create(
                self.session,
                sender_id=1,
                recipient_id=2,
                message_id=2,
            )
        )
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 2)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 2)

        headers = {'Authorization': 'Bearer Token'}

        # Get all
        with mock.patch('app.permission.permission', return_value=2) as _:
            response = self.client.get(f'{self.url}/notifications/', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(), [
                    {
                        'id': 2,
                        'type': 'SEND',
                        'data': {
                            **GetMessage(
                                **async_loop(message_crud.get(self.session, id=2)).__dict__,
                            ).dict(),
                            'created_at': f'{async_loop(message_crud.get(self.session, id=2)).created_at}Z'.replace(
                                ' ',
                                'T'
                            )
                        },
                    },
                    {
                        'id': 1, 'type': 'SEND',
                        'data': {
                            **GetMessage(
                                **async_loop(message_crud.get(self.session, id=1)).__dict__,
                            ).dict(),
                            'created_at': f'{async_loop(message_crud.get(self.session, id=1)).created_at}Z'.replace(
                                ' ',
                                'T'
                            )
                        },
                    }
                ]
            )

        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.get(f'{self.url}/notifications/', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), [])

        async_loop(message_crud.create(self.session, sender_id=2, msg='Hello world!', dialogue_id=1))
        async_loop(
            notification_crud.create(
                self.session,
                sender_id=2,
                recipient_id=1,
                message_id=3,
            )
        )
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 3)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 3)

        with mock.patch('app.permission.permission', return_value=2) as _:
            response = self.client.get(f'{self.url}/notifications/', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(), [
                    {
                        'id': 2,
                        'type': 'SEND',
                        'data': {
                            **GetMessage(
                                **async_loop(message_crud.get(self.session, id=2)).__dict__,
                            ).dict(),
                            'created_at': f'{async_loop(message_crud.get(self.session, id=2)).created_at}Z'.replace(
                                ' ',
                                'T'
                            )
                        },
                    },
                    {
                        'id': 1, 'type': 'SEND',
                        'data': {
                            **GetMessage(
                                **async_loop(message_crud.get(self.session, id=1)).__dict__,
                            ).dict(),
                            'created_at': f'{async_loop(message_crud.get(self.session, id=1)).created_at}Z'.replace(
                                ' ',
                                'T'
                            )
                        },
                    }
                ]
            )

        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.get(f'{self.url}/notifications/', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(), [
                    {
                        'id': 3,
                        'type': 'SEND',
                        'data': {
                            **GetMessage(
                                **async_loop(message_crud.get(self.session, id=3)).__dict__,
                            ).dict(),
                            'created_at': f'{async_loop(message_crud.get(self.session, id=3)).created_at}Z'.replace(
                                ' ',
                                'T'
                            )
                        },
                    }
                ]
            )

        async_loop(dialogue_crud.create(self.session, users_ids='3_2'))
        async_loop(message_crud.create(self.session, sender_id=3, msg='Hello world!', dialogue_id=2))
        async_loop(
            notification_crud.create(
                self.session,
                sender_id=3,
                recipient_id=2,
                message_id=4,
            )
        )
        self.assertEqual(len(async_loop(dialogue_crud.all(self.session))), 2)
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 4)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 4)

        with mock.patch('app.permission.permission', return_value=2) as _:
            response = self.client.get(f'{self.url}/notifications/', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(), [
                    {
                        'id': 4,
                        'type': 'SEND',
                        'data': {
                            **GetMessage(
                                **async_loop(message_crud.get(self.session, id=4)).__dict__,
                            ).dict(),
                            'created_at': f'{async_loop(message_crud.get(self.session, id=4)).created_at}Z'.replace(
                                ' ',
                                'T'
                            )
                        },
                    },
                    {
                        'id': 2,
                        'type': 'SEND',
                        'data': {
                            **GetMessage(
                                **async_loop(message_crud.get(self.session, id=2)).__dict__,
                            ).dict(),
                            'created_at': f'{async_loop(message_crud.get(self.session, id=2)).created_at}Z'.replace(
                                ' ',
                                'T'
                            )
                        },
                    },
                ]
            )
        self.assertEqual(len(async_loop(notification_crud.filter(self.session, recipient_id=2))), 3)
        self.assertEqual(len(response.json()), 2)

        # Get
        with mock.patch('app.permission.permission', return_value=2) as _:
            response = self.client.get(f'{self.url}/notifications/1', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(), {
                    'id': 1, 'type': 'SEND',
                    'data': {
                        **GetMessage(
                            **async_loop(message_crud.get(self.session, id=1)).__dict__,
                        ).dict(),
                        'created_at': f'{async_loop(message_crud.get(self.session, id=1)).created_at}Z'.replace(
                            ' ',
                            'T'
                        )
                    },
                }
            )

        with mock.patch('app.permission.permission', return_value=2) as _:
            response = self.client.get(f'{self.url}/notifications/3', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'You not owner this notification'})

        with mock.patch('app.permission.permission', return_value=2) as _:
            response = self.client.get(f'{self.url}/notifications/143', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Notification not found'})

        # View only 1
        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.delete(f'{self.url}/notifications/1', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'You not owner this notification'})

        # View all (delete)
        with mock.patch('app.permission.permission', return_value=2) as _:
            response = self.client.delete(f'{self.url}/notifications/', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Notifications has been viewed. You have more notifications'})

        self.assertEqual(len(async_loop(notification_crud.filter(self.session, recipient_id=2))), 1)
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 4)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 2)

        self.assertEqual(async_loop(notification_crud.exist(self.session, id=4)), False)
        self.assertEqual(async_loop(notification_crud.exist(self.session, id=3)), True)
        self.assertEqual(async_loop(notification_crud.exist(self.session, id=2)), False)
        self.assertEqual(async_loop(notification_crud.exist(self.session, id=1)), True)

        with mock.patch('app.permission.permission', return_value=2) as _:
            response = self.client.delete(f'{self.url}/notifications/', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(),
                {'msg': 'Notifications has been viewed. You don\'t have more notifications'}
            )

        self.assertEqual(len(async_loop(notification_crud.filter(self.session, recipient_id=2))), 0)
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 4)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 1)

        self.assertEqual(async_loop(notification_crud.exist(self.session, id=4)), False)
        self.assertEqual(async_loop(notification_crud.exist(self.session, id=3)), True)
        self.assertEqual(async_loop(notification_crud.exist(self.session, id=2)), False)
        self.assertEqual(async_loop(notification_crud.exist(self.session, id=1)), False)

        # View only 1
        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.delete(f'{self.url}/notifications/3', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Notification has been viewed'})
        self.assertEqual(async_loop(notification_crud.exist(self.session, id=3)), False)
        self.assertEqual(len(async_loop(notification_crud.all(self.session))), 0)

        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.delete(f'{self.url}/notifications/143', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Notification not found'})
