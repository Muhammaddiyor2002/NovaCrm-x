from __future__ import annotations

from apps.ai.providers import get_provider
from apps.deals.models import Deal


def next_best_action(deal: Deal) -> str:
    provider = get_provider()
    prompt = (
        f"You are a sales coach. Given this deal:\n"
        f"- Title: {deal.title}\n"
        f"- Stage: {deal.stage.name}\n"
        f"- Amount: {deal.amount} {deal.currency}\n"
        f"- Probability: {deal.probability}%\n"
        f"- Expected close: {deal.expected_close_date}\n\n"
        "Recommend the next best action in 1-2 sentences."
    )
    return provider.complete(prompt=prompt, temperature=0.4).text
