# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/playwright/python:v1.60.0-jammy

ENV CI=true \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
    && pip install --timeout=120 --upgrade-strategy only-if-needed -r requirements.txt

COPY . .

CMD ["pytest", "tests/"]
