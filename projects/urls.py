from django.urls import path
from .views import ProjectListCreateView, ProjectDetailView
app_name = "projects"

urlpatterns = [
    path("orgs/<int:org_id>/projects/", ProjectListCreateView.as_view(), name="project-list-create"),
    path("orgs/<int:org_id>/projects/<int:project_id>/", ProjectDetailView.as_view(), name="project-detail"),
] 