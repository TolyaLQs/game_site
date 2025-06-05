from django.test import TestCase
from .models import User


# Create your tests here.
class AuthTestCase(TestCase):
    def test_user_registration(self):
        response = self.client.post('/register/', {
            'email': 'test@example.com',
            'username': 'testuser',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_login_with_email(self):
        user = User.objects.create_user(email='test@ex.com', username='test', password='testpass')
        self.client.login(email='test@ex.com', password='testpass')
        response = self.client.get('/profile/')
        self.assertContains(response, user.username)