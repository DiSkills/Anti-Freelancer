from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.categories.routers import categories_router
from config import PROJECT_NAME, API

app = FastAPI(
    title=PROJECT_NAME,
    version='0.1.0',
    description='Main Service Anti-Freelancer by Counter',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(categories_router, prefix=f'/{API}/categories')
