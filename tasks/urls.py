from django.urls import path

from .views import TaskDetailView, TaskListCreateView

app_name = "tasks"

urlpatterns = [
    path("orgs/<int:org_id>/projects/<int:project_id>/tasks/",TaskListCreateView.as_view(),name="task-list-create",),
    path("orgs/<int:org_id>/projects/<int:project_id>/tasks/<int:task_id>/",TaskDetailView.as_view(),name="task-detail",),
]