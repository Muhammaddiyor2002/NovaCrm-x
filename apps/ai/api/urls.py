from __future__ import annotations

from django.urls import path

from .views import EmailDraftView, SentimentView

app_name = "ai"

urlpatterns = [
    path("sentiment/", SentimentView.as_view(), name="sentiment"),
    path("email/draft/", EmailDraftView.as_view(), name="email-draft"),
]
