import os
from dotenv import load_dotenv

load_dotenv('config.env')

BASE_DIR = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
PROJECT_NAME = 'Anti-Freelancer'
SERVER_AUTH_BACKEND = 'http://localhost:8000/'
SERVER_MAIN_BACKEND = 'http://localhost:8001/'

API = 'api/v1'
SERVER_MESSENGER_BACKEND = 'http://localhost:8002/'

LOGIN_URL = f'{SERVER_AUTH_BACKEND}{API}/login'

TEST = os.environ.get('TEST', 0)

DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

SEND = 'SEND'
SUCCESS = 'SUCCESS'
ERROR = 'ERROR'

if int(TEST):
    DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}_test'
