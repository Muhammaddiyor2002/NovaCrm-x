from __future__ import annotations

from rest_framework.routers import DefaultRouter

from .views import DealViewSet, PipelineViewSet, StageViewSet

app_name = "deals"

router = DefaultRouter()
router.register("pipelines", PipelineViewSet, basename="pipeline")
router.register("stages", StageViewSet, basename="stage")
router.register("deals", DealViewSet, basename="deal")

urlpatterns = router.urls
