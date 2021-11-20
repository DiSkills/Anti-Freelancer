from unittest import TestCase, mock

from app.crud import review_crud
from tests import BaseTest, async_loop


class ReviewTestCase(BaseTest, TestCase):

    def test_review(self):
        headers = {'Authorization': 'Bearer Token'}

        self.assertEqual(len(async_loop(review_crud.all(self.session))), 0)

        # Create
        # Bad
        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.post(
                f'{self.url}/reviews/',
                headers=headers,
                json={'appraisal': 9, 'text': 'Good site!'}
            )
            self.assertEqual(response.status_code, 422)
            self.assertEqual(response.json()['detail'][0]['msg'], 'ensure this value is less than 6')
            self.assertEqual(len(async_loop(review_crud.all(self.session))), 0)

            response = self.client.post(
                f'{self.url}/reviews/',
                headers=headers,
                json={'appraisal': 0, 'text': 'Good site!'}
            )
            self.assertEqual(response.status_code, 422)
            self.assertEqual(response.json()['detail'][0]['msg'], 'ensure this value is greater than 0')
            self.assertEqual(len(async_loop(review_crud.all(self.session))), 0)

            response = self.client.post(
                f'{self.url}/reviews/',
                headers=headers,
                json={'appraisal': -3, 'text': 'Good site!'}
            )
            self.assertEqual(response.status_code, 422)
            self.assertEqual(response.json()['detail'][0]['msg'], 'ensure this value is greater than 0')
            self.assertEqual(len(async_loop(review_crud.all(self.session))), 0)

        # Good
        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.post(
                f'{self.url}/reviews/',
                headers=headers,
                json={'appraisal': 5, 'text': 'Good site!'}
            )
            self.assertEqual(response.status_code, 201)
            self.assertEqual(
                response.json(),
                {
                    'appraisal': 5,
                    'created_at': f'{async_loop(review_crud.get(self.session, id=1)).created_at}Z'.replace(' ', 'T'),
                    'id': 1,
                    'text': 'Good site!',
                    'user_id': 1,
                }
            )
            self.assertEqual(len(async_loop(review_crud.all(self.session))), 1)

            response = self.client.post(
                f'{self.url}/reviews/',
                headers=headers,
                json={'appraisal': 5, 'text': 'Good site!'}
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Review exist'})
            self.assertEqual(len(async_loop(review_crud.all(self.session))), 1)
