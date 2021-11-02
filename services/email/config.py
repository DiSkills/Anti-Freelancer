import os

from dotenv import load_dotenv

load_dotenv('config.env')

BASE_DIR = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))

PROJECT_NAME = 'Anti-Freelancer'

SECRET_KEY = os.environ.get('SECRET_KEY')

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')
