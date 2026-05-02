"""Test settings — fast, in-memory where possible."""

from __future__ import annotations

from .base import *  # noqa: F401,F403
from .base import env  # noqa: F401

DEBUG = False
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": env.db_url(
        "DATABASE_URL",
        default="sqlite:///"
        + str(__import__("pathlib").Path(__file__).resolve().parent.parent.parent / "test.sqlite3"),
    ),
}

# Use a fast password hasher in tests.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Run Celery tasks synchronously in tests.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Disable channels redis layer for tests.
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

# Use locmem cache.
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# Force AI dummy provider.
AI_PROVIDER = "dummy"
