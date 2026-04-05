from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from orgs.models import Organization
from orgs.policies import is_org_admin_or_owner, is_org_member

from .models import Project
from .serializers import ProjectSerializer

# Create your views here.

class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_organization(self):
        return get_object_or_404(Organization, id=self.kwargs['org_id'])
    
    def get_queryset(self):
        org_id = self.kwargs['org_id']
        if not is_org_member(self.request.user, org_id):
            return Project.objects.none()
        return Project.objects.filter(organization_id=org_id).select_related("organization","created_by")
    
    def perform_create(self, serializer):
        org_id = self.kwargs["org_id"]
        if not is_org_admin_or_owner(self.request.user, org_id):
            raise PermissionDenied("Only admins or ownser can create projects.")
        serializer.save(organization = self.get_organization(), created_by = self.request.user)
        
class ProjectDetailView (generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        org_id = self.kwargs['org_id']
        if not is_org_member(self.request.user, org_id):
            return Project.objects.none()
        return Project.objects.filter(organization_id=org_id).select_related("organization","created_by")
    
    def get_object(self):
        return get_object_or_404(self.get_queryset(), id=self.kwargs['project_id'],)
    
    def perform_update(self, serializer):
        org_id = self.kwargs['org_id']
        if not is_org_admin_or_owner(self.request.user, org_id):
            raise PermissionDenied("Only owners or admin can update projects")
        serializer.save()
        
    def perform_destroy(self, instance):
        org_id = self.kwargs["org_id"]
        if not is_org_admin_or_owner(self.request.user, org_id):
            raise PermissionDenied("Only admins or owner can delete projects.")
        instance.delete()