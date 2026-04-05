from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import Invitation, Membership, Organization
from .policies import is_org_admin_or_owner, is_org_member, is_org_owner
from .serializers import (
    InvitationCreateSerializer,
    InvitationSerializer,
    MembershipRoleUpdateSerializer,
    MembershipSerializer,
    OrganizationSerializer,
)


from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.response import Response
from rest_framework import status
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
    
class OrganizationInvitationListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return InvitationCreateSerializer
        return InvitationSerializer

    def get_organization(self):
        return get_object_or_404(Organization, id=self.kwargs["org_id"])

    def _assert_admin_or_owner(self):
        org_id = self.kwargs["org_id"]
        if not is_org_admin_or_owner(self.request.user, org_id):
            raise PermissionDenied("Forbidden")

    def get_queryset(self):
        self._assert_admin_or_owner()
        return Invitation.objects.filter(
            organization_id=self.kwargs["org_id"]
        ).order_by("-created_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = self.get_organization()
        return context

    def perform_create(self, serializer):
        self._assert_admin_or_owner()
        serializer.save()


class InvitationAcceptView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvitationSerializer
    
    @extend_schema(request=None, responses={200: InvitationSerializer})
    def post(self, request, *args, **kwargs):
        invitation = get_object_or_404(Invitation, token=kwargs["token"])

        if request.user.email.lower().strip() != invitation.email:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        if invitation.status != Invitation.Status.PENDING:
            return Response(
                {"detail": "This invitation has already been processed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if invitation.expires_at <= timezone.now():
            invitation.status = Invitation.Status.EXPIRED
            invitation.save(update_fields=["status", "updated_at"])
            return Response(
                {"detail": "This invitation is expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            membership, created = Membership.objects.get_or_create(
                user=request.user,
                organization=invitation.organization,
                defaults={"role": invitation.role, "is_active": True},
            )

            if not created and membership.is_active:
                return Response(
                    {"detail": "You are already an active member of this organization."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not created:
                membership.role = invitation.role
                membership.is_active = True
                membership.save(update_fields=["role", "is_active"])

            invitation.status = Invitation.Status.ACCEPTED
            invitation.save(update_fields=["status", "updated_at"])

        return Response(InvitationSerializer(invitation).data, status=status.HTTP_200_OK)


class InvitationDeclineView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvitationSerializer
    
    @extend_schema(request=None, responses={200: InvitationSerializer})

    def post(self, request, *args, **kwargs):
        invitation = get_object_or_404(Invitation, token=kwargs["token"])

        if request.user.email.lower().strip() != invitation.email:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        if invitation.status != Invitation.Status.PENDING:
            return Response(
                {"detail": "This invitation has already been processed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if invitation.expires_at <= timezone.now():
            invitation.status = Invitation.Status.EXPIRED
            invitation.save(update_fields=["status", "updated_at"])
            return Response(
                {"detail": "This invitation is expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation.status = Invitation.Status.DECLINED
        invitation.save(update_fields=["status", "updated_at"])
        return Response(InvitationSerializer(invitation).data, status=status.HTTP_200_OK)
    
    
    