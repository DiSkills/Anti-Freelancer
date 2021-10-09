from unittest import TestCase

from fastapi import UploadFile

from app.crud import verification_crud, user_crud, skill_crud
from tests import BaseTest, async_loop


class SkillsTestCase(BaseTest, TestCase):

    def test_skills(self):
        self.client.post(self.url + '/register', json={**self.user_data, 'freelancer': True})
        verification = async_loop(verification_crud.get(self.session, id=1))
        self.client.get(self.url + f'/verify?link={verification.link}')
        async_loop(user_crud.update(self.session, {'id': 1}, is_superuser=True))
        async_loop(self.session.commit())

        tokens = self.client.post(f'{self.url}/login', data={'username': 'test', 'password': 'Test1234!'})
        headers = {'Authorization': f'Bearer {tokens.json()["access_token"]}'}

        self.assertEqual(len(async_loop(skill_crud.all(self.session))), 0)
        # Create 1
        response = self.client.post(
            f'{self.url}/skills/',
            headers=headers,
            json={
                'name': 'FastAPI',
                'image': 'https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white',
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
            'name': 'FastAPI',
            'image': 'https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white',
            'id': 1,
        })
        self.assertEqual(len(async_loop(skill_crud.all(self.session))), 1)

        response = self.client.post(
            f'{self.url}/skills/',
            headers=headers,
            json={
                'name': 'FastAPI',
                'image': 'https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white',
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Skill name exist'})

        response = self.client.post(
            f'{self.url}/skills/',
            headers=headers,
            json={
                'name': 'GitHub',
                'image': 'https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white',
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Skill image exist'})

        # Remove
        self.assertEqual(len(async_loop(skill_crud.all(self.session))), 1)
        response = self.client.delete(f'{self.url}/skills/1', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'msg': 'Skill has been deleted'})
        self.assertEqual(len(async_loop(skill_crud.all(self.session))), 0)

        response = self.client.delete(f'{self.url}/skills/2', headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Skill not found'})

        # Import from excel
        self.assertEqual(len(async_loop(skill_crud.all(self.session))), 0)
        with open('tests/skills.xls', 'rb') as file:
            response = self.client.post(
                f'{self.url}/skills/excel',
                headers=headers,
                files={'file': ('skills.xls', file, 'application/vnd.ms-excel')}
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.json()), 46)
        self.assertEqual(len(async_loop(skill_crud.all(self.session))), 46)

        file = UploadFile('skills.png', content_type='image/png')
        response = self.client.post(
            f'{self.url}/skills/excel',
            headers=headers,
            files={'file': ('skills.png', async_loop(file.read()), 'image/png')}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'File only format xls (excel)'})

        # Get all
        response = self.client.get(f'{self.url}/skills/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 46)

        # Get
        response = self.client.get(f'{self.url}/skills/1')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Skill not found'})

        response = self.client.get(f'{self.url}/skills/2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'id': 2,
                'image': 'https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white',
                'name': 'GitHub',
            }
        )

        # Update
        response = self.client.put(f'{self.url}/skills/1', headers=headers, json={
            'image': 'https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white',
            'name': 'GitHub',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Skill not found'})

        response = self.client.put(f'{self.url}/skills/3', headers=headers, json={
            'image': 'https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white',
            'name': 'GitHub',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Skill name exist'})

        response = self.client.put(f'{self.url}/skills/3', headers=headers, json={
            'image': 'https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white',
            'name': 'Programming',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Skill image exist'})

        response = self.client.put(f'{self.url}/skills/2', headers=headers, json={
            'image': 'https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white',
            'name': 'GitHub',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'id': 2,
                'image': 'https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white',
                'name': 'GitHub',
            }
        )

        response = self.client.put(f'{self.url}/skills/2', headers=headers, json={
            'image': 'https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white1',
            'name': 'GitHub1',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'id': 2,
                'image': 'https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white1',
                'name': 'GitHub1',
            }
        )
