import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))

PROJECT_NAME = os.environ.get('PROJECT_NAME', 'Anti-Freelancer')

API = os.environ.get('API', 'api/v1')
SERVER_AUTH_BACKEND = os.environ.get('SERVER_AUTH_BACKEND', 'http://auth:8000/')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL_BACKEND', 'http://email:7999/')
SERVER_BACKEND = os.environ.get('SERVER_BACKEND', 'http://localhost/')
VERSION = os.environ.get('VERSION', '0.1.0')
CLIENT_NAME = 'other'
SERVER_OTHER_BACKEND = SERVER_BACKEND + CLIENT_NAME + '/'

TEST = os.environ.get('TEST', 0)

LOGIN_URL = os.environ.get('LOGIN_URL', f'{SERVER_AUTH_BACKEND}{API}/login')

# DB
DB_USER = os.environ.get('DB_USER', 'other_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'other_user')
DB_NAME = os.environ.get('DB_NAME', 'other_db')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

COMPLETED = True
NEW = False

if int(TEST):
    DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}_test'
