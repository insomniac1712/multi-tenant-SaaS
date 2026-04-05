# Multi-Tenant SaaS Backend

A production-style Django REST backend that models real SaaS collaboration workflows with organization-level tenancy, role-based permissions, and containerized deployment.

## Recruiter Highlights

- Multi-tenant architecture with strict org-level data isolation.
- JWT authentication with refresh flow.
- Role-based access control (owner, admin, member).
- Invitation workflow with token-based accept/decline endpoints.
- Project and task management with tenant-aware route scoping.
- Dockerized local environment with PostgreSQL.
- OpenAPI schema and interactive Swagger documentation.

## Architecture Snapshot

```text
Client (Web/Postman/Swagger)
		|
		v
	Django REST API
		|
		v
	 PostgreSQL DB

Tenant boundary: Organization
Resource hierarchy: Organization -> Project -> Task
```

## Tech stack

- Python 3.13
- Django 4.2
- Django REST Framework
- PostgreSQL
- drf-spectacular (OpenAPI/Swagger)
- Docker + Docker Compose

## Core modules

- `accounts`: custom user model, registration, JWT login/refresh
- `orgs`: organizations, memberships, invitations, role policies
- `projects`: organization-scoped project CRUD
- `tasks`: project-scoped task CRUD with role-aware update/delete rules
- `core`: settings, URL routing, shared framework configuration

## Key API capabilities

- Auth: register, login, refresh token
- Org management: create/list organizations
- Membership controls: list, role update, soft remove
- Invitations: create, accept, decline
- Projects: list/create/detail/update/delete under org routes
- Tasks: list/create/detail/update/delete under org + project routes

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

## Permission model (high level)

- API access requires authentication by default.
- Tenant isolation is enforced through organization membership checks.
- Project data is scoped by `org_id` routes.
- Task data is scoped by `org_id + project_id` routes.
- Elevated write operations are controlled by org role (admin/owner).

## Typical development flow

1. Bring up services (`docker compose up --build`).
2. Open API docs at `/api/docs/`.
3. Register users and obtain JWT tokens.
4. Create organization and memberships/invitations.
5. Create projects and tasks under organization paths.

## Resume-ready bullets

- Built a multi-tenant SaaS backend using Django REST Framework and PostgreSQL with organization-scoped data isolation.
- Implemented JWT-based authentication and role-based authorization (owner/admin/member) for secure access control.
- Designed invitation and membership workflows with token-based onboarding and policy-driven permissions.
- Developed project/task APIs with nested tenant-aware routing and filter/search/order support.
- Containerized the application using Docker Compose for reproducible local setup and deployment readiness.

## Notes

- Keep secrets out of source control (`.env` is ignored).
- Use `.env.example` as a template for collaborators.
