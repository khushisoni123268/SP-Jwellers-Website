from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AuthPagesTests(TestCase):
    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')

    def test_user_can_register_and_redirect_to_dashboard(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'Khushi',
            'last_name': 'Sharma',
            'username': 'khushi123',
            'email': 'khushi@example.com',
            'password1': 'StrongPass@123',
            'password2': 'StrongPass@123',
        })

        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(username='khushi123').exists())

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
