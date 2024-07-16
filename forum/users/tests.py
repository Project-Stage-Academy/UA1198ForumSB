from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.http.cookie import SimpleCookie
from .models import CustomUser
from investors.models import Investor
from startups.models import Startup
from rest_framework_simplejwt.tokens import AccessToken


class SelectNameSpaceTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('users:namespace_selection')
        password = 'Test1234'
        self.user = CustomUser.objects.create_user(
            user_id=1,
            first_name='test',
            last_name='test',
            email='test@gmail.com',
            password=''
        )
        self.user.password = password
        self.user.save()
        user_credentials = {
            "email": self.user.email,
            "password": password
        }
        response = self.client.post(reverse('users:token_obtain_pair'), data=user_credentials)
        refresh_token = response.data.get("refresh")
        access_token = response.data.get("access")
        self.client.cookies = SimpleCookie({
            'refresh': refresh_token,
            'access': access_token
        })
        self.post_headers = {
            "Authorization": f"Bearer {access_token}"
        }
        self.investor = Investor.objects.create(
            investor_id=1,
            user=self.user
        )
        self.investor.save()
        self.startup = Startup.objects.create(
            startup_id=1,
            user=self.user,
            name="test-startup"
        )
        self.startup.save()

    def test_select_existed_investor_namespase(self):
        post_body = {
            'name_space_id': self.investor.investor_id,
            'name_space_name': 'investor'
        }
        response = self.client.post(self.url, data=post_body, headers=self.post_headers)
        access_token = response.cookies.get('access').value
        access_token_obj = AccessToken(access_token)

        user_id = access_token_obj.payload.get("user_id")
        name_space_id = access_token_obj.payload.get("name_space_id")
        name_space_name = access_token_obj.payload.get("name_space_name")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user_id, self.user.user_id)
        self.assertEqual(name_space_id, self.investor.investor_id)
        self.assertEqual(name_space_name, 'investor')
    
    def test_select_inexisted_investor_namespase(self):
        post_body = {
            'name_space_id': 3,
            'name_space_name': 'investor'
        }
        response = self.client.post(self.url, data=post_body, headers=self.post_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_select_existed_startup_namespase(self):
        post_body = {
            'name_space_id': self.startup.startup_id,
            'name_space_name': 'startup'
        }
        response = self.client.post(self.url, data=post_body, headers=self.post_headers)
        access_token = response.cookies.get('access').value
        access_token_obj = AccessToken(access_token)

        user_id = access_token_obj.payload.get("user_id")
        name_space_id = access_token_obj.payload.get("name_space_id")
        name_space_name = access_token_obj.payload.get("name_space_name")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user_id, self.user.user_id)
        self.assertEqual(name_space_id, self.startup.startup_id)
        self.assertEqual(name_space_name, 'startup')
    
    def test_select_inexisted_startup_namespase(self):
        post_body = {
            'name_space_id': 56,
            'name_space_name': 'startup'
        }
        response = self.client.post(self.url, data=post_body, headers=self.post_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_select_invalid_namespase(self):
        post_body = {
            'name_space_id': self.startup.startup_id,
            'name_space_name': 'python'
        }
        response = self.client.post(self.url, data=post_body, headers=self.post_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_select_namespase_invalid_post_data(self):
        post_body = {
            'name_space_name': 'startup'
        }
        response = self.client.post(self.url, data=post_body, headers=self.post_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_select_namespase_without_post_data(self):
        response = self.client.post(self.url, headers=self.post_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
