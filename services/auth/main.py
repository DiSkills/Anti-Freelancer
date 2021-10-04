from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth_router
from config import PROJECT_NAME, API

app = FastAPI(
    title=PROJECT_NAME,
    version='0.1.0',
    description='Freelance by Counter',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth_router, prefix=f'/{API}')
