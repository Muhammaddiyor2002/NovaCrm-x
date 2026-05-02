# Local installation

## Option A — Docker (recommended)

```bash
git clone https://github.com/Muhammaddiyor2002/novacrm-x.git
cd novacrm-x
cp .env.example .env
docker compose up -d --build
```

The web container automatically runs migrations and the `seed_demo` command on
first start, so the app is reachable at <http://localhost:8000> with:

- **Admin login**: `admin@novacrm.local` / `admin1234`
- **API docs**: <http://localhost:8000/api/v1/docs/>
- **Django admin**: <http://localhost:8000/admin/>

## Option B — Local Python

Requirements: Python 3.12, PostgreSQL 16, Redis 7.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env

# Edit .env to point at your local Postgres/Redis if needed.
export DJANGO_SETTINGS_MODULE=novacrm.settings.dev

python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Running the test suite

```bash
export DJANGO_SETTINGS_MODULE=novacrm.settings.test
pytest                  # all tests
pytest --cov=apps       # with coverage
```

The `test` settings use a local SQLite database, so no Postgres is required.

## Running Celery & Channels

```bash
celery -A novacrm worker -l info     # in one terminal
celery -A novacrm beat   -l info     # in another (optional)
daphne -p 8001 novacrm.asgi:application   # for WebSockets
```
