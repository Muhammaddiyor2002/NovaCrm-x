.PHONY: help install dev test lint format migrate seed run docker shell coverage

help:
	@echo "Targets:"
	@echo "  install       Install dev dependencies into a local virtualenv"
	@echo "  migrate       Run Django migrations against your DATABASE_URL"
	@echo "  seed          Run the seed_demo management command"
	@echo "  run           Start the Django dev server"
	@echo "  test          Run pytest"
	@echo "  coverage      Run pytest with coverage report"
	@echo "  lint          Run ruff + black check"
	@echo "  format        Auto-format with black + ruff --fix"
	@echo "  docker        docker compose up -d"

install:
	python -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -r requirements/dev.txt

migrate:
	python manage.py migrate

seed:
	python manage.py seed_demo

run:
	python manage.py runserver

test:
	pytest

coverage:
	pytest --cov=apps --cov-report=term-missing

lint:
	ruff check .
	black --check .

format:
	ruff check . --fix
	black .

docker:
	docker compose up -d --build
