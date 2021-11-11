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

            response = self.client.get(f'{self.url}/feedbacks/?page=143&page_size=1', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Results not found'})
