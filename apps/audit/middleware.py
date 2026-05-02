"""Stash request meta (IP, user agent) into context for audit signals."""

from __future__ import annotations

from django.utils.deprecation import MiddlewareMixin

from apps.core.context import set_audit_meta


class AuditContextMiddleware(MiddlewareMixin):
    def process_request(self, request) -> None:
        set_audit_meta(
            {
                "ip": _client_ip(request),
                "user_agent": request.META.get("HTTP_USER_AGENT", "")[:255],
            }
        )

    def process_response(self, request, response):
        set_audit_meta(None)
        return response


def _client_ip(request) -> str | None:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
