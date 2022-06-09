from unittest import TestCase

from app.crud import user_crud
from createsuperuser import createsuperuser
from tests import BaseTest, async_loop


class CreateSuperUserTestCase(BaseTest, TestCase):

    def test_createsuperuser(self):
        self.assertEqual(len(async_loop(user_crud.all(self.session))), 0)
        async_loop(createsuperuser(self.session, 'test', 'Test123456!', 'test@example.com'))
        self.assertEqual(len(async_loop(user_crud.all(self.session))), 2)

        async_loop(createsuperuser(self.session, 'test2', 'Test123456!', 'test2@example.com'))
        self.assertEqual(len(async_loop(user_crud.all(self.session))), 2)
