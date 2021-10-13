from unittest import TestCase, mock

from app.crud import super_category_crud, sub_category_crud
from tests import BaseTest, async_loop


class CategoriesTestCase(BaseTest, TestCase):

    def test_categories(self):
        with mock.patch('app.permission.permission', return_value={'user_id': 1}) as _:
            headers = {'Authorization': 'Bearer Token'}

            # Create
            self.assertEqual(len(async_loop(super_category_crud.all(self.session))), 0)
            self.assertEqual(len(async_loop(sub_category_crud.all(self.session))), 0)

            response = self.client.post(f'{self.url}/categories/', json={'name': 'Programming'}, headers=headers)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json(), {'id': 1, 'name': 'Programming', 'super_category_id': None})

            self.assertEqual(len(async_loop(super_category_crud.all(self.session))), 1)
            self.assertEqual(len(async_loop(sub_category_crud.all(self.session))), 0)

            response = self.client.post(
                f'{self.url}/categories/', json={'name': 'Python', 'super_category_id': 1}, headers=headers
            )
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json(), {'id': 1, 'name': 'Python', 'super_category_id': 1})

            self.assertEqual(len(async_loop(super_category_crud.all(self.session))), 1)
            self.assertEqual(len(async_loop(sub_category_crud.all(self.session))), 1)

            response = self.client.post(
                f'{self.url}/categories/', json={'name': 'Python', 'super_category_id': 143}, headers=headers
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Super category not found'})

            # Get all
            self.client.post(f'{self.url}/categories/', json={'name': 'Design'}, headers=headers)
            self.client.post(
                f'{self.url}/categories/', json={'name': 'C++', 'super_category_id': 1}, headers=headers
            )
            self.client.post(
                f'{self.url}/categories/', json={'name': 'JavaScript', 'super_category_id': 1}, headers=headers
            )

            response = self.client.get(f'{self.url}/categories/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), [
                {
                    'id': 2,
                    'name': 'Design',
                    'super_category_id': None,
                    'sub_categories': []
                },
                {
                    'id': 1,
                    'name': 'Programming',
                    'super_category_id': None,
                    'sub_categories': [
                        {'id': 2, 'name': 'C++', 'super_category_id': 1},
                        {'id': 3, 'name': 'JavaScript', 'super_category_id': 1},
                        {'id': 1, 'name': 'Python', 'super_category_id': 1},
                    ]
                },
            ])

            self.client.post(
                f'{self.url}/categories/', json={'name': 'Web', 'super_category_id': 2}, headers=headers
            )

            response = self.client.get(f'{self.url}/categories/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), [
                {
                    'id': 2,
                    'name': 'Design',
                    'super_category_id': None,
                    'sub_categories': [
                        {'id': 4, 'name': 'Web', 'super_category_id': 2},
                    ]
                },
                {
                    'id': 1,
                    'name': 'Programming',
                    'super_category_id': None,
                    'sub_categories': [
                        {'id': 2, 'name': 'C++', 'super_category_id': 1},
                        {'id': 3, 'name': 'JavaScript', 'super_category_id': 1},
                        {'id': 1, 'name': 'Python', 'super_category_id': 1},
                    ]
                },
            ])