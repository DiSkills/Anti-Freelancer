import os

from dotenv import load_dotenv

load_dotenv('config.env')

BASE_DIR = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))

PROJECT_NAME = 'Anti-Freelancer'

API = 'api/v1'
SERVER_AUTH_BACKEND = 'http://localhost:8000/'

LOGIN_URL = f'{SERVER_AUTH_BACKEND}{API}/login'

SECRET_KEY = os.environ.get('SECRET_KEY')

TEST = os.environ.get('TEST', 0)
DOCKER = os.environ.get('DOCKER', 0)

DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')

if int(TEST):
    DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}_test'

if int(DOCKER):
    SERVER_AUTH_BACKEND = 'http://auth:8000/'
