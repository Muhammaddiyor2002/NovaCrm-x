---
name: testing-novacrm-x
description: Test the NovaCRM X Django/DRF app end-to-end. Use whenever testing PRs in Muhammaddiyor2002/NovaCrm-x — covers local dev server setup (without Redis/Postgres), seed data, the golden-path UI flow, and known sharp edges.
---

# Testing NovaCRM X

NovaCRM X is a multi-tenant Django 5 + DRF SaaS CRM. The repo ships everything needed to run locally without Redis or Postgres — but only if you use the dev settings.

## Local dev server setup

```bash
cd /home/ubuntu/repos/novacrm-x
python -m venv .venv  # if not already created
source .venv/bin/activate
pip install -e .  # or: pip install -r requirements.txt

export DJANGO_SETTINGS_MODULE=novacrm.settings.dev
export DATABASE_URL=sqlite:///dev.sqlite3
export SECRET_KEY=devsecret
export DJANGO_DEBUG=true

python manage.py migrate --noinput
python manage.py seed_demo
nohup python manage.py runserver 0.0.0.0:8000 > /tmp/runserver.log 2>&1 &
```

**Do NOT use `novacrm.settings.test` for the runserver.** Test settings point at `test.sqlite3`, which pytest truncates to 0 bytes when it runs. The dashboard will then 500 with `no such table: accounts_user`. Always use `novacrm.settings.dev`.

## What `seed_demo` produces

- Admin: `admin@novacrm.local` / `admin1234`
- Tenant: "Acme Inc." (slug `acme`), 14-day trial
- Pipeline "Sales" with 6 stages: Qualification, Discovery, Proposal, Negotiation, Closed Won, Closed Lost
- 3 deals in Qualification: New logo — Soylent ($15k), Renewal — Initech ($10k), Beta deal — Globex ($5k) → Pipeline Value $30,000
- 5 companies: Globex, Initech, Soylent, Hooli, Pied Piper (all "Software")
- **2 contacts** (only — Hank Scorpio + Mindy Simmons at Globex). NOT 10. Update assertions accordingly.
- 5 leads: Lead 0..Lead 4 with scores 50..54 (descending sort)
- 3 tasks: Globex follow-up (High), Initech proposal (Normal), Pied Piper case study (Low)

## Golden-path UI flow (use this for runtime PR verification)

1. `http://localhost:8000/` — landing page. H1: "The CRM your sales team will actually love."
2. Click **Sign in** (top-right) → `/login/`
3. Email `admin@novacrm.local`, password `admin1234`, click **Sign in** → must redirect to `/dashboard/`
4. Dashboard KPI grid: Open Deals=3, Pipeline Value=$30000, Companies=5, Contacts=2, Total Leads=5
5. Sidebar → Customers → 5 companies + 2 contacts
6. Sidebar → Leads → 5 leads sorted by score desc (54..50)
7. Sidebar → Deals → 6-column Kanban, 3 cards in Qualification
8. Sidebar → Tasks → 3 rows
9. `http://localhost:8000/api/v1/docs/` — Swagger UI (200, full endpoint list)
10. `http://localhost:8000/api/v1/schema/` — OpenAPI YAML (`application/vnd.oai.openapi`, browser will download as `NovaCRM X API.yaml`, ~125 KB)

## Known sharp edges

- **drf-spectacular Swagger needs the namespaced URL.** Routes are mounted under `include((api_v1_patterns, "v1"))`, so `SpectacularSwaggerView`/`SpectacularRedocView` must be passed `url_name="v1:schema"`. Without that, `/api/v1/docs/` and `/api/v1/redoc/` 500 with `NoReverseMatch: 'schema' not found`. Regression test in `tests/test_smoke.py::test_swagger_url_name_is_namespaced`.
- **Debug toolbar.** `dev.py` auto-adds `debug_toolbar` middleware if the package is installed. `novacrm/urls.py` therefore conditionally includes `debug_toolbar.urls` when `DEBUG and 'debug_toolbar' in INSTALLED_APPS`. If you ever delete that block, every page in dev will 500 with `NoReverseMatch: 'djdt' is not a registered namespace`. The DjDT tab will show on the right edge of every screenshot — that's expected, not a UI bug.
- **Redis/Postgres are NOT needed in dev.** `dev.py` overrides `CACHES` to LocMemCache, `CHANNEL_LAYERS` to in-memory, and runs Celery eager. Without these, drf-spectacular's schema-cache call will 500 with `Error -3 connecting to redis:6379`.
- **Tenant resolution after JWT auth.** Middleware can't resolve tenant before DRF auth runs (`request.user` is anonymous). The fix is `apps/tenants/middleware.resolve_tenant(request)`, which permission classes call lazily after auth. If a permission test 403s with "You don't have access to this workspace", check that `IsTenantMember._ensure_tenant` is being called.
- **No ArrayField with SQLite.** `Contact.tags` uses `JSONField`, not `ArrayField`, so SQLite (dev/test) works.

## Standard CI commands

```bash
ruff check .
black --check .
python manage.py makemigrations --check --dry-run
pytest -q
```

All four must be green. CI runs the same job in `.github/workflows/ci.yml`.

## Devin Secrets Needed

None for the golden-path flow — everything works with the seeded admin and the in-memory dev cache.

Future work that *would* require secrets:
- `STRIPE_SECRET_KEY` + `STRIPE_PUBLISHABLE_KEY` (test mode) for billing checkout
- `OPENAI_API_KEY` for the OpenAI provider in `apps/ai/providers/openai_provider.py`
- SMTP credentials if you want to test the email verification flow against a real inbox
