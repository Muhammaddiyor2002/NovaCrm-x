"""Field-level encryption (Fernet) for sensitive PII columns."""

from __future__ import annotations

import base64

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models


def _get_cipher() -> Fernet:
    key = settings.FIELD_ENCRYPTION_KEY
    if not key:
        # In dev/test we fall back to a deterministic key so migrations and
        # tests work out of the box. NEVER use this in production.
        key = base64.urlsafe_b64encode(b"novacrm-dev-key-do-not-use-in-prd!!"[:32])
    if isinstance(key, str):
        key = key.encode()
    try:
        return Fernet(key)
    except Exception as exc:  # pragma: no cover - misconfig
        raise ImproperlyConfigured(
            "FIELD_ENCRYPTION_KEY must be a base64-encoded 32-byte Fernet key."
        ) from exc


class EncryptedTextField(models.TextField):
    """A TextField that transparently encrypts/decrypts at the ORM boundary."""

    def from_db_value(self, value, expression, connection):  # noqa: D401
        if value is None:
            return value
        try:
            return _get_cipher().decrypt(value.encode()).decode()
        except (InvalidToken, AttributeError):
            return value  # legacy plaintext

    def to_python(self, value):
        return value

    def get_prep_value(self, value):
        if value is None or value == "":
            return value
        return _get_cipher().encrypt(str(value).encode()).decode()
