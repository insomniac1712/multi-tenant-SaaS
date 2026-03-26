from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Membership, Organization


class BaseOrgTestCase(APITestCase):
    def setUp(self):
        user_model = get_user_model()

        self.owner_user = user_model.objects.create_user(
            username="owner", email="owner@test.com", password="ownerpass123"
        )
        self.member_user = user_model.objects.create_user(
            username="member", email="member@test.com", password="memberpass123"
        )
        self.outsider_user = user_model.objects.create_user(
            username="outsider", email="outsider@test.com", password="outsiderpass123"
        )

        self.organization = Organization.objects.create(
            name="Acme Org",
            created_by=self.owner_user,
        )
        self.owner_membership = Membership.objects.create(  
            user=self.owner_user,
            organization=self.organization,
            role=Membership.Role.OWNER,
        )
        self.member_membership = Membership.objects.create(
            user=self.member_user,
            organization=self.organization,
            role=Membership.Role.MEMBER,
        )

    def _auth(self, user):
        self.client.force_authenticate(user=user)


class OrganizationTests(BaseOrgTestCase):
    def test_create_organization(self):
        self._auth(self.outsider_user)
        url = reverse("org-list-create")

        response = self.client.post(url, {"name": "New Org"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_org = Organization.objects.get(name="New Org")
        created_membership = Membership.objects.get(
            user=self.outsider_user,
            organization=created_org,
        )
        self.assertEqual(created_membership.role, Membership.Role.OWNER)
        self.assertTrue(created_membership.is_active)

    def test_get_organizations_for_member(self):
        self._auth(self.member_user)
        url = reverse("org-list-create")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.organization.id)


class MembershipTests(BaseOrgTestCase):
    def test_get_members_list_for_member(self):
        self._auth(self.member_user)
        url = reverse("org-members-list", kwargs={"org_id": self.organization.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

    def test_owner_can_change_member_role(self):
        self._auth(self.owner_user)
        url = reverse(
            "org-member-detail",
            kwargs={"org_id": self.organization.id, "membership_id": self.member_membership.id},
        )

        response = self.client.patch(url, {"role": Membership.Role.ADMIN}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.member_membership.refresh_from_db()
        self.assertEqual(self.member_membership.role, Membership.Role.ADMIN)

    def test_member_cannot_change_role(self):
        self._auth(self.member_user)
        url = reverse(
            "org-member-detail",
            kwargs={"org_id": self.organization.id, "membership_id": self.owner_membership.id},
        )

        response = self.client.patch(url, {"role": Membership.Role.MEMBER}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_soft_delete_member(self):
        self._auth(self.owner_user)
        url = reverse(
            "org-member-detail",
            kwargs={"org_id": self.organization.id, "membership_id": self.member_membership.id},
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.member_membership.refresh_from_db()
        self.assertFalse(self.member_membership.is_active)











