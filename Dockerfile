FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/

COPY requirements.txt .
RUN uv pip install -r requirements.txt --system

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]