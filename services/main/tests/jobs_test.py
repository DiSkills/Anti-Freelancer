import datetime
from unittest import TestCase, mock

from app.crud import job_crud
from config import SERVER_MAIN_BACKEND
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
                'customer_id': 1,
                'completed': False,
                'title': 'Web site',
                'executor_id': None,
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

            # Get all without completed
            self.client.post(f'{self.url}/jobs/', headers=headers, json={
                'title': 'Django',
                'description': 'Web site',
                'price': 5000,
                'order_date': f'{now}Z',
                'category_id': 2,
            })
            self.client.post(f'{self.url}/jobs/', headers=headers, json={
                'title': 'Python',
                'description': 'Web site',
                'price': 5000,
                'order_date': f'{now}Z',
                'category_id': 2,
            })
            self.client.post(f'{self.url}/jobs/', headers=headers, json={
                'title': 'FastAPI',
                'description': 'Web site',
                'price': 5000,
                'order_date': f'{now}Z',
                'category_id': 1,
            })

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
                self.client.post(f'{self.url}/jobs/', headers=headers, json={
                    'title': 'PyCharm',
                    'description': 'Web site',
                    'price': 5000,
                    'order_date': f'{now}Z',
                    'category_id': 1,
                })
            response = self.client.get(f'{self.url}/jobs/1')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {
                'executor_id': None,
                'id': 1,
                'title': 'Web site',
                'description': 'Web site',
                'price': 5000,
                'order_date': f'{now}Z'.replace(' ', 'T'),
                'category_id': 1,
                'customer_id': 1,
                'completed': False,
            })

            response = self.client.get(f'{self.url}/jobs/5')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {
                'executor_id': None,
                'id': 5,
                'title': 'PyCharm',
                'description': 'Web site',
                'price': 5000,
                'order_date': f'{now}Z'.replace(' ', 'T'),
                'category_id': 1,
                'customer_id': 2,
                'completed': False,
            })

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
                self.assertEqual(response.json(), {
                    'executor_id': 2,
                    'id': 1,
                    'title': 'Web site',
                    'description': 'Web site',
                    'price': 5000,
                    'order_date': f'{now}Z'.replace(' ', 'T'),
                    'category_id': 1,
                    'customer_id': 1,
                    'completed': False
                })

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
