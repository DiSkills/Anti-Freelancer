import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.categories.routers import categories_router
from app.jobs.routers import jobs_router
from config import PROJECT_NAME, API, MEDIA_ROOT, VERSION, CLIENT_NAME
from db import Base, engine

app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION,
    description='Main Service Anti-Freelancer by Counter',
    root_path=f'/{CLIENT_NAME}',
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

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    if not os.path.exists(MEDIA_ROOT):
        os.makedirs(MEDIA_ROOT)

app.include_router(categories_router, prefix=f'/{API}/categories')
app.include_router(jobs_router, prefix=f'/{API}/jobs')
