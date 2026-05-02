from __future__ import annotations

from apps.ai.providers import get_provider


def draft_email(*, recipient_name: str, context: str, tone: str = "professional") -> str:
    provider = get_provider()
    prompt = (
        f"Write a {tone} email to {recipient_name}.\n"
        f"Context / talking points:\n{context}\n\n"
        f"Format: subject line + body, no markdown, no placeholders."
    )
    return provider.complete(prompt=prompt, temperature=0.7).text
