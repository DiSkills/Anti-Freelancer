from unittest import TestCase, mock

from app.crud import feedback_crud
from config import NEW
from tests import BaseTest, async_loop


class FeedbackTestCase(BaseTest, TestCase):

    def test_feedback(self):
        self.assertEqual(len(async_loop(feedback_crud.all(self.session))), 0)

        headers = {'Authorization': 'Bearer Token'}

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
