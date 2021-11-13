from unittest import TestCase, mock

from app.crud import feedback_crud
from config import NEW, SERVER_OTHER_BACKEND, API
from tests import BaseTest, async_loop


class FeedbackTestCase(BaseTest, TestCase):

    def test_feedback(self):
        self.assertEqual(len(async_loop(feedback_crud.all(self.session))), 0)

        headers = {'Authorization': 'Bearer Token'}

        # Create
        with mock.patch('app.permission.permission', return_value=3) as _:
            response = self.client.post(f'{self.url}/feedbacks/', headers=headers, json={'text': 'Hello world!'})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json(), {'msg': 'Thanks for your feedback. Feedback has been created!'})

        self.assertEqual(len(async_loop(feedback_crud.all(self.session))), 1)
        self.assertEqual(async_loop(feedback_crud.get(self.session, id=1)).user_id, 3)
        self.assertEqual(async_loop(feedback_crud.get(self.session, id=1)).status, NEW)

        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.post(f'{self.url}/feedbacks/', headers=headers, json={'text': 'Hello world!'})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json(), {'msg': 'Thanks for your feedback. Feedback has been created!'})

        self.assertEqual(len(async_loop(feedback_crud.all(self.session))), 2)
        self.assertEqual(async_loop(feedback_crud.get(self.session, id=2)).user_id, 1)
        self.assertEqual(async_loop(feedback_crud.get(self.session, id=2)).status, NEW)

        # Get all
        self.assertEqual(len(async_loop(feedback_crud.all(self.session))), 2)

        with mock.patch(
                'app.requests.get_users_request',
                return_value={'1': self.get_new_user(1), '3': self.get_new_user(3)}
        ) as _:
            with mock.patch('app.permission.permission', return_value=1) as _:
                response = self.client.get(f'{self.url}/feedbacks/?page=1&page_size=1', headers=headers)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()['results']), 1)
                self.assertEqual(
                    response.json()['next'],
                    f'{SERVER_OTHER_BACKEND}{API}/feedbacks/?page=2&page_size=1'
                )
                self.assertEqual(response.json()['page'], 1)
                self.assertEqual(response.json()['previous'], None)
                self.assertEqual(response.json()['results'][0]['id'], 2)
                self.assertEqual(response.json()['results'][0]['user'], self.get_new_user(1))

                response = self.client.get(f'{self.url}/feedbacks/?page=2&page_size=1', headers=headers)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()['results']), 1)
                self.assertEqual(
                    response.json()['previous'],
                    f'{SERVER_OTHER_BACKEND}{API}/feedbacks/?page=1&page_size=1'
                )
                self.assertEqual(response.json()['page'], 2)
                self.assertEqual(response.json()['next'], None)
                self.assertEqual(response.json()['results'][0]['id'], 1)
                self.assertEqual(response.json()['results'][0]['user'], self.get_new_user(3))

                response = self.client.get(f'{self.url}/feedbacks/?page=143&page_size=1', headers=headers)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'Results not found'})

        # Get
        with mock.patch('app.permission.permission', return_value=1) as _:
            with mock.patch(
                    'app.requests.get_user_request',
                    return_value=self.get_new_user(3)
            ) as _:
                response = self.client.get(f'{self.url}/feedbacks/1', headers=headers)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.json(),
                    {
                        'id': 1, 'status': False, 'text': 'Hello world!', 'user': self.get_new_user(3),
                        'created_at': f'{async_loop(feedback_crud.get(self.session, id=1)).created_at}Z'.replace(
                            ' ',
                            'T'
                        )
                    }
                )

                response = self.client.get(f'{self.url}/feedbacks/143', headers=headers)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'Feedback not found'})

            with mock.patch(
                    'app.requests.get_user_request',
                    return_value=self.get_new_user(1)
            ) as _:
                response = self.client.get(f'{self.url}/feedbacks/2', headers=headers)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.json(),
                    {
                        'id': 2, 'status': False, 'text': 'Hello world!', 'user': self.get_new_user(1),
                        'created_at': f'{async_loop(feedback_crud.get(self.session, id=2)).created_at}Z'.replace(
                            ' ',
                            'T'
                        )
                    }
                )

        # Update
        with mock.patch('app.permission.permission', return_value=1) as _:
            with mock.patch(
                    'app.requests.get_user_request',
                    return_value=self.get_new_user(3)
            ) as _:
                response = self.client.get(f'{self.url}/feedbacks/1', headers=headers)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.json(),
                    {
                        'id': 1, 'status': False, 'text': 'Hello world!', 'user': self.get_new_user(3),
                        'created_at': f'{async_loop(feedback_crud.get(self.session, id=1)).created_at}Z'.replace(
                            ' ',
                            'T'
                        )
                    }
                )
                old = response.json()

                response = self.client.put(
                    f'{self.url}/feedbacks/1',
                    headers=headers,
                    json={'status': True, 'text': 'Hello python!'}
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.json(),
                    {
                        'id': 1, 'status': True, 'text': 'Hello python!', 'user': self.get_new_user(3),
                        'created_at': f'{async_loop(feedback_crud.get(self.session, id=1)).created_at}Z'.replace(
                            ' ',
                            'T'
                        )
                    }
                )
                self.assertNotEqual(response.json(), old)

                response = self.client.get(f'{self.url}/feedbacks/1', headers=headers)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.json(),
                    {
                        'id': 1, 'status': True, 'text': 'Hello python!', 'user': self.get_new_user(3),
                        'created_at': f'{async_loop(feedback_crud.get(self.session, id=1)).created_at}Z'.replace(
                            ' ',
                            'T'
                        )
                    }
                )

                response = self.client.put(
                    f'{self.url}/feedbacks/143',
                    json={'status': False, 'text': 'GG'},
                    headers=headers,
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'Feedback not found'})

        # Sort
        self.assertEqual(len(async_loop(feedback_crud.all(self.session))), 2)

        # Desc
        with mock.patch(
                'app.requests.get_users_request',
                return_value={'1': self.get_new_user(1), '3': self.get_new_user(3)}
        ) as _:
            with mock.patch('app.permission.permission', return_value=1) as _:
                response = self.client.get(
                    f'{self.url}/feedbacks/sort?page=1&page_size=1&desc=true',
                    headers=headers
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()['results']), 1)
                self.assertEqual(
                    response.json()['next'],
                    f'{SERVER_OTHER_BACKEND}{API}/feedbacks/sort?page=2&page_size=1&desc=True'
                )
                self.assertEqual(response.json()['page'], 1)
                self.assertEqual(response.json()['previous'], None)
                self.assertEqual(response.json()['results'][0]['id'], 1)
                self.assertEqual(response.json()['results'][0]['user'], self.get_new_user(3))

                response = self.client.get(
                    f'{self.url}/feedbacks/sort?page=2&page_size=1&desc=True',
                    headers=headers
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()['results']), 1)
                self.assertEqual(response.json()['next'], None)
                self.assertEqual(response.json()['page'], 2)
                self.assertEqual(
                    response.json()['previous'],
                    f'{SERVER_OTHER_BACKEND}{API}/feedbacks/sort?page=1&page_size=1&desc=True'
                )
                self.assertEqual(response.json()['results'][0]['id'], 2)
                self.assertEqual(response.json()['results'][0]['user'], self.get_new_user(1))

                response = self.client.get(
                    f'{self.url}/feedbacks/sort?page=3&page_size=1&desc=True',
                    headers=headers
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'Results not found'})

                response = self.client.get(
                    f'{self.url}/feedbacks/sort?page=1&page_size=11&desc=True',
                    headers=headers
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()['results']), 2)
                self.assertEqual(response.json()['results'][0]['id'], 1)
                self.assertEqual(response.json()['results'][1]['id'], 2)

        # ASC
        with mock.patch(
                'app.requests.get_users_request',
                return_value={'1': self.get_new_user(1), '3': self.get_new_user(3)}
        ) as _:
            with mock.patch('app.permission.permission', return_value=1) as _:
                response = self.client.get(
                    f'{self.url}/feedbacks/sort?page=1&page_size=1&desc=false',
                    headers=headers
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()['results']), 1)
                self.assertEqual(
                    response.json()['next'],
                    f'{SERVER_OTHER_BACKEND}{API}/feedbacks/sort?page=2&page_size=1&desc=False'
                )
                self.assertEqual(response.json()['page'], 1)
                self.assertEqual(response.json()['previous'], None)
                self.assertEqual(response.json()['results'][0]['id'], 2)
                self.assertEqual(response.json()['results'][0]['user'], self.get_new_user(1))

                response = self.client.get(
                    f'{self.url}/feedbacks/sort?page=2&page_size=1&desc=False',
                    headers=headers
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()['results']), 1)
                self.assertEqual(response.json()['next'], None)
                self.assertEqual(response.json()['page'], 2)
                self.assertEqual(
                    response.json()['previous'],
                    f'{SERVER_OTHER_BACKEND}{API}/feedbacks/sort?page=1&page_size=1&desc=False'
                )
                self.assertEqual(response.json()['results'][0]['id'], 1)
                self.assertEqual(response.json()['results'][0]['user'], self.get_new_user(3))

                response = self.client.get(
                    f'{self.url}/feedbacks/sort?page=3&page_size=1&desc=False',
                    headers=headers
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'Results not found'})

                response = self.client.get(
                    f'{self.url}/feedbacks/sort?page=1&page_size=11&desc=False',
                    headers=headers
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()['results']), 2)
                self.assertEqual(response.json()['results'][0]['id'], 2)
                self.assertEqual(response.json()['results'][1]['id'], 1)

        # Delete
        self.assertEqual(len(async_loop(feedback_crud.all(self.session))), 2)
        self.assertEqual(async_loop(feedback_crud.exist(self.session, id=1)), True)
        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.delete(f'{self.url}/feedbacks/1', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Feedback has been deleted'})
            self.assertEqual(len(async_loop(feedback_crud.all(self.session))), 1)
            self.assertEqual(async_loop(feedback_crud.exist(self.session, id=1)), False)

            response = self.client.delete(f'{self.url}/feedbacks/143', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Feedback not found'})
            self.assertEqual(len(async_loop(feedback_crud.all(self.session))), 1)
