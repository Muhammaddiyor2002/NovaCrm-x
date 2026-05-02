"""Development settings."""

from __future__ import annotations

from .base import *  # noqa: F401,F403
from .base import INSTALLED_APPS, MIDDLEWARE, env  # noqa: F401

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Console email
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")

# Permissive CORS in dev
CORS_ALLOW_ALL_ORIGINS = True

INTERNAL_IPS = ["127.0.0.1"]

# Debug toolbar (only loaded if installed; safe in CI without the package)
try:  # pragma: no cover - dev-only
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
except ImportError:
    pass
