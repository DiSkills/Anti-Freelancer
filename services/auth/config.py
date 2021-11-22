import os

from authlib.integrations.starlette_client import OAuth

BASE_DIR = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get('SECRET_KEY', 'SECRET_KEY')

PROJECT_NAME = os.environ.get('PROJECT_NAME', 'Anti-Freelancer')
SERVER_BACKEND = os.environ.get('SERVER_BACKEND', 'http://localhost/')
API = os.environ.get('API', 'api/v1')
VERSION = os.environ.get('VERSION', '0.1.0')
CLIENT_NAME = 'auth'
SERVER_AUTH_BACKEND = SERVER_BACKEND + CLIENT_NAME + '/'
SERVER_EMAIL = os.environ.get('SERVER_EMAIL_BACKEND', 'http://email:8003/')

TEST = os.environ.get('TEST', 0)

# DB
DB_USER = os.environ.get('DB_USER', 'auth_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'auth_user')
DB_NAME = os.environ.get('DB_NAME', 'auth_db')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

MEDIA_ROOT = 'media/'

if int(TEST):
    DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}_test'
    MEDIA_ROOT = 'media/tests/'

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 15
RESET_TOKEN_EXPIRE_MINUTES = 15

ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'ADMIN_EMAIL')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'ADMIN_PASSWORD')

SERVER_USER_EMAIL = os.environ.get('SERVER_EMAIL', 'SERVER_EMAIL')
SERVER_USER_USERNAME = os.environ.get('SERVER_USERNAME', 'SERVER_USERNAME')
SERVER_USER_PASSWORD = os.environ.get('SERVER_PASSWORD', 'SERVER_PASSWORD')

SECRET_QIWI_KEY = os.environ.get('SECRET_QIWI_KEY', 'SECRET_QIWI_KEY')
PUBLIC_QIWI_KEY = os.environ.get('PUBLIC_QIWI_KEY', 'PUBLIC_QIWI_KEY')

social_auth = OAuth()
redirect_url = f'{SERVER_AUTH_BACKEND}{API}/github/bind'

social_auth.register(
    name='github',
    client_id=os.environ.get('GITHUB_ID', 'GITHUB_ID'),
    client_secret=os.environ.get('GITHUB_SECRET', 'GITHUB_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)
