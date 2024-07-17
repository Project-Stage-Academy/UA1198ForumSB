from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from users.models import CustomUser

class LogoutAPITestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='testuser@example.com',
            password='testpassword'
        )
        self.url = reverse('users:token_blacklist')

        response = self.client.post(reverse('users:token_obtain_pair'), {
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }, format='json')
        self.access_token = response.data['access']
        self.refresh_token = response.data['refresh']
        self.client.cookies['refresh'] = self.refresh_token
        self.client.cookies['access'] = self.access_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_logout_with_valid_token(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        response = self.client.post(reverse('users:token_refresh'), {'refresh': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_with_invalid_token(self):
        self.client.cookies['refresh'] = 'invalidtoken'
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Token is invalid or expired.')

    def tearDown(self):
        """ Clean up any created data. """
        self.user.delete()
