from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Project, Task

User = get_user_model()


class TaskFlowTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="Strong-test-pass-928!",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="Strong-test-pass-928!",
        )
        self.project = Project.objects.create(
            name="Website Redesign",
            description="Refresh the company website.",
            owner=self.user,
        )
        self.other_project = Project.objects.create(
            name="Private Project",
            owner=self.other_user,
        )
        self.task = Task.objects.create(
            title="Prepare wireframes",
            project=self.project,
            created_by=self.user,
            status=Task.Status.TODO,
            priority=Task.Priority.HIGH,
        )
        self.client.force_login(self.user)


class AuthenticationRequiredTests(TestCase):
    def test_all_workspace_pages_require_login(self):
        paths = [
            reverse("dashboard"),
            reverse("project_list"),
            reverse("project_create"),
            reverse("task_list"),
            reverse("task_create"),
        ]

        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertRedirects(
                    response,
                    f"{reverse('login')}?next={path}",
                )


class ProjectViewTests(TaskFlowTestCase):
    def test_project_list_shows_only_current_users_projects(self):
        response = self.client.get(reverse("project_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)
        self.assertNotContains(response, self.other_project.name)
        self.assertEqual(response.context["total_projects"], 1)

    def test_create_project_assigns_current_user_as_owner(self):
        response = self.client.post(
            reverse("project_create"),
            {"name": "Mobile App", "description": "Build an app."},
        )

        self.assertRedirects(response, reverse("project_list"))
        project = Project.objects.get(name="Mobile App")
        self.assertEqual(project.owner, self.user)

    def test_update_project(self):
        response = self.client.post(
            reverse("project_update", args=[self.project.pk]),
            {"name": "Website Refresh", "description": "Updated scope."},
        )

        self.assertRedirects(response, reverse("project_list"))
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Website Refresh")

    def test_delete_project_on_post(self):
        response = self.client.post(
            reverse("project_delete", args=[self.project.pk])
        )

        self.assertRedirects(response, reverse("project_list"))
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())
        self.assertFalse(Task.objects.filter(project=self.project).exists())

    def test_cannot_view_or_modify_another_users_project(self):
        protected_urls = [
            reverse("project_detail", args=[self.other_project.pk]),
            reverse("project_update", args=[self.other_project.pk]),
            reverse("project_delete", args=[self.other_project.pk]),
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 404)

    def test_dashboard_project_and_task_counts_match_workspace_data(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_projects"], 1)
        self.assertEqual(response.context["total_tasks"], 1)
        self.assertEqual(response.context["todo_tasks"], 1)
        self.assertEqual(response.context["in_progress_tasks"], 0)
        self.assertEqual(response.context["completed_tasks"], 0)

    def test_dashboard_uses_current_username_and_links_to_task_list(self):
        response = self.client.get(reverse("dashboard"))

        self.assertContains(response, self.user.username)
        self.assertContains(response, reverse("task_list"))
        self.assertNotContains(response, "/admin/tasks/task/")
        self.assertContains(response, reverse("logout"))


class TaskViewTests(TaskFlowTestCase):
    def test_task_list_shows_only_tasks_in_current_users_projects(self):
        foreign_task = Task.objects.create(
            title="Other user's task",
            project=self.other_project,
            created_by=self.other_user,
        )

        response = self.client.get(reverse("task_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.title)
        self.assertNotContains(response, foreign_task.title)
        self.assertEqual(response.context["total_tasks"], 1)

    def test_create_task(self):
        response = self.client.post(
            reverse("task_create"),
            {
                "title": "Implement landing page",
                "description": "Create responsive layout.",
                "project": self.project.pk,
                "status": Task.Status.IN_PROGRESS,
                "priority": Task.Priority.MEDIUM,
                "due_date": "2027-01-15",
            },
        )

        self.assertRedirects(response, reverse("task_list"))
        task = Task.objects.get(title="Implement landing page")
        self.assertEqual(task.created_by, self.user)
        self.assertEqual(task.project, self.project)
        self.assertEqual(task.status, Task.Status.IN_PROGRESS)

    def test_task_form_rejects_another_users_project(self):
        response = self.client.post(
            reverse("task_create"),
            {
                "title": "Unauthorized task",
                "description": "Should not be saved.",
                "project": self.other_project.pk,
                "status": Task.Status.TODO,
                "priority": Task.Priority.LOW,
                "due_date": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertFalse(Task.objects.filter(title="Unauthorized task").exists())

    def test_update_task(self):
        response = self.client.post(
            reverse("task_update", args=[self.task.pk]),
            {
                "title": "Prepare final wireframes",
                "description": "Ready for review.",
                "project": self.project.pk,
                "status": Task.Status.DONE,
                "priority": Task.Priority.HIGH,
                "due_date": "",
            },
        )

        self.assertRedirects(response, reverse("task_list"))
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Prepare final wireframes")
        self.assertEqual(self.task.status, Task.Status.DONE)

    def test_delete_task_on_post(self):
        response = self.client.post(reverse("task_delete", args=[self.task.pk]))

        self.assertRedirects(response, reverse("task_list"))
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())

    def test_cannot_view_or_modify_another_users_task(self):
        foreign_task = Task.objects.create(
            title="Foreign task",
            project=self.other_project,
            created_by=self.other_user,
        )
        protected_urls = [
            reverse("task_update", args=[foreign_task.pk]),
            reverse("task_delete", args=[foreign_task.pk]),
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 404)

    def test_search_filters_by_title(self):
        Task.objects.create(
            title="Write API documentation",
            project=self.project,
            created_by=self.user,
        )

        response = self.client.get(reverse("task_list"), {"q": "API"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Write API documentation")
        self.assertNotContains(response, self.task.title)
        self.assertEqual(response.context["total_tasks"], 1)

    def test_status_filter(self):
        Task.objects.create(
            title="Completed task",
            project=self.project,
            created_by=self.user,
            status=Task.Status.DONE,
        )

        response = self.client.get(
            reverse("task_list"),
            {"status": Task.Status.DONE},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Completed task")
        self.assertNotContains(response, self.task.title)

    def test_search_and_status_filters_can_be_combined(self):
        Task.objects.create(
            title="API task done",
            project=self.project,
            created_by=self.user,
            status=Task.Status.DONE,
        )
        Task.objects.create(
            title="API task pending",
            project=self.project,
            created_by=self.user,
            status=Task.Status.TODO,
        )

        response = self.client.get(
            reverse("task_list"),
            {"q": "API", "status": Task.Status.DONE},
        )

        self.assertContains(response, "API task done")
        self.assertNotContains(response, "API task pending")

    def test_task_list_paginates_ten_tasks_per_page(self):
        for number in range(11):
            Task.objects.create(
                title=f"Pagination task {number}",
                project=self.project,
                created_by=self.user,
            )

        first_page = self.client.get(reverse("task_list"))
        second_page = self.client.get(reverse("task_list"), {"page": 2})

        self.assertEqual(first_page.context["page_obj"].paginator.num_pages, 2)
        self.assertEqual(len(first_page.context["tasks"]), 10)
        self.assertEqual(len(second_page.context["tasks"]), 2)

    def test_invalid_page_number_falls_back_to_last_page(self):
        for number in range(11):
            Task.objects.create(
                title=f"Pagination task {number}",
                project=self.project,
                created_by=self.user,
            )

        response = self.client.get(reverse("task_list"), {"page": "not-a-number"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].number, 2)
