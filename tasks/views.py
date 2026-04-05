from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter

from orgs.policies import is_org_admin_or_owner, is_org_member
from projects.models import Project

from .models import Task
from .serializers import TaskSerializer


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "assigned_to", "created_by"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "status"]
    ordering = ["-created_at"]

    def get_project(self):
        return get_object_or_404(
            Project,
            id=self.kwargs["project_id"],
            organization_id=self.kwargs["org_id"],
        )

    def get_queryset(self):
        org_id = self.kwargs["org_id"]
        project_id = self.kwargs["project_id"]

        if not is_org_member(self.request.user, org_id):
            return Task.objects.none()

        return Task.objects.filter(
            project_id=project_id,
            project__organization_id=org_id,
            is_deleted=False,
        ).select_related("project", "created_by", "assigned_to")

    def perform_create(self, serializer):
        org_id = self.kwargs["org_id"]

        if not is_org_member(self.request.user, org_id):
            raise PermissionDenied("You are not a member of this organization.")

        serializer.save(
            project=self.get_project(),
            created_by=self.request.user,
        )


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        org_id = self.kwargs["org_id"]
        project_id = self.kwargs["project_id"]

        if not is_org_member(self.request.user, org_id):
            return Task.objects.none()

        return Task.objects.filter(
            project_id=project_id,
            project__organization_id=org_id,
            is_deleted=False,
        ).select_related("project", "created_by", "assigned_to")

    def get_object(self):
        return get_object_or_404(self.get_queryset(), id=self.kwargs["task_id"])

    def _can_edit(self, task):
        org_id = self.kwargs["org_id"]
        user = self.request.user

        if is_org_admin_or_owner(user, org_id):
            return True

        return task.created_by_id == user.id or task.assigned_to_id == user.id

    def perform_update(self, serializer):
        task = self.get_object()
        if not self._can_edit(task):
            raise PermissionDenied("You do not have permission to update this task.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self._can_edit(instance):
            raise PermissionDenied("You do not have permission to delete this task.")
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted", "updated_at"])
