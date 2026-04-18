# Multi-Tenant SaaS Backend

Backend API for a multi-tenant SaaS application built with Django REST Framework.
The tenant boundary is Organization, and resources are scoped as Organization -> Project -> Task.

## Current Project Status

This project currently includes:

- Authentication with JWT (register, login, refresh)
- Custom user model
- Organization management
- Membership and role-based access (owner, admin, member)
- Invitation flow (create, accept, decline)
- Organization-scoped Project CRUD
- Project-scoped Task CRUD
- Task soft delete support
- API documentation with Swagger/OpenAPI
- Dockerized development setup with PostgreSQL
- Initial smoke tests for critical task and permission flows

## Tech Stack

- Python 3.13
- Django 4.2
- Django REST Framework
- PostgreSQL
- djangorestframework-simplejwt
- django-filter
- drf-spectacular
- Docker and Docker Compose

## API Route Groups

Base prefix: /api/

### Auth

- POST /api/auth/register/
- POST /api/auth/login/
- POST /api/auth/refresh/

### Organizations

- GET /api/orgs/
- POST /api/orgs/
- GET /api/orgs/{org_id}/members/
- PATCH /api/orgs/{org_id}/members/{membership_id}/
- DELETE /api/orgs/{org_id}/members/{membership_id}/
- GET /api/orgs/{org_id}/invitations/
- POST /api/orgs/{org_id}/invitations/
- POST /api/orgs/invitations/{token}/accept/
- POST /api/orgs/invitations/{token}/decline/

### Projects

- GET /api/orgs/{org_id}/projects/
- POST /api/orgs/{org_id}/projects/
- GET /api/orgs/{org_id}/projects/{project_id}/
- PATCH /api/orgs/{org_id}/projects/{project_id}/
- PUT /api/orgs/{org_id}/projects/{project_id}/
- DELETE /api/orgs/{org_id}/projects/{project_id}/

### Tasks

- GET /api/orgs/{org_id}/projects/{project_id}/tasks/
- POST /api/orgs/{org_id}/projects/{project_id}/tasks/
- GET /api/orgs/{org_id}/projects/{project_id}/tasks/{task_id}/
- PATCH /api/orgs/{org_id}/projects/{project_id}/tasks/{task_id}/
- PUT /api/orgs/{org_id}/projects/{project_id}/tasks/{task_id}/
- DELETE /api/orgs/{org_id}/projects/{project_id}/tasks/{task_id}/

### API Docs

- GET /api/docs/
- GET /api/schema/

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies.
3. Create .env using .env.example.
4. Run migrations.
5. Start the server.

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Docker Setup

Build and run:

```bash
docker compose up --build
```

Stop containers:

```bash
docker compose down
```

Stop and remove DB volume data:

```bash
docker compose down -v
```

Run management commands inside the web container:

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## Environment Variables

Create .env in the project root.

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

Notes:

- In Docker, POSTGRES_HOST is overridden to db.
- Use a sufficiently long SECRET_KEY to avoid JWT key length warnings.

## Running Tests

Run all tests:

```bash
python manage.py test
```

Run tests in Docker:

```bash
docker compose exec web python manage.py test
```

## Access URLs

- API base: http://localhost:8000
- Swagger UI: http://localhost:8000/api/docs/
- OpenAPI schema: http://localhost:8000/api/schema/
- Django Admin: http://localhost:8000/admin/

## Permission Model (Current)

- Authenticated access by default
- Tenant isolation enforced through organization membership checks
- Project endpoints scoped by org_id
- Task endpoints scoped by org_id plus project_id
- Elevated actions controlled by role (admin or owner)

## Current Limitations

- Root path / is not mapped (returns 404 by design)
- Invitation delivery is API-only (email sending not integrated yet)
- Coverage is currently smoke-test level, not full module-level coverage
- Production hardening (CI, security profiles, ops tooling) is not finalized

## Next Steps

- Expand automated tests across auth, orgs, projects, and tasks
- Add invitation email sending workflow
- Improve production settings split and security defaults
- Add CI pipeline for lint and test checks
