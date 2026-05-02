# Production deployment

NovaCRM X ships with a production `docker-compose.prod.yml` that wires up
Postgres, Redis, Gunicorn, Celery worker, and Nginx.

## Required environment variables

| Variable | Required | Notes |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | yes | Generate with `python -c 'import secrets; print(secrets.token_urlsafe(64))'`. |
| `DJANGO_ALLOWED_HOSTS` | yes | Comma-separated list of hostnames. |
| `DATABASE_URL` | yes | `postgres://user:pass@host:5432/db`. Override the bundled Postgres if using a managed DB. |
| `REDIS_URL` | yes | Used for cache + Channels. |
| `CELERY_BROKER_URL` | yes | Usually the same Redis instance. |
| `SENTRY_DSN` | optional | Enables error reporting in `prod` settings. |
| `STRIPE_API_KEY` / `STRIPE_WEBHOOK_SECRET` | optional | Enables real Stripe billing flow. |
| `OPENAI_API_KEY` | optional | Required only when `AI_PROVIDER=openai`. |
| `FIELD_ENCRYPTION_KEY` | yes | base64-encoded Fernet key. **Do not** reuse the dev fallback. |

## Spinning up

```bash
cp .env.example .env.prod
# Edit .env.prod with real values

docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

The Nginx container proxies port 80 to Gunicorn. Terminate TLS with a managed
load balancer (Cloudflare, ALB, fly.io edge, etc.) or extend the bundled Nginx
config with an ACME / Let's Encrypt sidecar.

## Backups

```bash
docker compose exec postgres pg_dump -U novacrm novacrm | gzip > backup-$(date +%F).sql.gz
```

Restore:

```bash
gunzip -c backup-2026-05-02.sql.gz | docker compose exec -T postgres psql -U novacrm novacrm
```

## CI/CD

`.github/workflows/ci.yml` runs:

- `ruff check`
- `black --check`
- `python manage.py makemigrations --check --dry-run`
- `pytest --cov=apps`

Extend it with deployment jobs (e.g. SSH-rsync to a VPS, fly deploy, ECS update,
or k8s rollout) once your target environment is provisioned.
