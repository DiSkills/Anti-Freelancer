import datetime
from unittest import TestCase, mock

from app.crud import super_category_crud, sub_category_crud, job_crud
from tests import BaseTest, async_loop


class JobsTestCase(BaseTest, TestCase):

    def test_jobs(self):
        with mock.patch('app.permission.permission', return_value={'user_id': 1}) as _:
            headers = {'Authorization': 'Bearer Token'}

            self.assertEqual(len(async_loop(job_crud.all(self.session))), 0)

            self.client.post(f'{self.url}/categories/', json={'name': 'Programming'}, headers=headers)
            self.client.post(
                f'{self.url}/categories/', json={'name': 'Python', 'super_category_id': 1}, headers=headers,
            )

            # Create
            now = datetime.datetime.utcnow()
            response = self.client.post(f'{self.url}/jobs/', headers=headers, json={
                'title': 'Web site',
                'description': 'Web site',
                'price': 5000,
                'order_date': f'{now}Z',
                'category_id': 1,
            })
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json(), {
                'id': 1,
                'title': 'Web site',
                'description': 'Web site',
                'price': 5000,
                'order_date': f'{now}Z'.replace(' ', 'T'),
                'category_id': 1,
            })
            self.assertEqual(len(async_loop(job_crud.all(self.session))), 1)

            response = self.client.post(f'{self.url}/jobs/', headers=headers, json={
                'title': 'Web site',
                'description': 'Web site',
                'price': 5000,
                'order_date': f'{now}Z',
                'category_id': 143,
            })
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Category not found'})

            response = self.client.post(f'{self.url}/jobs/', headers=headers, json={
                'title': 'Web site',
                'description': 'Web site',
                'price': 0,
                'order_date': f'{now}Z',
                'category_id': 143,
            })
            self.assertEqual(response.status_code, 422)
            self.assertEqual(response.json()['detail'][0]['msg'], 'The price must be at least 0')

            response = self.client.post(f'{self.url}/jobs/', headers=headers, json={
                'title': 'Web site',
                'description': 'Web site',
                'price': -5,
                'order_date': f'{now}Z',
                'category_id': 143,
            })
            self.assertEqual(response.status_code, 422)
            self.assertEqual(response.json()['detail'][0]['msg'], 'The price must be at least 0')

            response = self.client.post(f'{self.url}/jobs/', headers=headers, json={
                'title': 'Web site',
                'description': 'Web site',
                'price': 5000,
                'order_date': f'{now - datetime.timedelta(days=2)}Z',
                'category_id': 143,
            })
            self.assertEqual(response.status_code, 422)
            self.assertEqual(response.json()['detail'][0]['msg'], 'Date can\'t be past')

            self.assertEqual(len(async_loop(job_crud.all(self.session))), 1)
