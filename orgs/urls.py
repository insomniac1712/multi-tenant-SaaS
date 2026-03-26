from django.urls import path
from .views import OrganizationListCreateView, OrganizationMembershipListView, OrganizationMembershipDetailView

urlpatterns = [
    path("", OrganizationListCreateView.as_view(), name="org-list-create"),
    path("<int:org_id>/members/", OrganizationMembershipListView.as_view(), name="org-members-list"),
    path("<int:org_id>/members/<int:membership_id>/", OrganizationMembershipDetailView.as_view(), name="org-member-detail"),
]