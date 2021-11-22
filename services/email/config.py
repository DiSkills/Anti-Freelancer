import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))

PROJECT_NAME = os.environ.get('PROJECT_NAME', 'Anti-Freelancer')

API = os.environ.get('API', 'api/v1')
SERVER_AUTH_BACKEND = os.environ.get('SERVER_AUTH_BACKEND', 'http://auth:8000/')
VERSION = os.environ.get('VERSION', '0.1.0')
CLIENT_NAME = 'email'

LOGIN_URL = os.environ.get('LOGIN_URL', f'{SERVER_AUTH_BACKEND}{API}/login')

SECRET_KEY = os.environ.get('SECRET_KEY', 'SECRET_KEY')

TEST = os.environ.get('TEST', 0)

DB_USER = os.environ.get('DB_USER', 'email_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'email_user')
DB_NAME = os.environ.get('DB_NAME', 'email_db')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')

if int(TEST):
    DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}_test'
