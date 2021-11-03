import os
from dotenv import load_dotenv

load_dotenv('config.env')

BASE_DIR = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
PROJECT_NAME = 'Anti-Freelancer'
SERVER_AUTH_BACKEND = 'http://localhost:8000/'
SERVER_EMAIL = 'http://localhost:8003/'

API = 'api/v1'
SERVER_MAIN_BACKEND = 'http://localhost:8001/'

CLIENT_NAME = 'main'

SERVER_USER_EMAIL = os.environ.get('SERVER_EMAIL')
SERVER_USER_USERNAME = os.environ.get('SERVER_USERNAME')
SERVER_USER_PASSWORD = os.environ.get('SERVER_PASSWORD')

LOGIN_URL = f'{SERVER_AUTH_BACKEND}{API}/login'

TEST = os.environ.get('TEST', 0)
DOCKER = os.environ.get('DOCKER', 0)

DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

MEDIA_ROOT = 'media/'

if int(DOCKER):
    SERVER_AUTH_BACKEND = 'http://auth:8000/'
    SERVER_EMAIL = 'http://email:8003/'

if int(TEST):
    DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}_test'
    MEDIA_ROOT = 'media/tests/'
