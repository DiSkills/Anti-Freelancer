from unittest import TestCase, mock

from app.crud import dialogue_crud
from tests import BaseTest, async_loop


class MessageTestCase(BaseTest, TestCase):

    def setUp(self) -> None:
        super().setUp()
        async_loop(dialogue_crud.create(self.session, users_ids='2_1'))
        async_loop(dialogue_crud.create(self.session, users_ids='1_4'))
        async_loop(dialogue_crud.create(self.session, users_ids='1_6'))
        async_loop(dialogue_crud.create(self.session, users_ids='11_2'))
        async_loop(dialogue_crud.create(self.session, users_ids='12_2'))
        async_loop(dialogue_crud.create(self.session, users_ids='13_156'))
        async_loop(dialogue_crud.create(self.session, users_ids='111_11'))
        async_loop(dialogue_crud.create(self.session, users_ids='1111_1'))
        async_loop(dialogue_crud.create(self.session, users_ids='1_111'))
        self.count_true_results = 5
        self.true_results = [111, 1111, 6, 4, 2]

    def test_crud_get_for_user(self):
        dialogues = async_loop(dialogue_crud.get_for_user(self.session, 1))
        self.assertEqual(len(dialogues), self.count_true_results)
        self.assertEqual([dialogue.get_recipient_id(1) for dialogue in dialogues], self.true_results)

    def test_get_dialogue(self):
        headers = {'Authorization': 'Bearer Token'}

        with mock.patch('app.permission.permission', return_value=1) as _:
            with mock.patch('app.requests.get_user_request', return_value=self.get_new_user(2)) as _:
                response = self.client.get(f'{self.url}/dialogues/1', headers=headers)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {'id': 1, 'user': self.get_new_user(2)})

        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.get(f'{self.url}/dialogues/7', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'You are not in this dialogue'})

        with mock.patch('app.permission.permission', return_value=1) as _:
            response = self.client.get(f'{self.url}/dialogues/143', headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'detail': 'Dialogue not found'})

    def test_get_dialogues(self):
        headers = {'Authorization': 'Bearer Token'}

        with mock.patch('app.permission.permission', return_value=1) as _:
            with mock.patch(
                    'app.requests.get_users_request',
                    return_value={f'{user}': self.get_new_user(user) for user in self.true_results}
            ) as _:
                response = self.client.get(f'{self.url}/dialogues/', headers=headers)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()), self.count_true_results)
                self.assertEqual(
                    response.json(),
                    [
                        {
                            'id': 9,
                            'user': self.get_new_user(111)
                        },
                        {
                            'id': 8,
                            'user': self.get_new_user(1111)
                        },
                        {
                            'id': 3,
                            'user': self.get_new_user(6)
                        },
                        {
                            'id': 2,
                            'user': self.get_new_user(4)
                        },
                        {
                            'id': 1,
                            'user': self.get_new_user(2)
                        }
                    ]
                )

        with mock.patch('app.permission.permission', return_value=2) as _:
            with mock.patch(
                    'app.requests.get_users_request',
                    return_value={f'{user}': self.get_new_user(user) for user in [11, 12, 1]}
            ) as _:
                response = self.client.get(f'{self.url}/dialogues/', headers=headers)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()), 3)
                self.assertEqual(
                    response.json(),
                    [
                        {'id': 5, 'user': self.get_new_user(12)},
                        {'id': 4, 'user': self.get_new_user(11)},
                        {'id': 1, 'user': self.get_new_user(1)},
                    ]
                )
