import datetime
import os
from unittest import TestCase, mock

from fastapi import UploadFile

from app.crud import job_crud, attachment_crud
from config import SERVER_MAIN_BACKEND, MEDIA_ROOT, API
from tests import BaseTest, async_loop


class JobsTestCase(BaseTest, TestCase):

    def test_jobs(self):
        with mock.patch('app.permission.permission', return_value=1) as _:
            headers = {'Authorization': 'Bearer Token'}

            self.assertEqual(len(async_loop(job_crud.all(self.session))), 0)

            self.client.post(f'{self.url}/categories/', json={'name': 'Programming'}, headers=headers)
            self.client.post(
                f'{self.url}/categories/', json={'name': 'Python', 'super_category_id': 1}, headers=headers,
            )
            self.client.post(
                f'{self.url}/categories/', json={'name': 'FastAPI', 'super_category_id': 1}, headers=headers,
            )

            # Create
            now = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
            response = self.client.post(
                f'{self.url}/jobs/', headers=headers, json={
                    'title': 'Web site',
                    'description': 'Web site',
                    'price': 5000,
                    'order_date': f'{now}Z',
                    'category_id': 1,
                }
            )
            self.assertEqual(response.status_code, 201)
            self.assertEqual(
                response.json(), {
                    'id': 1,
                    'customer_id': 1,
                    'completed': False,
                    'title': 'Web site',
                    'executor_id': None,
                    'description': 'Web site',
                    'price': 5000,
                    'order_date': f'{now}Z'.replace(' ', 'T'),
                    'category_id': 1,
                }
            )
            self.assertEqual(len(async_loop(job_crud.all(self.session))), 1)

            response = self.client.post(
                f'{self.url}/jobs/', headers=headers, json={
                    'title': 'Web site',
                    'description': 'Web site',
                    'price': 5000,
                    'order_date': f'{now}Z',
                    'category_id': 143,
                }
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Category not found'})

            response = self.client.post(
                f'{self.url}/jobs/', headers=headers, json={
                    'title': 'Web site',
                    'description': 'Web site',
                    'price': 0,
                    'order_date': f'{now}Z',
                    'category_id': 143,
                }
            )
            self.assertEqual(response.status_code, 422)
            self.assertEqual(response.json()['detail'][0]['msg'], 'The price must be at least 0')

            response = self.client.post(
                f'{self.url}/jobs/', headers=headers, json={
                    'title': 'Web site',
                    'description': 'Web site',
                    'price': -5,
                    'order_date': f'{now}Z',
                    'category_id': 143,
                }
            )
            self.assertEqual(response.status_code, 422)
            self.assertEqual(response.json()['detail'][0]['msg'], 'The price must be at least 0')

            response = self.client.post(
                f'{self.url}/jobs/', headers=headers, json={
                    'title': 'Web site',
                    'description': 'Web site',
                    'price': 5000,
                    'order_date': f'{now - datetime.timedelta(days=2)}Z',
                    'category_id': 143,
                }
            )
            self.assertEqual(response.status_code, 422)
            self.assertEqual(response.json()['detail'][0]['msg'], 'Date can\'t be past')

            self.assertEqual(len(async_loop(job_crud.all(self.session))), 1)

            # Get all without completed
            self.client.post(
                f'{self.url}/jobs/', headers=headers, json={
                    'title': 'Django',
                    'description': 'Web site',
                    'price': 5000,
                    'order_date': f'{now}Z',
                    'category_id': 2,
                }
            )
            self.client.post(
                f'{self.url}/jobs/', headers=headers, json={
                    'title': 'Python',
                    'description': 'Web site',
                    'price': 5000,
                    'order_date': f'{now}Z',
                    'category_id': 2,
                }
            )
            self.client.post(
                f'{self.url}/jobs/', headers=headers, json={
                    'title': 'FastAPI',
                    'description': 'Web site',
                    'price': 5000,
                    'order_date': f'{now}Z',
                    'category_id': 1,
                }
            )

            response = self.client.get(f'{self.url}/jobs/?page=1&page_size=1')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()['next'], f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/?page=2&page_size=1'
            )
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(len(response.json()['results']), 1)

            response = self.client.get(f'{self.url}/jobs/?page=2&page_size=1')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()['next'], f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/?page=3&page_size=1'
            )
            self.assertEqual(
                response.json()['previous'], f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/?page=1&page_size=1'
            )
            self.assertEqual(response.json()['page'], 2)
            self.assertEqual(len(response.json()['results']), 1)

            response = self.client.get(f'{self.url}/jobs/?page=4&page_size=1')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()['next'], None
            )
            self.assertEqual(
                response.json()['previous'], f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/?page=3&page_size=1'
            )
            self.assertEqual(response.json()['page'], 4)
            self.assertEqual(len(response.json()['results']), 1)

            response = self.client.get(f'{self.url}/jobs/?page=1&page_size=10')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(len(response.json()['results']), 4)

            response = self.client.get(f'{self.url}/jobs/?page=143&page_size=10')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Results not found'})

            # Get from categories without completed
            response = self.client.get(f'{self.url}/jobs/category?page=1&page_size=1&category_id=1')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()['next'],
                f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/category?page=2&page_size=1&category_id=1'
            )
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(len(response.json()['results']), 1)
            self.assertEqual(response.json()['results'][0]['id'], 4)

            response = self.client.get(f'{self.url}/jobs/category?page=2&page_size=1&category_id=1')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(
                response.json()['previous'],
                f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/category?page=1&page_size=1&category_id=1'
            )
            self.assertEqual(response.json()['page'], 2)
            self.assertEqual(len(response.json()['results']), 1)
            self.assertEqual(response.json()['results'][0]['id'], 1)

            response = self.client.get(f'{self.url}/jobs/category?page=1&page_size=2&category_id=1')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(len(response.json()['results']), 2)
            self.assertEqual(response.json()['results'][0]['id'], 4)
            self.assertEqual(response.json()['results'][1]['id'], 1)

            # Category 2
            response = self.client.get(f'{self.url}/jobs/category?page=1&page_size=1&category_id=2')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()['next'],
                f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/category?page=2&page_size=1&category_id=2'
            )
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(len(response.json()['results']), 1)
            self.assertEqual(response.json()['results'][0]['id'], 3)

            response = self.client.get(f'{self.url}/jobs/category?page=2&page_size=1&category_id=2')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(
                response.json()['previous'],
                f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/category?page=1&page_size=1&category_id=2'
            )
            self.assertEqual(response.json()['page'], 2)
            self.assertEqual(len(response.json()['results']), 1)
            self.assertEqual(response.json()['results'][0]['id'], 2)

            response = self.client.get(f'{self.url}/jobs/category?page=1&page_size=2&category_id=2')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(len(response.json()['results']), 2)
            self.assertEqual(response.json()['results'][0]['id'], 3)
            self.assertEqual(response.json()['results'][1]['id'], 2)

            response = self.client.get(f'{self.url}/jobs/category?page=2&page_size=2&category_id=1')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Results not found'})

            response = self.client.get(f'{self.url}/jobs/category?page=2&page_size=2&category_id=2')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Results not found'})

            response = self.client.get(f'{self.url}/jobs/category?page=2&page_size=2&category_id=143')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Results not found'})

            # Search without completed
            response = self.client.get(f'{self.url}/jobs/search?page=1&page_size=1&search=web')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()['next'],
                f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/search?page=2&page_size=1&search=web'
            )
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(response.json()['results'][0]['id'], 4)
            self.assertEqual(len(response.json()['results']), 1)

            response = self.client.get(f'{self.url}/jobs/search?page=2&page_size=1&search=web')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()['next'],
                f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/search?page=3&page_size=1&search=web'
            )
            self.assertEqual(
                response.json()['previous'],
                f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/search?page=1&page_size=1&search=web'
            )
            self.assertEqual(response.json()['page'], 2)
            self.assertEqual(response.json()['results'][0]['id'], 3)
            self.assertEqual(len(response.json()['results']), 1)

            response = self.client.get(f'{self.url}/jobs/search?page=4&page_size=1&search=web')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(
                response.json()['previous'],
                f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/search?page=3&page_size=1&search=web'
            )
            self.assertEqual(response.json()['page'], 4)
            self.assertEqual(response.json()['results'][0]['id'], 1)
            self.assertEqual(len(response.json()['results']), 1)

            response = self.client.get(f'{self.url}/jobs/search?page=1&page_size=4&search=web')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(response.json()['results'][0]['id'], 4)
            self.assertEqual(len(response.json()['results']), 4)

            response = self.client.get(f'{self.url}/jobs/search?page=1&page_size=1&search=FastApi')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(response.json()['results'][0]['id'], 4)
            self.assertEqual(len(response.json()['results']), 1)

            response = self.client.get(f'{self.url}/jobs/search?page=1&page_size=1&search=Python')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(response.json()['results'][0]['id'], 3)
            self.assertEqual(len(response.json()['results']), 1)

            response = self.client.get(f'{self.url}/jobs/search?page=2&page_size=1&search=Python')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Results not found'})

            response = self.client.get(f'{self.url}/jobs/search?page=1&page_size=1&search=djangO')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(response.json()['results'][0]['id'], 2)
            self.assertEqual(len(response.json()['results']), 1)

            response = self.client.get(f'{self.url}/jobs/search?page=1&page_size=1&search=Hello World!')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Results not found'})

            # Get job
            with mock.patch('app.permission.permission', return_value=2) as _:
                headers = {'Authorization': 'Bearer Token'}
                self.client.post(
                    f'{self.url}/jobs/', headers=headers, json={
                        'title': 'PyCharm',
                        'description': 'Web site',
                        'price': 5000,
                        'order_date': f'{now}Z',
                        'category_id': 1,
                    }
                )
            response = self.client.get(f'{self.url}/jobs/1')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(), {
                    'attachments': [],
                    'executor_id': None,
                    'id': 1,
                    'title': 'Web site',
                    'description': 'Web site',
                    'price': 5000,
                    'order_date': f'{now}Z'.replace(' ', 'T'),
                    'category_id': 1,
                    'customer_id': 1,
                    'completed': False,
                }
            )

            response = self.client.get(f'{self.url}/jobs/5')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(), {
                    'attachments': [],
                    'executor_id': None,
                    'id': 5,
                    'title': 'PyCharm',
                    'description': 'Web site',
                    'price': 5000,
                    'order_date': f'{now}Z'.replace(' ', 'T'),
                    'category_id': 1,
                    'customer_id': 2,
                    'completed': False,
                }
            )

            response = self.client.get(f'{self.url}/jobs/143')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Job not found'})

            # Select executor
            response = self.client.put(f'{self.url}/jobs/select-executor/143?user_id=2', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Job not found'})

            async_loop(job_crud.update(self.session, {'id': 2}, completed=True))
            async_loop(self.session.commit())
            response = self.client.put(f'{self.url}/jobs/select-executor/2?user_id=2', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Job is completed'})

            with mock.patch('app.permission.permission', return_value=2) as _:
                response = self.client.put(f'{self.url}/jobs/select-executor/1?user_id=2', headers=headers)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'You not owner this job'})

            response = self.client.put(f'{self.url}/jobs/select-executor/1?user_id=1', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'You cannot fulfill your job'})

            fake_user = {
                'username': 'string',
                'email': 'user@example.com',
                'about': 'string',
                'id': 1,
                'date_joined': '2021-10-20T13:16:37.732Z',
                'last_login': '2021-10-20T13:16:37.732Z',
                'avatar': '',
                'freelancer': False,
                'skills': [],
                'github': 'string'
            }
            with mock.patch('app.requests.get_user', return_value=fake_user) as _:
                response = self.client.put(f'{self.url}/jobs/select-executor/1?user_id=2', headers=headers)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'Executor not freelancer'})

            fake_user = {
                'username': 'string',
                'email': 'user@example.com',
                'about': 'string',
                'id': 2,
                'date_joined': '2021-10-20T13:16:37.732Z',
                'last_login': '2021-10-20T13:16:37.732Z',
                'avatar': '',
                'freelancer': True,
                'skills': [],
                'github': 'string'
            }
            with mock.patch('app.requests.get_user', return_value=fake_user) as _:
                response = self.client.put(f'{self.url}/jobs/select-executor/1?user_id=2', headers=headers)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.json(), {
                        'executor_id': 2,
                        'id': 1,
                        'title': 'Web site',
                        'description': 'Web site',
                        'price': 5000,
                        'order_date': f'{now}Z'.replace(' ', 'T'),
                        'category_id': 1,
                        'customer_id': 1,
                        'completed': False
                    }
                )

                response = self.client.put(f'{self.url}/jobs/select-executor/1?user_id=2', headers=headers)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'Executor already appointed'})

            # Complete job
            response = self.client.put(f'{self.url}/jobs/complete/1', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Job has been completed'})

            response = self.client.put(f'{self.url}/jobs/complete/1', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Job already completed'})

            response = self.client.put(f'{self.url}/jobs/complete/3', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Job has not executor'})

            with mock.patch('app.permission.permission', return_value=2) as _:
                response = self.client.put(f'{self.url}/jobs/complete/1', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'You not owner this job'})

            response = self.client.put(f'{self.url}/jobs/complete/143', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Job not found'})

            async_loop(job_crud.remove(self.session, id=5))
            async_loop(job_crud.update(self.session, {'id': 2}, completed=False, executor_id=2))
            async_loop(self.session.commit())
            # Except completed jobs
            # Get all without completed
            response = self.client.get(f'{self.url}/jobs/?page=1&page_size=1')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()['next'], f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/?page=2&page_size=1'
            )
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(len(response.json()['results']), 1)

            response = self.client.get(f'{self.url}/jobs/?page=2&page_size=1')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(
                response.json()['previous'], f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/?page=1&page_size=1'
            )
            self.assertEqual(response.json()['page'], 2)
            self.assertEqual(len(response.json()['results']), 1)

            response = self.client.get(f'{self.url}/jobs/?page=1&page_size=10')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(len(response.json()['results']), 2)

            response = self.client.get(f'{self.url}/jobs/?page=143&page_size=10')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Results not found'})

            # Get from categories without completed
            response = self.client.get(f'{self.url}/jobs/category?page=1&page_size=1&category_id=1')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(len(response.json()['results']), 1)
            self.assertEqual(response.json()['results'][0]['id'], 4)

            response = self.client.get(f'{self.url}/jobs/category?page=1&page_size=2&category_id=1')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(len(response.json()['results']), 1)
            self.assertEqual(response.json()['results'][0]['id'], 4)

            # Category 2
            response = self.client.get(f'{self.url}/jobs/category?page=1&page_size=1&category_id=2')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(len(response.json()['results']), 1)
            self.assertEqual(response.json()['results'][0]['id'], 3)

            response = self.client.get(f'{self.url}/jobs/category?page=1&page_size=2&category_id=2')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(len(response.json()['results']), 1)
            self.assertEqual(response.json()['results'][0]['id'], 3)

            response = self.client.get(f'{self.url}/jobs/category?page=2&page_size=2&category_id=1')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Results not found'})

            response = self.client.get(f'{self.url}/jobs/category?page=2&page_size=2&category_id=2')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Results not found'})

            response = self.client.get(f'{self.url}/jobs/category?page=2&page_size=2&category_id=143')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Results not found'})

            # Search
            response = self.client.get(f'{self.url}/jobs/search?page=1&page_size=1&search=web')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()['next'],
                f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/search?page=2&page_size=1&search=web'
            )
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(response.json()['results'][0]['id'], 4)
            self.assertEqual(len(response.json()['results']), 1)

            response = self.client.get(f'{self.url}/jobs/search?page=2&page_size=1&search=web')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(
                response.json()['previous'],
                f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/search?page=1&page_size=1&search=web'
            )
            self.assertEqual(response.json()['page'], 2)
            self.assertEqual(response.json()['results'][0]['id'], 3)
            self.assertEqual(len(response.json()['results']), 1)

            response = self.client.get(f'{self.url}/jobs/search?page=1&page_size=4&search=web')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(response.json()['results'][0]['id'], 4)
            self.assertEqual(len(response.json()['results']), 2)

            response = self.client.get(f'{self.url}/jobs/search?page=1&page_size=1&search=FastApi')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(response.json()['results'][0]['id'], 4)
            self.assertEqual(len(response.json()['results']), 1)

            response = self.client.get(f'{self.url}/jobs/search?page=1&page_size=1&search=Python')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(response.json()['results'][0]['id'], 3)
            self.assertEqual(len(response.json()['results']), 1)

            response = self.client.get(f'{self.url}/jobs/search?page=2&page_size=1&search=Python')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Results not found'})

            response = self.client.get(f'{self.url}/jobs/search?page=1&page_size=1&search=djangO')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Results not found'})

            response = self.client.get(f'{self.url}/jobs/search?page=1&page_size=1&search=Hello World!')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Results not found'})

            # Get jobs for freelancers
            with mock.patch('app.requests.get_user', return_value=fake_user) as _:
                response = self.client.get(f'{self.url}/jobs/freelancer?page=1&page_size=1&pk=2')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.json()['next'],
                    f'{SERVER_MAIN_BACKEND.strip("/")}{self.url}/jobs/freelancer?page=2&page_size=1&pk=2'
                )
                self.assertEqual(response.json()['previous'], None)
                self.assertEqual(len(response.json()['results']), 1)
                self.assertEqual(response.json()['results'][0]['id'], 2)
                self.assertEqual(response.json()['results'][0]['executor_id'], 2)
                self.assertEqual(response.json()['results'][0]['completed'], False)

                response = self.client.get(f'{self.url}/jobs/freelancer?page=2&page_size=1&pk=2')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()['next'], None)
                self.assertEqual(
                    response.json()['previous'],
                    f'{SERVER_MAIN_BACKEND.strip("/")}{self.url}/jobs/freelancer?page=1&page_size=1&pk=2'
                )
                self.assertEqual(len(response.json()['results']), 1)
                self.assertEqual(response.json()['results'][0]['id'], 1)
                self.assertEqual(response.json()['results'][0]['executor_id'], 2)
                self.assertEqual(response.json()['results'][0]['completed'], True)

            with mock.patch('app.requests.get_user', return_value={**fake_user, 'id': 1, 'freelancer': False}) as _:
                response = self.client.get(f'{self.url}/jobs/freelancer?page=1&page_size=1&pk=1')
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'User is customer'})

            with mock.patch('app.requests.get_user', return_value={**fake_user, 'id': 1}) as _:
                response = self.client.get(f'{self.url}/jobs/freelancer?page=1&page_size=1&pk=1')
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'Results not found'})

            # Get jobs for customers
            with mock.patch('app.requests.get_user', return_value={**fake_user, 'id': 1, 'freelancer': False}) as _:
                response = self.client.get(f'{self.url}/jobs/customer?page=1&page_size=2&pk=1')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.json()['next'],
                    f'{SERVER_MAIN_BACKEND.strip("/")}{self.url}/jobs/customer?page=2&page_size=2&pk=1'
                )
                self.assertEqual(response.json()['previous'], None)
                self.assertEqual(len(response.json()['results']), 2)
                self.assertEqual(response.json()['results'][0]['id'], 4)
                self.assertEqual(response.json()['results'][1]['id'], 3)
                self.assertEqual(response.json()['results'][0]['completed'], False)
                self.assertEqual(response.json()['results'][1]['completed'], False)
                self.assertEqual(response.json()['results'][0]['executor_id'], None)
                self.assertEqual(response.json()['results'][1]['executor_id'], None)

                response = self.client.get(f'{self.url}/jobs/customer?page=2&page_size=2&pk=1')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()['next'], None)
                self.assertEqual(
                    response.json()['previous'],
                    f'{SERVER_MAIN_BACKEND.strip("/")}{self.url}/jobs/customer?page=1&page_size=2&pk=1'
                )
                self.assertEqual(len(response.json()['results']), 2)
                self.assertEqual(response.json()['results'][0]['id'], 2)
                self.assertEqual(response.json()['results'][1]['id'], 1)
                self.assertEqual(response.json()['results'][0]['completed'], False)
                self.assertEqual(response.json()['results'][1]['completed'], True)
                self.assertEqual(response.json()['results'][0]['executor_id'], 2)
                self.assertEqual(response.json()['results'][1]['executor_id'], 2)

            with mock.patch('app.requests.get_user', return_value=fake_user) as _:
                response = self.client.get(f'{self.url}/jobs/customer?page=1&page_size=1&pk=2')
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'User is freelancer'})

            with mock.patch('app.requests.get_user', return_value={**fake_user, 'freelancer': False}) as _:
                response = self.client.get(f'{self.url}/jobs/customer?page=1&page_size=1&pk=2')
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'Results not found'})

            # Get all
            response = self.client.get(f'{self.url}/jobs/all?page=1&page_size=2')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()['next'],
                f'{SERVER_MAIN_BACKEND.strip("/")}{self.url}/jobs/all?page=2&page_size=2'
            )
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(len(response.json()['results']), 2)
            self.assertEqual(response.json()['results'][0]['id'], 4)
            self.assertEqual(response.json()['results'][1]['id'], 3)
            self.assertEqual(response.json()['results'][0]['completed'], False)
            self.assertEqual(response.json()['results'][1]['completed'], False)
            self.assertEqual(response.json()['results'][0]['executor_id'], None)
            self.assertEqual(response.json()['results'][1]['executor_id'], None)

            response = self.client.get(f'{self.url}/jobs/all?page=2&page_size=2')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(
                response.json()['previous'],
                f'{SERVER_MAIN_BACKEND.strip("/")}{self.url}/jobs/all?page=1&page_size=2'
            )
            self.assertEqual(response.json()['page'], 2)
            self.assertEqual(len(response.json()['results']), 2)
            self.assertEqual(response.json()['results'][0]['id'], 2)
            self.assertEqual(response.json()['results'][1]['id'], 1)
            self.assertEqual(response.json()['results'][0]['completed'], False)
            self.assertEqual(response.json()['results'][1]['completed'], True)
            self.assertEqual(response.json()['results'][0]['executor_id'], 2)
            self.assertEqual(response.json()['results'][1]['executor_id'], 2)

            # Get from categories
            response = self.client.get(f'{self.url}/jobs/category/all?page=1&page_size=1&category_id=1')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()['next'],
                f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/category/all?page=2&page_size=1&category_id=1'
            )
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(len(response.json()['results']), 1)
            self.assertEqual(response.json()['results'][0]['id'], 4)
            self.assertEqual(response.json()['results'][0]['completed'], False)
            self.assertEqual(response.json()['results'][0]['executor_id'], None)

            response = self.client.get(f'{self.url}/jobs/category/all?page=2&page_size=1&category_id=1')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(
                response.json()['previous'],
                f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/category/all?page=1&page_size=1&category_id=1'
            )
            self.assertEqual(response.json()['page'], 2)
            self.assertEqual(len(response.json()['results']), 1)
            self.assertEqual(response.json()['results'][0]['id'], 1)
            self.assertEqual(response.json()['results'][0]['completed'], True)
            self.assertEqual(response.json()['results'][0]['executor_id'], 2)

            response = self.client.get(f'{self.url}/jobs/category/all?page=1&page_size=2&category_id=1')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(len(response.json()['results']), 2)
            self.assertEqual(response.json()['results'][0]['id'], 4)
            self.assertEqual(response.json()['results'][1]['id'], 1)
            self.assertEqual(response.json()['results'][0]['completed'], False)
            self.assertEqual(response.json()['results'][0]['executor_id'], None)
            self.assertEqual(response.json()['results'][1]['completed'], True)
            self.assertEqual(response.json()['results'][1]['executor_id'], 2)

            # Category 2
            response = self.client.get(f'{self.url}/jobs/category/all?page=1&page_size=1&category_id=2')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()['next'],
                f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/category/all?page=2&page_size=1&category_id=2'
            )
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(len(response.json()['results']), 1)
            self.assertEqual(response.json()['results'][0]['id'], 3)
            self.assertEqual(response.json()['results'][0]['completed'], False)
            self.assertEqual(response.json()['results'][0]['executor_id'], None)

            response = self.client.get(f'{self.url}/jobs/category/all?page=2&page_size=1&category_id=2')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(
                response.json()['previous'],
                f'{SERVER_MAIN_BACKEND}{self.url.strip("/")}/jobs/category/all?page=1&page_size=1&category_id=2'
            )
            self.assertEqual(response.json()['page'], 2)
            self.assertEqual(len(response.json()['results']), 1)
            self.assertEqual(response.json()['results'][0]['id'], 2)
            self.assertEqual(response.json()['results'][0]['completed'], False)
            self.assertEqual(response.json()['results'][0]['executor_id'], 2)

            response = self.client.get(f'{self.url}/jobs/category/all?page=1&page_size=2&category_id=2')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['next'], None)
            self.assertEqual(response.json()['previous'], None)
            self.assertEqual(response.json()['page'], 1)
            self.assertEqual(len(response.json()['results']), 2)
            self.assertEqual(response.json()['results'][0]['id'], 3)
            self.assertEqual(response.json()['results'][1]['id'], 2)
            self.assertEqual(response.json()['results'][0]['completed'], False)
            self.assertEqual(response.json()['results'][0]['executor_id'], None)
            self.assertEqual(response.json()['results'][1]['completed'], False)
            self.assertEqual(response.json()['results'][1]['executor_id'], 2)

            response = self.client.get(f'{self.url}/jobs/category/all?page=2&page_size=2&category_id=1')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Results not found'})

            response = self.client.get(f'{self.url}/jobs/category/all?page=2&page_size=2&category_id=2')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Results not found'})

            response = self.client.get(f'{self.url}/jobs/category/all?page=2&page_size=2&category_id=143')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Results not found'})

            # Update (owner)
            response = self.client.get(f'{self.url}/jobs/3')
            self.assertEqual(
                response.json(),
                {
                    'attachments': [],
                    'category_id': 2,
                    'completed': False,
                    'customer_id': 1,
                    'description': 'Web site',
                    'executor_id': None,
                    'id': 3,
                    'order_date': f'{now}Z'.replace(' ', 'T'),
                    'price': 5000,
                    'title': 'Python'
                }

            )

            response = self.client.put(
                f'{self.url}/jobs/3', json={
                    'title': 'Web site',
                    'description': 'Web site',
                    'price': 5000,
                    'order_date': f'{now + datetime.timedelta(minutes=15)}Z',
                    'category_id': 1,
                }, headers=headers
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(),
                {
                    'category_id': 1,
                    'completed': False,
                    'customer_id': 1,
                    'description': 'Web site',
                    'executor_id': None,
                    'id': 3,
                    'order_date': f'{now + datetime.timedelta(minutes=15)}Z'.replace(' ', 'T'),
                    'price': 5000,
                    'title': 'Web site'
                }
            )

            response = self.client.put(
                f'{self.url}/jobs/143', json={
                    'title': 'Web site',
                    'description': 'Web site',
                    'price': 5000,
                    'order_date': f'{now}Z',
                    'category_id': 1,
                }, headers=headers
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Job not found'})

            with mock.patch('app.permission.permission', return_value=2) as _:
                response = self.client.put(
                    f'{self.url}/jobs/3', json={
                        'title': 'Web site',
                        'description': 'Web site',
                        'price': 5000,
                        'order_date': f'{now}Z',
                        'category_id': 1,
                    }, headers=headers
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'You not owner this job'})

            response = self.client.put(
                f'{self.url}/jobs/1', json={
                    'title': 'Web site',
                    'description': 'Web site',
                    'price': 5000,
                    'order_date': f'{now}Z',
                    'category_id': 1,
                }, headers=headers
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Job is completed'})

            response = self.client.put(
                f'{self.url}/jobs/3', json={
                    'title': 'Web site',
                    'description': 'Web site',
                    'price': 5000,
                    'order_date': f'{now}Z',
                    'category_id': 143,
                }, headers=headers
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Category not found'})

            response = self.client.put(
                f'{self.url}/jobs/3', json={
                    'title': 'Web site',
                    'description': 'Web site',
                    'price': 5000,
                    'order_date': f'{now - datetime.timedelta(minutes=11)}Z',
                    'category_id': 1,
                }, headers=headers
            )
            self.assertEqual(response.status_code, 422)
            self.assertEqual(response.json()['detail'][0]['msg'], 'Date can\'t be past')

            # Update (admin)
            with mock.patch('app.requests.get_user', return_value={**fake_user, 'id': 2}) as _:
                response = self.client.put(
                    f'{self.url}/jobs/admin/3?executor_id=2', json={
                        'title': 'Web',
                        'description': 'Web site',
                        'price': 50000,
                        'order_date': f'{now}Z',
                        'category_id': 2,
                        'completed': True,
                    }, headers=headers
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.json(),
                    {
                        'category_id': 2,
                        'completed': True,
                        'customer_id': 1,
                        'description': 'Web site',
                        'executor_id': 2,
                        'id': 3,
                        'order_date': f'{now}Z'.replace(' ', 'T'),
                        'price': 50000,
                        'title': 'Web'
                    }
                )

                response = self.client.put(
                    f'{self.url}/jobs/admin/143?executor_id=2', json={
                        'title': 'Web',
                        'description': 'Web site',
                        'price': 50000,
                        'order_date': f'{now}Z',
                        'category_id': 1,
                        'completed': True,
                    }, headers=headers
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'Job not found'})

                response = self.client.put(
                    f'{self.url}/jobs/admin/3?executor_id=2', json={
                        'title': 'Web',
                        'description': 'Web site',
                        'price': 50000,
                        'order_date': f'{now}Z',
                        'category_id': 143,
                        'completed': True,
                    }, headers=headers
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'Category not found'})

            # Delete job (owner)
            self.assertEqual(len(async_loop(job_crud.all(self.session))), 4)

            response = self.client.delete(f'{self.url}/jobs/4', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Job has been deleted'})
            self.assertEqual(len(async_loop(job_crud.all(self.session))), 3)

            with mock.patch('app.permission.permission', return_value=2) as _:
                response = self.client.delete(f'{self.url}/jobs/3', headers=headers)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'You not owner this job'})

            response = self.client.delete(f'{self.url}/jobs/143', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Job not found'})
            self.assertEqual(len(async_loop(job_crud.all(self.session))), 3)

            # Delete job (admin)
            self.assertEqual(len(async_loop(job_crud.all(self.session))), 3)

            self.assertEqual(async_loop(job_crud.get(self.session, id=1)).customer_id, 1)
            with mock.patch('app.permission.permission', return_value=2) as _:
                response = self.client.delete(f'{self.url}/jobs/admin/1', headers=headers)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {'msg': 'Job has been deleted'})
                self.assertEqual(len(async_loop(job_crud.all(self.session))), 2)

            response = self.client.delete(f'{self.url}/jobs/admin/143', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Job not found'})
            self.assertEqual(len(async_loop(job_crud.all(self.session))), 2)

            # Delete all jobs
            async_loop(job_crud.update(self.session, {'id': 2}, customer_id=2, executor_id=3))
            async_loop(job_crud.update(self.session, {'id': 3}, customer_id=3, executor_id=2))
            async_loop(self.session.commit())
            self.assertEqual(len(async_loop(job_crud.all(self.session))), 2)

            self.assertEqual(async_loop(job_crud.get(self.session, id=2)).customer_id, 2)
            self.assertEqual(async_loop(job_crud.get(self.session, id=2)).executor_id, 3)
            self.assertEqual(async_loop(job_crud.get(self.session, id=3)).customer_id, 3)
            self.assertEqual(async_loop(job_crud.get(self.session, id=3)).executor_id, 2)

            with mock.patch('app.permission.permission', return_value=2) as _:
                response = self.client.delete(f'{self.url}/jobs/all', headers=headers)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {'msg': 'Jobs has been deleted'})

            self.assertEqual(len(async_loop(job_crud.all(self.session))), 0)

    def test_attachments(self):
        with mock.patch('app.permission.permission', return_value=1) as _:
            headers = {'Authorization': 'Bearer Token'}

            self.assertEqual(len(async_loop(job_crud.all(self.session))), 0)

            self.client.post(f'{self.url}/categories/', json={'name': 'Programming'}, headers=headers)
            self.client.post(
                f'{self.url}/categories/', json={'name': 'Python', 'super_category_id': 1}, headers=headers,
            )
            self.client.post(
                f'{self.url}/categories/', json={'name': 'FastAPI', 'super_category_id': 1}, headers=headers,
            )

            # Create
            now = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
            self.client.post(
                f'{self.url}/jobs/', headers=headers, json={
                    'title': 'Web site',
                    'description': 'Web site',
                    'price': 5000,
                    'order_date': f'{now}Z',
                    'category_id': 1,
                }
            )

            self.client.post(
                f'{self.url}/jobs/', headers=headers, json={
                    'title': 'Web site',
                    'description': 'Web site',
                    'price': 5000,
                    'order_date': f'{now}Z',
                    'category_id': 1,
                }
            )

            image = UploadFile('image.png', content_type='image/png')
            doc = UploadFile('doc.doc', content_type='application/msword')
            xls = UploadFile('xls.xls', content_type='application/vnd.ms-excel')

            job = async_loop(job_crud.get(self.session, id=1))
            self.assertEqual(len(job.attachments), 0)
            self.assertEqual(len(async_loop(attachment_crud.all(self.session))), 0)

            # Add
            response = self.client.post(
                f'{self.url}/jobs/attachments/add?job_id=1',
                headers=headers,
                files=[
                    ('files', ('image.png', async_loop(image.read()), 'image/png')),
                    ('files', ('doc.doc', async_loop(doc.read()), 'application/msword'),),
                    ('files', ('xls.xls', async_loop(xls.read()), 'application/vnd.ms-excel')),
                ]
            )
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json(), {'msg': 'Attachments has been added'})
            async_loop(self.session.commit())
            job = async_loop(job_crud.get(self.session, id=1))
            self.assertEqual(len(job.attachments), 3)
            self.assertEqual(len(async_loop(attachment_crud.all(self.session))), 3)

            file_1, file_2, file_3 = job.attachments
            self.assertEqual(os.path.exists(file_1.path), True)
            self.assertEqual(os.path.exists(file_2.path), True)
            self.assertEqual(os.path.exists(file_3.path), True)
            self.assertNotEqual(file_2, file_3)
            self.assertNotEqual(file_1, file_2)
            self.assertNotEqual(file_1, file_3)

            self.assertEqual(f'{MEDIA_ROOT}{job.id}' in file_2.path, True)

            response = self.client.post(
                f'{self.url}/jobs/attachments/add?job_id=2',
                headers=headers,
                files=[
                    ('files', ('image.png', async_loop(image.read()), 'image/png')),
                    ('files', ('doc.doc', async_loop(doc.read()), 'application/msword'),),
                    ('files', ('xls.xls', async_loop(xls.read()), 'application/vnd.ms-excel')),
                ]
            )
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json(), {'msg': 'Attachments has been added'})
            async_loop(self.session.commit())
            job = async_loop(job_crud.get(self.session, id=1))
            job_2 = async_loop(job_crud.get(self.session, id=2))
            self.assertEqual(len(job.attachments), 3)
            self.assertEqual(len(job_2.attachments), 3)
            self.assertEqual(len(async_loop(attachment_crud.all(self.session))), 6)

            with mock.patch('app.permission.permission', return_value=2) as _:
                response = self.client.post(
                    f'{self.url}/jobs/attachments/add?job_id=1',
                    headers=headers,
                    files=[
                        ('files', ('image.png', async_loop(image.read()), 'image/png')),
                        ('files', ('doc.doc', async_loop(doc.read()), 'application/msword'),),
                        ('files', ('xls.xls', async_loop(xls.read()), 'application/vnd.ms-excel')),
                    ]
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'You not owner this job'})

            response = self.client.post(
                f'{self.url}/jobs/attachments/add?job_id=143',
                headers=headers,
                files=[
                    ('files', ('image.png', async_loop(image.read()), 'image/png')),
                    ('files', ('doc.doc', async_loop(doc.read()), 'application/msword'),),
                    ('files', ('xls.xls', async_loop(xls.read()), 'application/vnd.ms-excel')),
                ]
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Job not found'})

            response = self.client.get(f'{self.url}/jobs/2')
            self.assertEqual(response.json()['category_id'], 1)
            self.assertEqual(response.json()['completed'], False)
            self.assertEqual(response.json()['customer_id'], 1)
            self.assertEqual(response.json()['description'], 'Web site')
            self.assertEqual(response.json()['executor_id'], None)
            self.assertEqual(response.json()['id'], 2)
            self.assertEqual(response.json()['order_date'], f'{now}Z'.replace(' ', 'T'))
            self.assertEqual(response.json()['price'], 5000)
            self.assertEqual(response.json()['title'], 'Web site')
            self.assertEqual(len(response.json()['attachments']), 3)
            self.assertEqual(response.json()['attachments'][0]['id'], 4)
            self.assertEqual(response.json()['attachments'][1]['id'], 5)
            self.assertEqual(response.json()['attachments'][2]['id'], 6)

            self.assertEqual(
                f'{SERVER_MAIN_BACKEND.strip("/")}{self.url}/jobs' in response.json()['attachments'][0]['path'], True
            )
            attachment_1 = response.json()['attachments'][0]['path'].replace(
                f'{SERVER_MAIN_BACKEND}', ''
            ).replace('tests', '')
            attachment_2 = response.json()['attachments'][1]['path'].replace(
                f'{SERVER_MAIN_BACKEND}', ''
            ).replace('tests', '')
            attachment_3 = response.json()['attachments'][2]['path'].replace(
                f'{SERVER_MAIN_BACKEND}', ''
            ).replace('tests', '')

            # Get attachments
            response_1 = self.client.get(attachment_1)
            self.assertEqual(response_1.status_code, 200)

            response_2 = self.client.get(attachment_2)
            self.assertEqual(response_2.status_code, 200)

            response_3 = self.client.get(attachment_3)
            self.assertEqual(response_3.status_code, 200)

            response = self.client.get(f'{self.url}/jobs/media/1/4343.png')
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json(), {'detail': 'File not found'})

            # Remove
            attachment_6 = async_loop(attachment_crud.get(self.session, id=6))
            self.assertEqual(os.path.exists(attachment_6.path), True)

            response = self.client.delete(f'{self.url}/jobs/attachments/remove?pk=6', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Attachment has been deleted'})

            self.assertEqual(len(async_loop(attachment_crud.all(self.session))), 5)
            self.assertEqual(os.path.exists(attachment_6.path), False)

            response = self.client.delete(f'{self.url}/jobs/attachments/remove?pk=143', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Attachment not found'})

            with mock.patch('app.permission.permission', return_value=2) as _:
                response = self.client.delete(f'{self.url}/jobs/attachments/remove?pk=5', headers=headers)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'You not owner this job'})

            response = self.client.delete(f'{self.url}/jobs/attachments/remove?pk=5', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Attachment has been deleted'})

            self.assertEqual(len(async_loop(attachment_crud.all(self.session))), 4)

            response = self.client.delete(f'{self.url}/jobs/attachments/remove?pk=4', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Attachment has been deleted'})

            self.assertEqual(len(async_loop(attachment_crud.all(self.session))), 3)

            response = self.client.delete(f'{self.url}/jobs/attachments/remove?pk=3', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Attachment has been deleted'})

            self.assertEqual(len(async_loop(attachment_crud.all(self.session))), 2)

            response = self.client.delete(f'{self.url}/jobs/attachments/remove?pk=2', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Attachment has been deleted'})

            self.assertEqual(len(async_loop(attachment_crud.all(self.session))), 1)

            response = self.client.delete(f'{self.url}/jobs/attachments/remove?pk=1', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'msg': 'Attachment has been deleted'})

            self.assertEqual(len(async_loop(attachment_crud.all(self.session))), 0)
