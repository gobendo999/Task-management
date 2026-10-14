from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()


class AccountsAuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='johndoe',
            email='john@example.com',
            password='Password123!'
        )

    def test_profile_auto_created_via_signal(self):
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_registration_view_success(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'SecretPass999!',
            'password2': 'SecretPass999!'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(Profile.objects.filter(user__username='newuser').exists())
        self.assertEqual(User.objects.get(username='newuser').email, 'newuser@example.com')

    def test_registration_fails_without_email(self):
        response = self.client.post(reverse('register'), {
            'username': 'noemailuser',
            'email': '',
            'password1': 'SecretPass999!',
            'password2': 'SecretPass999!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='noemailuser').exists())
        self.assertIn('email', response.context['form'].errors)
        self.assertIn('Valid email address is strictly required.', response.context['form'].errors['email'])

    def test_registration_fails_with_invalid_email_format(self):
        # Invalid email format (missing domain dot / malformed)
        response = self.client.post(reverse('register'), {
            'username': 'bademailuser',
            'email': 'bademail@local',
            'password1': 'SecretPass999!',
            'password2': 'SecretPass999!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='bademailuser').exists())

    def test_registration_fails_with_duplicate_email(self):
        # Attempt to register with john@example.com which already belongs to johndoe
        response = self.client.post(reverse('register'), {
            'username': 'anotherjohn',
            'email': 'john@example.com',
            'password1': 'SecretPass999!',
            'password2': 'SecretPass999!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='anotherjohn').exists())
        self.assertIn('email', response.context['form'].errors)
        self.assertIn('An account with this email already exists. Please sign in instead.', response.context['form'].errors['email'])

    def test_password_visibility_toggle_present_in_templates(self):
        # Login page contains password visibility toggle
        login_page = self.client.get(reverse('login'))
        self.assertEqual(login_page.status_code, 200)
        self.assertContains(login_page, 'togglePasswordVisibility')
        self.assertContains(login_page, 'fa-eye')

        # Register page contains password visibility toggle
        register_page = self.client.get(reverse('register'))
        self.assertEqual(register_page.status_code, 200)
        self.assertContains(register_page, 'togglePasswordVisibility')
        self.assertContains(register_page, 'password-match-badge')

    def test_login_and_logout_flow(self):
        # Login
        login_response = self.client.post(reverse('login'), {
            'username': 'johndoe',
            'password': 'Password123!'
        })
        self.assertRedirects(login_response, reverse('todo:task_list'))

        # Logout
        logout_response = self.client.get(reverse('logout'))
        self.assertRedirects(logout_response, reverse('login'))

    def test_profile_view_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_profile_view_and_update(self):
        self.client.login(username='johndoe', password='Password123!')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'johndoe')

        # Update profile
        update_response = self.client.post(reverse('profile'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'johndoe_updated@example.com',
            'bio': 'Software developer',
            'phone': '+1234567890',
            'location': 'Dhaka, Bangladesh',
        })
        self.assertRedirects(update_response, reverse('profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'johndoe_updated@example.com')
        self.assertEqual(self.user.profile.location, 'Dhaka, Bangladesh')

    def test_swagger_ui_endpoint(self):
        response = self.client.get(reverse('swagger-ui'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'swagger-ui')

    def test_api_registration_and_tasks(self):
        # API register with invalid email
        bad_reg = self.client.post(
            reverse('api_register'),
            {'username': 'apibad', 'email': 'notanemail', 'password': 'StrongPassword123!'},
            content_type='application/json'
        )
        self.assertEqual(bad_reg.status_code, 400)

        # API register with valid email
        good_reg = self.client.post(
            reverse('api_register'),
            {'username': 'apiuser', 'email': 'apiuser@example.com', 'password': 'StrongPassword123!'},
            content_type='application/json'
        )
        self.assertEqual(good_reg.status_code, 201)

        # API task CRUD
        self.client.login(username='apiuser', password='StrongPassword123!')
        create_task = self.client.post(
            '/api/tasks/',
            {'title': 'Swagger Test Task', 'description': 'Testing via API'},
            content_type='application/json'
        )
        self.assertEqual(create_task.status_code, 201)
        task_id = create_task.data['id']

        # API toggle task
        toggle_res = self.client.post(f'/api/tasks/{task_id}/toggle/')
        self.assertEqual(toggle_res.status_code, 200)
        self.assertTrue(toggle_res.data['task']['completed'])

    def test_open_redirect_protection(self):
        # Untrusted external redirect URL must be blocked
        malicious_url = 'https://malicious-phishing-site.com/steal-creds'
        response = self.client.post(f"{reverse('login')}?next={malicious_url}", {
            'username': 'johndoe',
            'password': 'Password123!'
        })
        self.assertRedirects(response, reverse('todo:task_list'))

    def test_remember_me_session_setting(self):
        # Login without remember_me
        self.client.post(reverse('login'), {
            'username': 'johndoe',
            'password': 'Password123!'
        })
        self.assertEqual(self.client.session.get_expire_at_browser_close(), True)

        # Login with remember_me
        self.client.post(reverse('login'), {
            'username': 'johndoe',
            'password': 'Password123!',
            'remember_me': 'on'
        })
        self.assertEqual(self.client.session.get_expire_at_browser_close(), False)

    def test_password_reset_workflow(self):
        # Request password reset email
        response = self.client.post(reverse('password_reset'), {'email': 'john@example.com'})
        self.assertRedirects(response, reverse('password_reset_done'))

    def test_token_authentication_endpoint(self):
        # Obtain auth token
        token_res = self.client.post(
            reverse('api_token_auth'),
            {'username': 'johndoe', 'password': 'Password123!'},
            content_type='application/json'
        )
        self.assertEqual(token_res.status_code, 200)
        token_key = token_res.data['token']
        self.assertTrue(bool(token_key))

        # Use token to call protected API
        auth_client = Client()
        api_res = auth_client.get(
            '/api/auth/user/',
            HTTP_AUTHORIZATION=f'Token {token_key}'
        )
        self.assertEqual(api_res.status_code, 200)
        self.assertEqual(api_res.data['username'], 'johndoe')

