"""Project-wide tiny views (health check, etc.)."""

from __future__ import annotations

from django.db import connection
from django.http import JsonResponse


def healthz(request) -> JsonResponse:
    """Liveness/readiness probe.

    Returns 200 with {"status": "ok"} when the database is reachable;
    503 otherwise.
    """
    db_ok = True
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
    except Exception:  # pragma: no cover - environment-dependent
        db_ok = False
    status = 200 if db_ok else 503
    return JsonResponse({"status": "ok" if db_ok else "degraded", "db": db_ok}, status=status)
