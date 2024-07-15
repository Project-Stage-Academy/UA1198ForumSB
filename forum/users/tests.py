from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser


class LogoutAPITestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='testuser@example.com',
            password='testpassword'
        )
        self.url = reverse('users:token_blacklist')

        # Obtain tokens for the user
        response = self.client.post(reverse('users:token_obtain_pair'), {
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }, format='json')
        self.access_token = response.data['access']
        self.refresh_token = response.data['refresh']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_logout_with_valid_token(self):
        response = self.client.post(self.url, {'refresh': self.refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_with_invalid_token(self):
        invalid_refresh_token = 'invalidtoken'
        response = self.client.post(self.url, {'refresh': invalid_refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

