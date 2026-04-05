# Multi-Tenant SaaS Backend

A Django REST API backend for multi-tenant SaaS use cases.

## What this project includes

- JWT authentication (register, login, refresh)
- Organization-based multi-tenancy
- Membership roles (owner, admin, member)
- Invitation flow (create, accept, decline)
- Project management per organization
- Task management per project
- Role-based access control and tenant scoping
- OpenAPI schema + Swagger docs
- PostgreSQL + Docker Compose setup

## Tech stack

- Python 3.13
- Django 4.2
- Django REST Framework
- PostgreSQL
- drf-spectacular (OpenAPI/Swagger)
- Docker + Docker Compose

## Project structure

- `accounts/` authentication and user model
- `orgs/` organizations, memberships, invitations
- `projects/` org-scoped projects
- `tasks/` project-scoped tasks
- `core/` settings, URL routing, ASGI/WSGI

## API docs

When server is running:

- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

Note: root URL (`/`) is not mapped and returns 404 by design.

## Environment variables

Create `.env` in project root.

Example:

```env
DEBUG=True
SECRET_KEY=change-this-to-a-new-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=saas_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=superuser
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

JWT_ACCESS_MINUTES=15
JWT_REFRESH_DAYS=7
```

For Docker runs, `POSTGRES_HOST` is overridden to `db` in `docker-compose.yaml`.

## Run locally (without Docker)

1. Create and activate virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
python manage.py migrate
```

4. Start server:

```bash
python manage.py runserver
```

## Run with Docker

Build and start:

```bash
docker compose up --build
```

Stop without deleting data:

```bash
docker compose down
```

Stop and delete DB volume data:

```bash
docker compose down -v
```

Run Django commands inside container:

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## Current permission model (high level)

- Auth required for API access by default.
- Tenant isolation is enforced by organization membership checks.
- Projects are scoped under org IDs.
- Tasks are scoped under org + project IDs.
- Admin/owner have elevated write access in organization contexts.

## Typical development flow

1. Bring up services (`docker compose up --build`).
2. Open API docs at `/api/docs/`.
3. Register users and obtain JWT tokens.
4. Create organization and memberships/invitations.
5. Create projects and tasks under organization paths.

## Notes

- Keep secrets out of source control (`.env` is ignored).
- Use `.env.example` as a template for collaborators.
