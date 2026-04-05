from django.urls import path

from .views import (
    InvitationAcceptView,
    InvitationDeclineView,
    OrganizationInvitationListCreateView,
    OrganizationListCreateView,
    OrganizationMembershipDetailView,
    OrganizationMembershipListView,
)

urlpatterns = [
    path("", OrganizationListCreateView.as_view(), name="org-list-create"),
    path("<int:org_id>/members/", OrganizationMembershipListView.as_view(), name="org-members-list"),
    path("<int:org_id>/members/<int:membership_id>/", OrganizationMembershipDetailView.as_view(), name="org-member-detail"),
    path("<int:org_id>/invitations/", OrganizationInvitationListCreateView.as_view(), name="org-invitations-list-create"),
    path("invitations/<str:token>/accept/", InvitationAcceptView.as_view(), name="org-invitation-accept"),
    path("invitations/<str:token>/decline/", InvitationDeclineView.as_view(), name="org-invitation-decline"),
]