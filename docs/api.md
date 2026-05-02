# API reference

NovaCRM X exposes a versioned REST API at `/api/v1/`. Interactive docs live at
`/api/v1/docs/` (Swagger UI) and `/api/v1/redoc/` (Redoc), backed by an
OpenAPI 3.0 schema at `/api/v1/schema/`.

## Authentication

```http
POST /api/v1/auth/login/
{
  "email": "alice@example.com",
  "password": "supersecret"
}
```

Returns `{"access": "<jwt>", "refresh": "<jwt>"}`. Send the access token as
`Authorization: Bearer <jwt>` on subsequent requests.

Tokens are short-lived (15 min) — refresh via `POST /api/v1/auth/token/refresh/`.

## Tenant scope

Every authenticated request resolves the active tenant from:

1. `X-Tenant-Id: <uuid>` header (must be a tenant the user belongs to)
2. The user's default `Membership`

Use the header to switch between workspaces a user is part of.

## Resource overview

| Resource | List endpoint | Notes |
| --- | --- | --- |
| Users (self) | `GET /api/v1/auth/me/` | |
| Tenants | `GET /api/v1/tenants/tenants/me/` | The active workspace |
| Memberships | `GET /api/v1/tenants/memberships/` | |
| Roles | `GET /api/v1/rbac/roles/` | RBAC |
| Companies | `GET /api/v1/customers/companies/` | |
| Contacts | `GET /api/v1/customers/contacts/` | |
| Leads | `GET /api/v1/leads/` | + `POST {id}/score/` and `POST {id}/convert/` |
| Pipelines | `GET /api/v1/deals/pipelines/` | |
| Stages | `GET /api/v1/deals/stages/` | |
| Deals | `GET /api/v1/deals/deals/` | + `POST {id}/move/` (Kanban move) |
| Tasks | `GET /api/v1/tasks/` | |
| Tickets | `GET /api/v1/tickets/tickets/` | + `replies/` |
| Notifications | `GET /api/v1/notifications/` | + `POST read-all/` |
| Plans | `GET /api/v1/billing/plans/` | Public |
| Subscriptions | `GET /api/v1/billing/subscriptions/` | + `POST checkout/` |
| Audit logs | `GET /api/v1/audit/logs/` | Tenant admins only |
| AI sentiment | `POST /api/v1/ai/sentiment/` | |
| AI email draft | `POST /api/v1/ai/email/draft/` | |

## Common parameters

- `?page=2&page_size=50` — pagination (max 100)
- `?search=acme` — full-text on configured fields
- `?ordering=-created_at` — sort
- `?<field>=<value>` — django-filter exact match (e.g. `?status=open`)

## Error format

DRF default JSON. HTTP status codes follow REST conventions:

| Status | Meaning |
| --- | --- |
| 400 | Validation error |
| 401 | Missing/expired token |
| 403 | Authenticated but no permission to perform this action |
| 404 | Resource not found *or* not in your tenant |
| 429 | Rate limited |
