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

        # Get super category
        response = self.client.get(f'{self.url}/categories/sup/2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'id': 2,
            'name': 'Design',
            'super_category_id': None,
            'sub_categories': [
                {'id': 4, 'name': 'Web', 'super_category_id': 2},
            ]
        })

        response = self.client.get(f'{self.url}/categories/sup/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'id': 1,
            'name': 'Programming',
            'super_category_id': None,
            'sub_categories': [
                {'id': 2, 'name': 'C++', 'super_category_id': 1},
                {'id': 3, 'name': 'JavaScript', 'super_category_id': 1},
                {'id': 1, 'name': 'Python', 'super_category_id': 1},
            ]
        })

        response = self.client.get(f'{self.url}/categories/sup/143')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Super category not found'})

        # Get sub category
        response = self.client.get(f'{self.url}/categories/sub/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'id': 1, 'name': 'Python', 'super_category_id': 1})

        response = self.client.get(f'{self.url}/categories/sub/2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'id': 2, 'name': 'C++', 'super_category_id': 1})

        response = self.client.get(f'{self.url}/categories/sub/4')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'id': 4, 'name': 'Web', 'super_category_id': 2})

        response = self.client.get(f'{self.url}/categories/sub/143')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Sub category not found'})

        # Update super category
        response = self.client.put(f'{self.url}/categories/sup/2', headers=headers, json={'name': 'Game development'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'id': 2,
            'name': 'Game development',
            'super_category_id': None,
            'sub_categories': [
                {'id': 4, 'name': 'Web', 'super_category_id': 2},
            ]
        })
        self.assertEqual(async_loop(super_category_crud.get(self.session, id=2)).name, 'Game development')

        response = self.client.put(f'{self.url}/categories/sup/143', headers=headers, json={'name': 'Game development'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Super category not found'})

        # Update sub category
        response = self.client.put(f'{self.url}/categories/sub/4', headers=headers, json={'name': 'Unity'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'id': 4, 'name': 'Unity', 'super_category_id': 2})
        self.assertEqual(async_loop(sub_category_crud.get(self.session, id=4)).name, 'Unity')

        response = self.client.put(f'{self.url}/categories/sub/143', headers=headers, json={'name': 'Unity'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Sub category not found'})

        # Delete super category
        self.assertEqual(len(async_loop(super_category_crud.all(self.session))), 2)
        self.assertEqual(len(async_loop(sub_category_crud.all(self.session))), 4)

        response = self.client.delete(f'{self.url}/categories/sup/2', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'msg': 'Super category has been deleted'})
        self.assertEqual(len(async_loop(super_category_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(sub_category_crud.all(self.session))), 3)

        response = self.client.delete(f'{self.url}/categories/sup/143', headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Super category not found'})
        self.assertEqual(len(async_loop(super_category_crud.all(self.session))), 1)
        self.assertEqual(len(async_loop(sub_category_crud.all(self.session))), 3)

        # Delete sub category
        self.assertEqual(len(async_loop(sub_category_crud.all(self.session))), 3)

        response = self.client.delete(f'{self.url}/categories/sub/3', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'msg': 'Sub category has been deleted'})
        self.assertEqual(len(async_loop(sub_category_crud.all(self.session))), 2)

        response = self.client.delete(f'{self.url}/categories/sub/143', headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Sub category not found'})
        self.assertEqual(len(async_loop(sub_category_crud.all(self.session))), 2)
