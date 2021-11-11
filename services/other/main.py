import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import PROJECT_NAME, DOCKER, MEDIA_ROOT
from db import engine, Base

app = FastAPI(
    title=PROJECT_NAME,
    version='0.1.0',
    description='Advertisement, Feedbacks and Reviews Service Anti-Freelancer',
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
    """ Startup """

    if int(DOCKER):
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    if not os.path.exists(MEDIA_ROOT):
        os.makedirs(MEDIA_ROOT)
