# NovaCRM X

> Enterprise-grade, multi-tenant, AI-powered CRM platform built with Django.

NovaCRM X is a production-ready foundation for a SaaS CRM that competes with Salesforce, HubSpot,
Zoho, Monday.com, and Pipedrive. It ships with multi-tenancy, RBAC, a modular CRM core (Customers,
Contacts, Leads, Deals, Tasks, Tickets, Invoices), a versioned REST API, a pluggable AI service
layer, Celery/Redis async jobs, and a Docker-first deployment story.

[![CI](https://github.com/Muhammaddiyor2002/novacrm-x/actions/workflows/ci.yml/badge.svg)](https://github.com/Muhammaddiyor2002/novacrm-x/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.x-darkgreen)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## Highlights

- **Multi-tenant SaaS engine** — Tenant isolation via shared schema with row-level scoping middleware.
- **Authentication** — JWT (SimpleJWT) + Session, MFA-ready, email verification, password reset.
- **RBAC** — Custom roles with granular permissions enforced at API and template layers.
- **CRM Core** — Customers, Contacts, Leads, Deals (Kanban pipeline), Tasks, Tickets, Invoices, Notes.
- **API v1** — DRF viewsets, OpenAPI/Swagger via drf-spectacular, pagination, filtering, search.
- **AI layer** — Pluggable provider interface (`OpenAIProvider`, `LocalLLMProvider`) for lead scoring,
  sentiment analysis, email drafting, smart search, next-best-action.
- **Async** — Celery + Redis for background jobs; Channels-ready for realtime notifications.
- **Billing** — Stripe subscription scaffolding (plans, checkout sessions, webhooks).
- **Frontend** — Server-rendered Django templates with HTMX + Alpine.js + Tailwind CSS for a premium
  dashboard feel without an SPA build pipeline. (React/Next.js alternative documented.)
- **Observability** — Structured logging, Sentry hook, Prometheus metrics endpoint.
- **Quality** — Type hints, ruff, black, mypy, pytest with factory-boy, coverage gating.
- **Deploy** — Dockerfile, docker-compose (dev + prod), Nginx, Gunicorn, GitHub Actions CI.

## Quickstart (Docker)

```bash
git clone https://github.com/Muhammaddiyor2002/novacrm-x.git
cd novacrm-x
cp .env.example .env
docker compose up --build
```

Then visit:

- App:        <http://localhost:8000>
- API docs:   <http://localhost:8000/api/v1/docs/>
- Admin:      <http://localhost:8000/admin/>

Default super admin (created by `make seed`):

| Email                 | Password    |
| --------------------- | ----------- |
| `admin@novacrm.local` | `admin1234` |

## Local development (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env
export $(cat .env | xargs)   # or use direnv
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Documentation

| Doc                                                  | What's inside                                      |
| ---------------------------------------------------- | -------------------------------------------------- |
| [docs/architecture.md](docs/architecture.md)         | High-level architecture, module breakdown, ERD     |
| [docs/erd.md](docs/erd.md)                           | Per-table column-level schema                      |
| [docs/install.md](docs/install.md)                   | Local & Docker setup                               |
| [docs/deployment.md](docs/deployment.md)             | Production deployment (compose, env, backups)      |
| [docs/api.md](docs/api.md)                           | REST API reference & examples                      |

## Tech stack

| Layer        | Choice                                                    |
| ------------ | --------------------------------------------------------- |
| Language     | Python 3.12+                                              |
| Framework    | Django 5.x, Django REST Framework, Channels               |
| Async tasks  | Celery + Redis                                            |
| Database     | PostgreSQL 16                                             |
| Frontend     | Django templates + HTMX + Alpine.js + Tailwind CSS        |
| AI           | Pluggable provider (OpenAI / local LLM)                   |
| Billing      | Stripe                                                    |
| Container    | Docker, docker-compose                                    |
| Web server   | Gunicorn behind Nginx                                     |
| CI/CD        | GitHub Actions                                            |
| Monitoring   | Sentry, Prometheus client, structured JSON logs           |
| Testing      | pytest, pytest-django, factory-boy, coverage              |
| Linting      | ruff, black, mypy                                         |

## Project layout

```
novacrm-x/
├── apps/
│   ├── accounts/          # Custom user model, MFA, email verification
│   ├── tenants/           # Multi-tenant engine (Tenant, Membership, middleware)
│   ├── rbac/              # Roles, permissions, scoping
│   ├── customers/         # Customers, Companies, Contacts
│   ├── leads/             # Leads, scoring, conversion
│   ├── deals/             # Pipelines, Stages, Deals, Quotes
│   ├── tasks/             # Tasks, Calendar, Reminders
│   ├── tickets/           # Support desk
│   ├── billing/           # Subscriptions, Plans, Invoices, Stripe webhooks
│   ├── notifications/     # In-app notifications, activity feed
│   ├── ai/                # Pluggable AI providers + use-cases
│   ├── audit/             # AuditLog, change tracking
│   ├── core/              # Base models, mixins, common utilities
│   └── dashboard/         # HTMX server-rendered UI
├── novacrm/               # Django project (settings, urls, wsgi, asgi)
│   └── settings/          # base.py, dev.py, prod.py, test.py
├── deploy/
│   ├── docker/            # Dockerfile, entrypoint
│   ├── nginx/             # Nginx config
│   └── compose/           # docker-compose.yml, prod.yml
├── docs/                  # Architecture, install, deployment, API, manuals
├── requirements/          # base.txt, dev.txt, prod.txt
├── scripts/               # backup, restore, seed
├── tests/                 # Pytest suites (unit, integration, api)
├── manage.py
├── pyproject.toml
└── README.md
```

## Roadmap

See [docs/roadmap.md](docs/roadmap.md) for the full phased plan. Status of this PR:

- [x] Phase 1 — Architecture, blueprint, folder structure
- [x] Phase 2 — Django setup, models, migrations
- [x] Phase 3 — Auth + multi-tenant + RBAC
- [x] Phase 4 — REST API v1 (read/write for core entities)
- [x] Phase 5 — HTMX dashboard (landing, auth, dashboard, customers, deals, tasks)
- [x] Phase 6 — AI service layer with pluggable provider
- [x] Phase 7 — Pytest suite scaffolding
- [x] Phase 8 — Docker, compose, Nginx, GitHub Actions CI
- [ ] Phase 9 — Production hardening (rate limits tuning, full observability, blue/green deploy, ML model training pipelines)

## License

MIT
