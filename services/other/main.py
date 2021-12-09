import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.feedback.routers import feedbacks_router
from app.review.routers import review_router
from config import PROJECT_NAME, API, VERSION, CLIENT_NAME
from db import engine, Base

app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION,
    description='Feedbacks and Reviews Service Anti-Freelancer',
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


app.include_router(feedbacks_router, prefix=f'/{API}/feedbacks')
app.include_router(review_router, prefix=f'/{API}/reviews')
