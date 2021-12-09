FROM python:3.9.5

WORKDIR /app

COPY pyproject.toml .
COPY poetry.lock .

RUN pip install poetry

RUN poetry install

COPY . .

EXPOSE 8003
