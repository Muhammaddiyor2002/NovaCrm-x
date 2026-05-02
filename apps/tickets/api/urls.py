from __future__ import annotations

from rest_framework.routers import DefaultRouter

from .views import TicketReplyViewSet, TicketViewSet

app_name = "tickets"

router = DefaultRouter()
router.register("tickets", TicketViewSet, basename="ticket")
router.register("replies", TicketReplyViewSet, basename="ticket-reply")

urlpatterns = router.urls
