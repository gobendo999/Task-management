from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Task

User = get_user_model()


class TaskModelAndViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create two distinct users
        self.user1 = User.objects.create_user(
            username='user_alice',
            email='alice@example.com',
            password='Password123!'
        )
        self.user2 = User.objects.create_user(
            username='user_bob',
            email='bob@example.com',
            password='Password123!'
        )

        # Tasks for User 1
        self.task1 = Task.objects.create(
            user=self.user1,
            title="Design landing page",
            description="Create high-fidelity mockups in Figma",
            completed=False
        )
        self.task2 = Task.objects.create(
            user=self.user1,
            title="Configure CI/CD pipeline",
            description="Set up GitHub Actions for automated deployment",
            completed=True
        )

        # Task for User 2
        self.bob_task = Task.objects.create(
            user=self.user2,
            title="Bob secret financial task",
            description="Highly confidential budget for Bob",
            completed=False
        )

    def test_unauthenticated_user_redirected_to_login(self):
        # Accessing task list unauthenticated must redirect to login
        response = self.client.get(reverse('todo:task_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_user_isolation_in_dashboard(self):
        # Alice logs in
        self.client.login(username='user_alice', password='Password123!')
        response = self.client.get(reverse('todo:task_list'))
        self.assertEqual(response.status_code, 200)

        # Alice must see her tasks
        self.assertContains(response, "Design landing page")
        self.assertContains(response, "Configure CI/CD pipeline")
        self.assertEqual(response.context['total_count'], 2)
        self.assertEqual(response.context['completed_count'], 1)
        self.assertEqual(response.context['pending_count'], 1)

        # Alice MUST NOT see Bob's task!
        self.assertNotContains(response, "Bob secret financial task")

    def test_user_cannot_access_or_edit_another_users_task(self):
        # Alice logs in and attempts to edit Bob's task
        self.client.login(username='user_alice', password='Password123!')
        response = self.client.get(reverse('todo:task_update', kwargs={'pk': self.bob_task.pk}))
        # Must return 404 Not Found!
        self.assertEqual(response.status_code, 404)

        # Alice attempts to delete Bob's task
        delete_response = self.client.post(reverse('todo:task_delete', kwargs={'pk': self.bob_task.pk}))
        self.assertEqual(delete_response.status_code, 404)
        self.assertTrue(Task.objects.filter(pk=self.bob_task.pk).exists())

        # Alice attempts to toggle Bob's task
        toggle_response = self.client.post(reverse('todo:task_toggle', kwargs={'pk': self.bob_task.pk}))
        self.assertEqual(toggle_response.status_code, 404)

    def test_task_create_assigns_authenticated_user(self):
        self.client.login(username='user_alice', password='Password123!')
        response = self.client.post(reverse('todo:task_create'), {
            'title': 'New Task by Alice',
            'description': 'Alice specific notes',
            'completed': False
        })
        self.assertRedirects(response, reverse('todo:task_list'))
        created_task = Task.objects.get(title='New Task by Alice')
        self.assertEqual(created_task.user, self.user1)

    def test_task_update_own_task(self):
        self.client.login(username='user_alice', password='Password123!')
        response = self.client.post(reverse('todo:task_update', kwargs={'pk': self.task1.pk}), {
            'title': 'Updated Landing Page Title',
            'description': 'Updated details',
            'completed': True
        })
        self.assertRedirects(response, reverse('todo:task_list'))
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, 'Updated Landing Page Title')
        self.assertTrue(self.task1.completed)

    def test_task_toggle_own_task(self):
        self.client.login(username='user_alice', password='Password123!')
        response = self.client.post(reverse('todo:task_toggle', kwargs={'pk': self.task1.pk}))
        self.assertRedirects(response, reverse('todo:task_list'))
        self.task1.refresh_from_db()
        self.assertTrue(self.task1.completed)

    def test_task_delete_own_task(self):
        self.client.login(username='user_alice', password='Password123!')
        response = self.client.post(reverse('todo:task_delete', kwargs={'pk': self.task1.pk}))
        self.assertRedirects(response, reverse('todo:task_list'))
        self.assertFalse(Task.objects.filter(pk=self.task1.pk).exists())

    def test_task_toggle_get_not_allowed(self):
        # State-modifying toggle endpoint must reject GET requests with 405 Method Not Allowed
        self.client.login(username='user_alice', password='Password123!')
        response = self.client.get(reverse('todo:task_toggle', kwargs={'pk': self.task1.pk}))
        self.assertEqual(response.status_code, 405)

    def test_task_list_pagination(self):
        # Create 10 more tasks for Alice (total 12 tasks, paginated by 8 per page)
        self.client.login(username='user_alice', password='Password123!')
        for i in range(10):
            Task.objects.create(user=self.user1, title=f"Bulk Task {i}")

        response = self.client.get(reverse('todo:task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['page_obj'].has_other_pages())
        self.assertEqual(len(response.context['tasks']), 8)

