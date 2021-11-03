import os

from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv

load_dotenv('config.env')

BASE_DIR = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get('SECRET_KEY')

PROJECT_NAME = 'Anti-Freelancer'
SERVER_BACKEND = 'http://localhost:8000/'
SERVER_EMAIL = 'http://localhost:8003/'
API = 'api/v1'

TEST = os.environ.get('TEST', 0)
DOCKER = os.environ.get('DOCKER', 0)

DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

CLIENT_NAME = 'auth'

MEDIA_ROOT = 'media/'

if int(TEST):
    DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}_test'
    MEDIA_ROOT = 'media/tests/'

if int(DOCKER):
    SERVER_EMAIL = 'http://email:8003/'

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 15
RESET_TOKEN_EXPIRE_MINUTES = 15

ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

SERVER_USER_EMAIL = os.environ.get('SERVER_EMAIL')
SERVER_USER_USERNAME = os.environ.get('SERVER_USERNAME')
SERVER_USER_PASSWORD = os.environ.get('SERVER_PASSWORD')

social_auth = OAuth()
redirect_url = f'{SERVER_BACKEND}{API}/github/bind'

social_auth.register(
    name='github',
    client_id=os.environ.get('GITHUB_ID'),
    client_secret=os.environ.get('GITHUB_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)
