# NovaCRM X — Architecture

This document captures the high-level architecture, module breakdown, and database design.

## 1. Goals

- **Multi-tenant SaaS** — One deployment serves N tenants, each fully isolated.
- **Modular** — Business domains are independent Django apps that compose through clear interfaces.
- **API-first** — Every UI feature is reachable via versioned REST API.
- **AI-powered** — Pluggable provider abstraction so we can swap OpenAI ↔ local LLM ↔ self-hosted.
- **Production-ready** — Docker, CI, observability, security baked in from day one.

## 2. High-level diagram

```
                           ┌──────────────────────────────┐
   Browser  ──HTTPS──▶     │  Nginx (TLS, gzip, static)   │
                           └──────────────┬───────────────┘
                                          │
              ┌───────────────────────────┴───────────────────────────┐
              │                                                       │
   ┌──────────▼──────────┐                                ┌───────────▼───────────┐
   │  Gunicorn (WSGI)    │  HTTP                          │  Daphne / Uvicorn     │  WebSocket
   │  Django app         │                                │  Channels             │
   └──────────┬──────────┘                                └───────────┬───────────┘
              │                                                       │
              │             ┌────────────────────────────┐            │
              ├────────────▶│  PostgreSQL (primary)      │◀───────────┤
              │             └────────────────────────────┘            │
              │                                                       │
              │             ┌────────────────────────────┐            │
              ├────────────▶│  Redis (cache, queue, ws)  │◀───────────┘
              │             └──────────────┬─────────────┘
              │                            │
              │             ┌──────────────▼─────────────┐
              └────────────▶│  Celery workers + Beat     │
                            └──────────────┬─────────────┘
                                           │
                            ┌──────────────▼─────────────┐
                            │  External: Stripe, SMTP,   │
                            │  OpenAI, S3, Sentry        │
                            └────────────────────────────┘
```

## 3. Multi-tenancy strategy

We use a **shared schema, row-level scoping** model:

- A `Tenant` model represents a customer organization.
- Every business model inherits from `TenantOwnedModel` (in `apps/core/models.py`), which adds a
  non-null `tenant` foreign key.
- A `TenantMiddleware` resolves the active tenant from the authenticated user's `Membership` (or
  from a subdomain in production) and stores it in `request.tenant`.
- A custom `TenantQuerySet` automatically filters by `tenant=request.tenant` via a thread-local
  context. Managers expose both scoped (`objects`) and unscoped (`all_tenants`) queryset entry
  points; the unscoped manager is intentionally only safe to use from staff/admin contexts.
- Permission classes (`apps/rbac/permissions.py`) double-check that any object accessed via the API
  belongs to the request's tenant.

This approach was chosen over schema-per-tenant because it is simpler to operate, cheaper to back
up, and lets us run cross-tenant analytics for the super admin without complex cross-schema joins.
For very large customers we can transparently move them to a dedicated database later via Django's
multi-database routing without changing application code.

## 4. App breakdown

| App              | Responsibility                                                              |
| ---------------- | --------------------------------------------------------------------------- |
| `core`           | Base models (UUID PK, timestamps, soft delete), mixins, common utilities.   |
| `accounts`       | Custom `User` (email login), MFA, email verification, password reset.       |
| `tenants`        | `Tenant`, `Membership`, tenant-resolution middleware, onboarding.           |
| `rbac`           | `Role`, `Permission`, role assignment, DRF permission classes.              |
| `customers`      | `Company`, `Contact`, tags, attachments.                                    |
| `leads`          | `Lead`, lead sources, scoring service, conversion to deal.                  |
| `deals`          | `Pipeline`, `Stage`, `Deal`, `Quote`, forecasting.                          |
| `tasks`          | `Task`, calendar events, reminders, Kanban.                                 |
| `tickets`        | `Ticket`, SLA timers, assignment, customer responses.                       |
| `notifications`  | In-app notifications, activity feed, email/SMS dispatch.                    |
| `billing`        | `Plan`, `Subscription`, `Invoice`, Stripe webhooks.                         |
| `ai`             | `AIProvider` ABC + concrete adapters; use-cases (scoring, sentiment, etc.). |
| `audit`          | `AuditLog`, signal-driven change tracking.                                  |
| `dashboard`      | Server-rendered HTMX UI on top of the API.                                  |

## 5. Data model (ERD summary)

```
User ─┬─< Membership >─┬─ Tenant ─┬─< Role
      │                            ├─< Plan / Subscription / Invoice
      │                            ├─< Company ─< Contact
      │                            ├─< Lead
      │                            ├─< Pipeline ─< Stage ─< Deal
      │                            ├─< Task / Ticket
      │                            ├─< Note (generic)
      │                            ├─< Notification
      │                            └─< AuditLog
      └─< Notification (recipient)
```

All models inherit:

- `id: UUID` (primary key, default uuid4)
- `created_at`, `updated_at` (auto)
- `deleted_at` (nullable; soft delete)
- `tenant: FK Tenant` (for tenant-owned models)

Indexes are declared on every foreign key, on `(tenant, created_at)` for time-series queries, and
on commonly-filtered fields (e.g. `Lead.status`, `Deal.stage`, `Ticket.priority`).

See [erd.md](erd.md) for the full ERD with attributes.

## 6. API design

- Base path: `/api/v1/`
- Authentication: JWT bearer tokens (SimpleJWT) for clients; session auth for the dashboard.
- Pagination: `PageNumberPagination` with `page_size=25` and `page_size=100` max.
- Filtering: `django-filter` for structured filters; DRF `SearchFilter` for free-text search.
- Sorting: `OrderingFilter` with whitelisted fields.
- Errors: structured JSON `{"detail": "...", "errors": {...}}`.
- Schema: `drf-spectacular` exposes OpenAPI 3.1 at `/api/v1/schema/` and Swagger UI at
  `/api/v1/docs/`.
- Rate limits: per-user and per-IP throttling via DRF; tunable via env.
- Webhooks: outbound webhook delivery scaffolded in `apps/notifications/webhooks.py`.

## 7. Authentication & authorization

- **Email-as-username** custom user (`accounts.User`).
- **Password reset** via signed token email.
- **Email verification** required before tenant operations.
- **MFA** via TOTP (django-otp), opt-in per user, enforceable per tenant policy.
- **JWT** access (15 min) + refresh (7 days) tokens.
- **Social login** scaffolded with `django-allauth` (Google, GitHub, Microsoft).
- **RBAC** — `Role` ↔ `Permission` (built-in defaults: `super_admin`, `tenant_owner`, `manager`,
  `sales_rep`, `support_agent`, `accountant`, `read_only`). Custom roles per tenant supported.
- **Audit log** captures every create/update/delete on tenant-owned models via signals.

## 8. AI architecture

- `apps/ai/providers/base.py` defines `BaseAIProvider` with methods like `complete()`,
  `embed()`, `classify()`, `summarize()`.
- Concrete providers: `OpenAIProvider`, `LocalLLMProvider` (HTTP API to a local server),
  `DummyProvider` (returns deterministic values for tests).
- Use-cases live in `apps/ai/usecases/` and orchestrate one or more provider calls:
  `lead_scoring.py`, `sentiment.py`, `email_writer.py`, `meeting_summary.py`,
  `next_best_action.py`, `smart_search.py`, `chatbot.py`.
- The active provider is selected via `settings.AI_PROVIDER` (env-driven).
- All AI calls are async (Celery tasks) and write back to the database, so the UI never blocks on
  external API latency.

## 9. Async & realtime

- **Celery** workers consume tasks from Redis. `celery beat` runs scheduled jobs (lead-scoring
  refresh, daily digest, churn report).
- **Channels** with Redis backend powers a `notifications` consumer that pushes activity-feed
  events to authenticated WebSocket clients.

## 10. Billing

- `Plan` (free, starter, pro, enterprise) declares feature flags and quota limits.
- `Subscription` links `Tenant` to `Plan` and tracks Stripe IDs.
- `Invoice` is a local mirror of Stripe invoices for offline reporting.
- Stripe checkout sessions are created server-side; webhooks update subscription status.
- Quota enforcement happens in DRF permission classes (e.g. max contacts per plan).

## 11. Observability

- **Structured logs** (JSON) via `python-json-logger`, including `tenant_id`, `user_id`,
  `request_id`.
- **Sentry** SDK initialized in production settings.
- **Prometheus** metrics exposed at `/metrics` (django-prometheus).
- **Health check** at `/healthz` (DB + Redis ping).

## 12. Security

- HTTPS-only cookies, `SECURE_*` Django settings enabled in prod.
- CSRF on all unsafe methods (also for the API when used with session auth).
- Argon2 password hasher.
- Brute-force protection via `django-axes`.
- Per-user and per-IP DRF throttling.
- Field-level encryption for sensitive PII (`apps/core/fields.py`) using Fernet keys from env.
- Strict RBAC checks at API layer; permission classes deny by default.
- Dependency scanning in CI (`pip-audit`).

## 13. Deployment

Two compose files:

- `deploy/compose/docker-compose.yml` — dev (single web, postgres, redis, celery, beat).
- `deploy/compose/docker-compose.prod.yml` — prod (Nginx in front, multiple web replicas, healthchecks).

GitHub Actions CI (`.github/workflows/ci.yml`):

1. Lint (ruff, black --check, mypy).
2. Run pytest with coverage.
3. Build Docker image.
4. (Optional) push to registry on `main`.

Backups: `scripts/backup.sh` runs `pg_dump` and uploads to S3; `scripts/restore.sh` reverses.

## 14. Open items / Phase 9

- Multi-region deploy with read replicas
- Schema-per-tenant migration path for whales
- Full ML training pipelines (currently inference-only)
- WhatsApp / SMS providers (architecture is ready, providers TBD)
- Mobile app (React Native, talks to `/api/v1/`)
