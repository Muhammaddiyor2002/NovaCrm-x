from __future__ import annotations

from django.utils import timezone

from apps.customers.api.views import TenantScopedModelViewSet
from apps.tasks.models import Task, TaskStatus

from .serializers import TaskSerializer


class TaskViewSet(TenantScopedModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    search_fields = ("title", "description")
    ordering_fields = ("due_at", "priority", "created_at", "status")
    filterset_fields = ("status", "priority", "assignee", "owner")

    @property
    def required_permission(self) -> str:
        return "tasks.view" if self.action in {"list", "retrieve"} else "tasks.update"

    def perform_update(self, serializer):
        instance: Task = serializer.save()
        if instance.status == TaskStatus.DONE and instance.completed_at is None:
            instance.completed_at = timezone.now()
            instance.save(update_fields=["completed_at"])
        elif instance.status != TaskStatus.DONE and instance.completed_at is not None:
            instance.completed_at = None
            instance.save(update_fields=["completed_at"])
