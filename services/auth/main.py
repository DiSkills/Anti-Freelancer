import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth_router
from config import PROJECT_NAME, API, MEDIA_ROOT

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


@app.on_event('startup')
async def startup():
    if not os.path.exists(MEDIA_ROOT):
        os.makedirs(MEDIA_ROOT)

app.include_router(auth_router, prefix=f'/{API}')
