from rest_framework import generics, permissions
from .serializers import OrganizationSerializer
from .models import Organization, Membership
from django.db import transaction

# Create your views here.

class OrganizationListCreateView(generics.ListCreateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Organization.objects.filter(memberships__user=self.request.user, memberships__is_active=True).distinct().order_by('name')
    
    @transaction.atomic
    def perform_create(self, serializer):
        organization = serializer.save(created_by=self.request.user)
        Membership.objects.create(user=self.request.user,organization=organization,role=Membership.Role.OWNER,is_active=True)