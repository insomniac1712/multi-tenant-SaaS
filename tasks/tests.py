from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from orgs.models import Membership, Organization
from projects.models import Project
from tasks.models import Task




class TaskSmokeTests(APITestCase):
    def setUp(self):
        User = get_user_model()

        self.owner_user = User.objects.create_user(
            username="owner",
            email="owner@test.com",
            password="ownerpass123",
        )
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="adminpass123",
        )
        self.member_user = User.objects.create_user(
            username="member",
            email="member@test.com",
            password="memberpass123",
        )
        self.outsider_user = User.objects.create_user(
            username="outsider",
            email="outsider@test.com",
            password="outsiderpass123",
        )

        self.organization = Organization.objects.create(
            name="Acme Org",
            created_by=self.owner_user,
        )

        Membership.objects.create(
            user=self.owner_user,
            organization=self.organization,
            role=Membership.Role.OWNER,
        )
        Membership.objects.create(
            user=self.admin_user,
            organization=self.organization,
            role=Membership.Role.ADMIN,
        )
        Membership.objects.create(
            user=self.member_user,
            organization=self.organization,
            role=Membership.Role.MEMBER,
        )

        self.project = Project.objects.create(
            name="Main Project",
            description="smoke tests",
            organization=self.organization,
            created_by=self.owner_user,
        )

    def _auth(self, user):
        self.client.force_authenticate(user=user)

    def _task_detail_url(self, task_id):
        return reverse(
            "tasks:task-detail",
            kwargs={
                "org_id": self.organization.id,
                "project_id": self.project.id,
                "task_id": task_id,
            },
        )

    def _task_list_url(self):
        return reverse(
            "tasks:task-list-create",
            kwargs={
                "org_id": self.organization.id,
                "project_id": self.project.id,
            },
        )

    def _project_detail_url(self):
        return reverse(
            "projects:project-detail",
            kwargs={
                "org_id": self.organization.id,
                "project_id": self.project.id,
            },
        )

    # 1) auth login works
    def test_auth_login_works(self):
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"email": "owner@test.com", "password": "ownerpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    # 2) outsider cannot access another org's project/task
    def test_outsider_cannot_access_other_org_project_and_task(self):
        task = Task.objects.create(
            project=self.project,
            title="Task A",
            description="private",
            status="todo",
            created_by=self.owner_user,
            assigned_to=self.admin_user,
        )

        self._auth(self.outsider_user)

        project_response = self.client.get(self._project_detail_url())
        task_response = self.client.get(self._task_detail_url(task.id))

        self.assertEqual(project_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(task_response.status_code, status.HTTP_404_NOT_FOUND)

    # 3) member cannot edit task they neither created nor are assigned to
    def test_member_cannot_edit_unowned_unassigned_task(self):
        task = Task.objects.create(
            project=self.project,
            title="Task B",
            description="not member-owned",
            status="todo",
            created_by=self.owner_user,
            assigned_to=self.admin_user,
        )

        self._auth(self.member_user)
        response = self.client.patch(
            self._task_detail_url(task.id),
            {"status": "done"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 4) member can edit own task
    def test_member_can_edit_own_task(self):
        task = Task.objects.create(
            project=self.project,
            title="Task C",
            description="member-owned",
            status="todo",
            created_by=self.member_user,
        )

        self._auth(self.member_user)
        response = self.client.patch(
            self._task_detail_url(task.id),
            {"status": "in_progress"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.status, "in_progress")

    # 5) admin/owner can edit any task in org
    def test_admin_and_owner_can_edit_any_task_in_org(self):
        task = Task.objects.create(
            project=self.project,
            title="Task D",
            description="created by member",
            status="todo",
            created_by=self.member_user,
        )

        self._auth(self.admin_user)
        admin_response = self.client.patch(
            self._task_detail_url(task.id),
            {"status": "in_progress"},
            format="json",
        )
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)

        self._auth(self.owner_user)
        owner_response = self.client.patch(
            self._task_detail_url(task.id),
            {"status": "done"},
            format="json",
        )
        self.assertEqual(owner_response.status_code, status.HTTP_200_OK)

        task.refresh_from_db()
        self.assertEqual(task.status, "done")

    # 6) soft delete hides task from task list
    def test_soft_delete_hides_task_from_task_list(self):
        task = Task.objects.create(
            project=self.project,
            title="Task E",
            description="soft delete candidate",
            status="todo",
            created_by=self.owner_user,
        )

        self._auth(self.owner_user)

        delete_response = self.client.delete(self._task_detail_url(task.id))
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        task.refresh_from_db()
        self.assertTrue(task.is_deleted)

        list_response = self.client.get(self._task_list_url())
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data["count"], 0)