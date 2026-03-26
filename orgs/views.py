from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Organization, Membership
from .serializers import OrganizationSerializer, MembershipSerializer, MembershipRoleUpdateSerializer
from .policies import is_org_member, is_org_admin_or_owner, is_org_owner
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
        
class OrganizationMembershipListView(generics.ListAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        org_id = self.kwargs["org_id"]
        if not is_org_member(self.request.user, org_id):
            return Membership.objects.none()
        return Membership.objects.filter(
            organization_id=org_id, is_active= True 
        ).select_related("user").order_by("joined_at")
        
        
class OrganizationMembershipDetailView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MembershipSerializer
    
    def get_serializer_class(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return MembershipRoleUpdateSerializer
        return MembershipSerializer
    
    def get_object(self):
        org_id = self.kwargs["org_id"]
        membership_id = self.kwargs["membership_id"]
        return get_object_or_404(
            Membership,
            id=membership_id,
            organization_id=org_id,
            is_active=True,
        )

    def patch(self, request, *args, **kwargs):
        org_id = kwargs["org_id"]

        if not is_org_admin_or_owner(request.user, org_id):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        target = self.get_object()
        actor = Membership.objects.get(
            user=request.user,
            organization_id=org_id,
            is_active=True
        )

        # admin cannot modify owner
        if actor.role == Membership.Role.ADMIN and target.role == Membership.Role.OWNER:
            return Response({"detail": "Admins cannot modify owner."}, status=status.HTTP_403_FORBIDDEN)

        serializer = MembershipRoleUpdateSerializer(target, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(MembershipSerializer(target).data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        org_id = kwargs["org_id"]

        if not is_org_admin_or_owner(request.user, org_id):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        target = self.get_object()

        if target.user_id == request.user.id and target.role == Membership.Role.OWNER:
            return Response({"detail": "Owner cannot remove self."}, status=status.HTTP_400_BAD_REQUEST)

        if target.role == Membership.Role.OWNER and not is_org_owner(request.user, org_id):
            return Response({"detail": "Only owner can remove owner."}, status=status.HTTP_403_FORBIDDEN)

        target.is_active = False
        target.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)