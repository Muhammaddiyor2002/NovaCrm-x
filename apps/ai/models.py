"""Persisted AI artifacts (logs of completions, scores, etc.)."""

from __future__ import annotations

from django.db import models

from apps.core.models import TenantOwnedModel


class AIInvocation(TenantOwnedModel):
    """One record per AI provider call. Used for cost tracking + auditing."""

    use_case = models.CharField(max_length=64)
    provider = models.CharField(max_length=32)
    model = models.CharField(max_length=64, blank=True, default="")
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    latency_ms = models.IntegerField(default=0)
    input = models.JSONField(default=dict, blank=True)
    output = models.JSONField(default=dict, blank=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, default="")

    class Meta(TenantOwnedModel.Meta):
        indexes = [
            models.Index(fields=["tenant", "use_case", "created_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"AIInvocation({self.use_case}, {self.provider})"
