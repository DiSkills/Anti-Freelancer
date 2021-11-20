from unittest import TestCase, mock

from app.crud import review_crud
from app.review.schemas import GetReview
from config import SERVER_OTHER_BACKEND, API
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

        # Get
        response = self.client.get(f'{self.url}/reviews/1')
        self.assertEqual(response.status_code, 200)
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

        response = self.client.get(f'{self.url}/reviews/143')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Review not found'})

        # Update
        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.put(
                f'{self.url}/reviews/1',
                headers=headers,
                json={'appraisal': 3, 'text': 'Hello world!'}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(),
                {
                    'appraisal': 3,
                    'created_at': f'{async_loop(review_crud.get(self.session, id=1)).created_at}Z'.replace(' ', 'T'),
                    'id': 1,
                    'text': 'Hello world!',
                    'user_id': 1,
                }
            )

        response = self.client.get(f'{self.url}/reviews/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'appraisal': 3,
                'created_at': f'{async_loop(review_crud.get(self.session, id=1)).created_at}Z'.replace(' ', 'T'),
                'id': 1,
                'text': 'Hello world!',
                'user_id': 1,
            }
        )

        # Bad
        with mock.patch('app.permission.permission', return_value=143) as _:
            response = self.client.put(
                f'{self.url}/reviews/1',
                headers=headers,
                json={'appraisal': 3, 'text': 'Hello world!'}
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'User not owner this review'})

            response = self.client.put(
                f'{self.url}/reviews/143',
                headers=headers,
                json={'appraisal': 3, 'text': 'Hello world!'}
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Review not found'})

        # Update (admin)
        with mock.patch('app.permission.permission', return_value=143) as _:
            response = self.client.put(
                f'{self.url}/reviews/admin/1',
                headers=headers,
                json={'appraisal': 5, 'text': 'Hello python!'}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(),
                {
                    'appraisal': 5,
                    'created_at': f'{async_loop(review_crud.get(self.session, id=1)).created_at}Z'.replace(' ', 'T'),
                    'id': 1,
                    'text': 'Hello python!',
                    'user_id': 1,
                }
            )

            response = self.client.put(
                f'{self.url}/reviews/admin/143',
                headers=headers,
                json={'appraisal': 5, 'text': 'Hello python!'}
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Review not found'})

    def test_reviews_paginate(self):
        headers = {'Authorization': 'Bearer Token'}

        response = self.client.get(f'{self.url}/reviews/?page=1&page_size=1&sort=desc')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Results not found'})

        self.assertEqual(len(async_loop(review_crud.all(self.session))), 0)
        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.post(
                f'{self.url}/reviews/',
                headers=headers,
                json={'appraisal': 5, 'text': 'Good site!'}
            )
            self.assertEqual(response.status_code, 201)

        with mock.patch('app.permission.permission', return_value=2) as _:
            response = self.client.post(
                f'{self.url}/reviews/',
                headers=headers,
                json={'appraisal': 3, 'text': 'Good site!'}
            )
            self.assertEqual(response.status_code, 201)

        with mock.patch('app.permission.permission', return_value=3) as _:
            response = self.client.post(
                f'{self.url}/reviews/',
                headers=headers,
                json={'appraisal': 5, 'text': 'Good site!'}
            )
            self.assertEqual(response.status_code, 201)

        # Get all
        # ASC
        response = self.client.get(f'{self.url}/reviews/?page=1&page_size=1&sort=asc')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'next': f'{SERVER_OTHER_BACKEND}{API}/reviews/?page=2&page_size=1&sort=asc',
                'page': 1,
                'previous': None,
                'results': [
                    GetReview(**async_loop(review_crud.get(self.session, id=1)).__dict__).dict()
                ],
            }
        )

        response = self.client.get(f'{self.url}/reviews/?page=2&page_size=1&sort=asc')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'next': f'{SERVER_OTHER_BACKEND}{API}/reviews/?page=3&page_size=1&sort=asc',
                'page': 2,
                'previous': f'{SERVER_OTHER_BACKEND}{API}/reviews/?page=1&page_size=1&sort=asc',
                'results': [
                    GetReview(**async_loop(review_crud.get(self.session, id=2)).__dict__).dict()
                ],
            }
        )

        response = self.client.get(f'{self.url}/reviews/?page=3&page_size=1&sort=asc')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'previous': f'{SERVER_OTHER_BACKEND}{API}/reviews/?page=2&page_size=1&sort=asc',
                'page': 3,
                'next': None,
                'results': [
                    GetReview(**async_loop(review_crud.get(self.session, id=3)).__dict__).dict()
                ],
            }
        )

        # DESC
        response = self.client.get(f'{self.url}/reviews/?page=1&page_size=1&sort=desc')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'next': f'{SERVER_OTHER_BACKEND}{API}/reviews/?page=2&page_size=1&sort=desc',
                'page': 1,
                'previous': None,
                'results': [
                    GetReview(**async_loop(review_crud.get(self.session, id=3)).__dict__).dict()
                ],
            }
        )

        response = self.client.get(f'{self.url}/reviews/?page=2&page_size=1&sort=desc')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'next': f'{SERVER_OTHER_BACKEND}{API}/reviews/?page=3&page_size=1&sort=desc',
                'page': 2,
                'previous': f'{SERVER_OTHER_BACKEND}{API}/reviews/?page=1&page_size=1&sort=desc',
                'results': [
                    GetReview(**async_loop(review_crud.get(self.session, id=2)).__dict__).dict()
                ],
            }
        )

        response = self.client.get(f'{self.url}/reviews/?page=3&page_size=1&sort=desc')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'previous': f'{SERVER_OTHER_BACKEND}{API}/reviews/?page=2&page_size=1&sort=desc',
                'page': 3,
                'next': None,
                'results': [
                    GetReview(**async_loop(review_crud.get(self.session, id=1)).__dict__).dict()
                ],
            }
        )

        # ASC appraisal
        response = self.client.get(f'{self.url}/reviews/?page=1&page_size=1&sort=asc_appraisal')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'next': f'{SERVER_OTHER_BACKEND}{API}/reviews/?page=2&page_size=1&sort=asc_appraisal',
                'page': 1,
                'previous': None,
                'results': [
                    GetReview(**async_loop(review_crud.get(self.session, id=2)).__dict__).dict()
                ],
            }
        )

        response = self.client.get(f'{self.url}/reviews/?page=2&page_size=1&sort=asc_appraisal')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'next': f'{SERVER_OTHER_BACKEND}{API}/reviews/?page=3&page_size=1&sort=asc_appraisal',
                'page': 2,
                'previous': f'{SERVER_OTHER_BACKEND}{API}/reviews/?page=1&page_size=1&sort=asc_appraisal',
                'results': [
                    GetReview(**async_loop(review_crud.get(self.session, id=1)).__dict__).dict()
                ],
            }
        )

        response = self.client.get(f'{self.url}/reviews/?page=3&page_size=1&sort=asc_appraisal')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'previous': f'{SERVER_OTHER_BACKEND}{API}/reviews/?page=2&page_size=1&sort=asc_appraisal',
                'page': 3,
                'next': None,
                'results': [
                    GetReview(**async_loop(review_crud.get(self.session, id=3)).__dict__).dict()
                ],
            }
        )

        # DESC appraisal
        response = self.client.get(f'{self.url}/reviews/?page=1&page_size=1&sort=desc_appraisal')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'next': f'{SERVER_OTHER_BACKEND}{API}/reviews/?page=2&page_size=1&sort=desc_appraisal',
                'page': 1,
                'previous': None,
                'results': [
                    GetReview(**async_loop(review_crud.get(self.session, id=1)).__dict__).dict()
                ],
            }
        )

        response = self.client.get(f'{self.url}/reviews/?page=2&page_size=1&sort=desc_appraisal')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'next': f'{SERVER_OTHER_BACKEND}{API}/reviews/?page=3&page_size=1&sort=desc_appraisal',
                'page': 2,
                'previous': f'{SERVER_OTHER_BACKEND}{API}/reviews/?page=1&page_size=1&sort=desc_appraisal',
                'results': [
                    GetReview(**async_loop(review_crud.get(self.session, id=3)).__dict__).dict()
                ],
            }
        )

        response = self.client.get(f'{self.url}/reviews/?page=3&page_size=1&sort=desc_appraisal')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'previous': f'{SERVER_OTHER_BACKEND}{API}/reviews/?page=2&page_size=1&sort=desc_appraisal',
                'page': 3,
                'next': None,
                'results': [
                    GetReview(**async_loop(review_crud.get(self.session, id=2)).__dict__).dict()
                ],
            }
        )

        # Bad
        response = self.client.get(f'{self.url}/reviews/?page=1&page_size=1&sort=DESC')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Sort not found'})

        response = self.client.get(f'{self.url}/reviews/?page=143&page_size=1&sort=desc_appraisal')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Results not found'})
