import json
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.http.cookie import SimpleCookie
from investors.models import Investor
from startups.models import Startup
from rest_framework_simplejwt.tokens import AccessToken

from unittest.mock import patch

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from users.models import CustomUser
from forum.tests_setup import UserSetupMixin


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
            'refresh_token': refresh_token,
            'access_token': access_token
        })
        self.authorization_headers = {
            "Authorization": f"Bearer {access_token}"
        }
        self.investor = Investor.objects.create(
            investor_id=1,
            user=self.user,
            contacts=json.dumps({})
        )
        self.investor.save()
        self.startup = Startup.objects.create(
            startup_id=1,
            user=self.user,
            name="test-startup",
            contacts=json.dumps({})
        )
        self.startup.save()

    def test_select_existed_investor_namespase(self):
        post_body = {
            'name_space_id': self.investor.investor_id,
            'name_space_name': 'investor'
        }
        response = self.client.post(self.url, data=post_body, headers=self.authorization_headers)
        access_token = response.cookies.get('access_token').value
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
        response = self.client.post(self.url, data=post_body, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_select_existed_startup_namespase(self):
        post_body = {
            'name_space_id': self.startup.startup_id,
            'name_space_name': 'startup'
        }
        response = self.client.post(self.url, data=post_body, headers=self.authorization_headers)
        access_token = response.cookies.get('access_token').value
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
        response = self.client.post(self.url, data=post_body, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_select_invalid_namespase(self):
        post_body = {
            'name_space_id': self.startup.startup_id,
            'name_space_name': 'python'
        }
        response = self.client.post(self.url, data=post_body, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_select_namespase_invalid_post_data(self):
        post_body = {
            'name_space_name': 'startup'
        }
        response = self.client.post(self.url, data=post_body, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_select_namespase_without_post_data(self):
        response = self.client.post(self.url, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserStartupListTestCase(APITestCase):
    def setUp(self):
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
        self.url = reverse("users:user_startups", kwargs=dict(user_id=self.user.user_id))
        user_credentials = {
            "email": self.user.email,
            "password": password
        }
        response = self.client.post(reverse('users:token_obtain_pair'), data=user_credentials)
        refresh_token = response.data.get("refresh")
        access_token = response.data.get("access")
        self.client.cookies = SimpleCookie({
            'refresh_token': refresh_token,
            'access_token': access_token
        })
        self.authorization_headers = {
            "Authorization": f"Bearer {access_token}"
        }
        self.investor1 = Investor.objects.create(
            investor_id=10,
            user=self.user
        )
        self.investor2 = Investor.objects.create(
            investor_id=11,
            user=self.user
        )
        self.investor1.save()
        self.investor2.save()

        self.startup1 = Startup.objects.create(
            startup_id=10,
            user=self.user,
            name="test-startup1",
            contacts={}
        )
        self.startup2 = Startup.objects.create(
            startup_id=11,
            user=self.user,
            name="test-startup2",
            contacts={}
        )
        self.startup1.save()
        self.startup2.save()
    
    def test_user_can_get_his_startups_if_namespace_is_not_selected(self):
        response = self.client.get(self.url, headers=self.authorization_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0].get("name"), 'test-startup1')
        self.assertEqual(response.data[1].get("name"), 'test-startup2')
    
    def test_user_can_get_his_startups_if_namespace_is_startup(self):
        select_namespace_data = {
            'name_space_id': self.startup1.startup_id,
            'name_space_name': 'startup'
        }
        self.client.post(
            reverse('users:namespace_selection'),
            data=select_namespace_data,
            headers=self.authorization_headers
        )
        response = self.client.get(self.url, headers=self.authorization_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0].get("name"), 'test-startup1')
        self.assertEqual(response.data[1].get("name"), 'test-startup2')
    
    def test_user_can_get_his_startups_if_namespace_is_investor(self):
        select_namespace_data = {
            'name_space_id': self.investor1.investor_id,
            'name_space_name': 'investor'
        }
        self.client.post(
            reverse('users:namespace_selection'),
            data=select_namespace_data,
            headers=self.authorization_headers
        )
        response = self.client.get(self.url, headers=self.authorization_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0].get("name"), 'test-startup1')
        self.assertEqual(response.data[1].get("name"), 'test-startup2')

    def test_user_can_create_startup_if_namespace_is_not_selected(self):
        post_data = dict(
            user=self.user.user_id,
            name="test-startup3",
            location="UA",
            description="desc",
            contacts=json.dumps({})
        )
        response = self.client.post(self.url, data=post_data, headers=self.authorization_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_user_can_create_startup_if_namespace_is_startup(self):
        select_namespace_data = {
            'name_space_id': self.startup1.startup_id,
            'name_space_name': 'startup'
        }
        self.client.post(
            reverse('users:namespace_selection'),
            data=select_namespace_data,
            headers=self.authorization_headers
        )
        post_data = dict(
            user=self.user.user_id,
            name="test-startup3",
            location="UA",
            description="desc",
            contacts=json.dumps({})
        )
        response = self.client.post(self.url, data=post_data, headers=self.authorization_headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response = self.client.get(self.url, headers=self.authorization_headers)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[2].get("name"), 'test-startup3')
    
    def test_user_can_create_startup_if_namespace_is_investor(self):
        select_namespace_data = {
            'name_space_id': self.investor1.investor_id,
            'name_space_name': 'investor'
        }
        self.client.post(
            reverse('users:namespace_selection'),
            data=select_namespace_data,
            headers=self.authorization_headers
        )
        post_data = dict(
            user=self.user.user_id,
            name="test-startup3",
            location="UA",
            description="desc",
            contacts=json.dumps({})
        )
        response = self.client.post(self.url, data=post_data, headers=self.authorization_headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response = self.client.get(self.url, headers=self.authorization_headers)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[2].get("name"), 'test-startup3')
    
    def test_user_can_not_view_startups_of_an_other_user(self):
        url = reverse("users:user_startups", kwargs=dict(user_id=100))
        response = self.client.get(url, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_can_not_create_startup_for_an_other_user(self):
        select_namespace_data = {
            'name_space_id': self.startup1.startup_id,
            'name_space_name': 'startup'
        }
        self.client.post(
            reverse('users:namespace_selection'),
            data=select_namespace_data,
            headers=self.authorization_headers
        )
        other_user = CustomUser.objects.create_user(
            user_id=101,
            first_name='test',
            last_name='test',
            email='other@gmail.com',
            password='test'
        )
        other_user.save()
        post_data = dict(
            user=other_user.user_id,
            name="test-startup",
            location="UA",
            description="desc",
            contacts=json.dumps({})
        )
        response = self.client.post(self.url, data=post_data, headers=self.authorization_headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = other_url = f"/users/{other_user.user_id}/startups/"
        response = self.client.post(other_url, data=post_data, headers=self.authorization_headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserStartupDetailTestCase(APITestCase):
    def setUp(self):
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
            'refresh_token': refresh_token,
            'access_token': access_token
        })
        self.authorization_headers = {
            "Authorization": f"Bearer {access_token}"
        }
        self.investor1 = Investor.objects.create(
            investor_id=10,
            user=self.user
        )
        self.investor2 = Investor.objects.create(
            investor_id=11,
            user=self.user
        )
        self.investor1.save()
        self.investor2.save()

        self.startup1 = Startup.objects.create(
            startup_id=10,
            user=self.user,
            name="test-startup1",
            contacts={}
        )
        self.startup2 = Startup.objects.create(
            startup_id=11,
            user=self.user,
            name="test-startup2",
            contacts={}
        )
        self.startup1.save()
        self.startup2.save()
        self.url = reverse("users:user_startup", kwargs=dict(
            user_id=self.user.user_id,
            startup_id=self.startup1.startup_id
        ))
    
    def test_user_can_view_update_or_delete_his_startup(self):
        select_namespace_data = {
            'name_space_id': self.startup1.startup_id,
            'name_space_name': 'startup'
        }
        self.client.post(
            reverse('users:namespace_selection'),
            data=select_namespace_data,
            headers=self.authorization_headers
        )
        response = self.client.get(self.url, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("name"), 'test-startup1')

        patch_data = {"name":"new-name-1", "location": "new-loc"}
        response = self.client.patch(self.url, data=patch_data, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.url, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("name"), 'new-name-1')
        self.assertEqual(response.data.get("location"), 'new-loc')

        response = self.client.delete(self.url, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_user_can_view_startup_if_namespace_is_investor(self):
        select_namespace_data = {
            'name_space_id': self.investor1.investor_id,
            'name_space_name': 'investor'
        }
        self.client.post(
            reverse('users:namespace_selection'),
            data=select_namespace_data,
            headers=self.authorization_headers
        )
        response = self.client.get(self.url, headers=self.authorization_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("name"), 'test-startup1')

    def test_user_can_not_update_or_delete_startup_if_namespace_is_investor(self):
        select_namespace_data = {
            'name_space_id': self.investor1.investor_id,
            'name_space_name': 'investor'
        }
        self.client.post(
            reverse('users:namespace_selection'),
            data=select_namespace_data,
            headers=self.authorization_headers
        )
        patch_data = {"name": "updated-name1"}
        response = self.client.patch(self.url, data=patch_data, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(self.url, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_can_view_startup_if_namespace_is_not_selected(self):
        response = self.client.get(self.url, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("name"), 'test-startup1')

    def test_user_can_not_update_or_delete_startup_if_namespace_is_not_selected(self):
        patch_data = {"name": "updated-name1"}
        response = self.client.patch(self.url, data=patch_data, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(self.url, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_can_not_update_stratup_if_an_other_is_selected(self):
        select_namespace_data = {
            'name_space_id': self.startup2.startup_id,
            'name_space_name': 'startup'
        }
        self.client.post(
            reverse('users:namespace_selection'),
            data=select_namespace_data,
            headers=self.authorization_headers
        )
        patch_data = {"name": "updated-name1"}
        response = self.client.patch(self.url, data=patch_data, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_view_or_delete_stratup_if_an_other_is_selected(self):
        select_namespace_data = {
            'name_space_id': self.startup2.startup_id,
            'name_space_name': 'startup'
        }
        self.client.post(
            reverse('users:namespace_selection'),
            data=select_namespace_data,
            headers=self.authorization_headers
        )
        response = self.client.get(self.url, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.url, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_can_not_view_update_or_delete_startup_of_an_other_user(self):
        select_namespace_data = {
            'name_space_id': self.startup1.startup_id,
            'name_space_name': 'startup'
        }
        self.client.post(
            reverse('users:namespace_selection'),
            data=select_namespace_data,
            headers=self.authorization_headers
        )
        password = 'Test1234'
        other_user = CustomUser.objects.create_user(
            user_id=2,
            first_name='test',
            last_name='test',
            email='test2@gmail.com',
            password=''
        )
        other_user.password = password
        other_user.save()
        other_startup = Startup.objects.create(
            startup_id=300,
            user=other_user,
            name="test-other-startup",
            contacts={}
        )
        other_startup.save()
        url = f"/users/{other_user.user_id}/startups/{other_startup.startup_id}/"

        response = self.client.get(url, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        patch_data = {"name": "new-name"}
        response = self.client.patch(url, data=patch_data, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(url, headers=self.authorization_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserInvestorListTestCase(APITestCase):
    def setUp(self):
        password = "Test_12345"
        self.user = CustomUser.objects.create_user(            
            first_name="test",
            last_name="test",
            email="test@gmail.com",
            password=password
        )
        self.user2 = CustomUser.objects.create_user(            
            first_name="test2",
            last_name="test2",
            email="test2@gmail.com",
            password=password
        )
        self.investor1 = Investor.objects.create(
            user=self.user,
            contacts={"contact": "+380950000000"} 
        )
        self.investor2 = Investor.objects.create(
            user=self.user,
            contacts={"contact": "+380990000000"} 
        )
        self.namespace_selection_url = reverse('users:namespace_selection')
        self.user_investors_url = reverse('users:user_investors', args=[self.user.user_id])
        self.other_user_investors_url = reverse('users:user_investors', args=[self.user2.user_id])
        
        user_credentials = {
            "email": self.user.email,
            "password": password
        }
        response = self.client.post(reverse('users:token_obtain_pair'), data=user_credentials)
        refresh_token = response.data.get("refresh")
        access_token = response.data.get("access")
        self.client.cookies = SimpleCookie({'access_token': str(access_token), 'refresh_token': str(refresh_token)})
        self.client_credentials_headers = {"Authorization": f"Bearer {access_token}"}

    def tearDown(self):
        CustomUser.objects.all().delete()
        Investor.objects.all().delete()

    def test_user_can_get_investors_if_namespace_is_selected(self):
        self.client.post(self.namespace_selection_url, {
            'name_space_name': 'investor',
            'name_space_id': self.investor1.investor_id
        }, headers=self.client_credentials_headers)

        response = self.client.get(self.user_investors_url, 
                                   headers=self.client_credentials_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['contacts']['contact'], '+380950000000')
        self.assertEqual(response.data[1]['contacts']['contact'], '+380990000000')

    def test_user_can_get_investors_if_namespace_is_not_selected(self):
        response = self.client.get(self.user_investors_url, 
                                   headers=self.client_credentials_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_user_can_not_get_investors_if_not_authenticated(self):
        response = self.client.get(self.user_investors_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_user_can_not_view_investors_of_an_other_user(self):
        response = self.client.get(self.other_user_investors_url, 
                                   headers=self.client_credentials_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_create_investor_if_namespace_is_selected(self):
        self.client.post(self.namespace_selection_url, {
            'name_space_name': 'investor',
            'name_space_id': self.investor1.investor_id
        }, headers=self.client_credentials_headers)

        response = self.client.post(self.user_investors_url, {
            'user': self.user.user_id,
            'contacts': {'contact': '+380960000000'}
        }, headers=self.client_credentials_headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['contacts']['contact'], '+380960000000')

    def test_user_can_create_investor_if_namespace_is_not_selected(self):
        response = self.client.post(self.user_investors_url, {
            'user': self.user.user_id,
            'contacts': {'contact': '+380960000000'}
        }, headers=self.client_credentials_headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['contacts']['contact'], '+380960000000')
        
    def test_user_can_not_create_investor_if_not_authenticated(self):
        response = self.client.post(self.user_investors_url, {
            'user': self.user.user_id,
            'contacts': {'contact': '+380960000000'}
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  
        
    def test_user_can_not_create_investor_for_an_other_user(self):
        self.client.post(self.namespace_selection_url, {
            'name_space_name': 'investor',
            'name_space_id': self.investor1.investor_id
        }, headers=self.client_credentials_headers)
        
        post_data = dict(
            user=self.user2.user_id,
            contacts={'contact': '+380960000000'}
        )

        response = self.client.post(self.other_user_investors_url, data=post_data, 
                                    headers=self.client_credentials_headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        response = self.client.post(self.user_investors_url, data=post_data, 
                                    headers=self.client_credentials_headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserInvestorDetailTestCase(APITestCase):
    def setUp(self):
        password = "Test_12345"
        self.user = CustomUser.objects.create_user(            
            first_name="test",
            last_name="test",
            email="test@gmail.com",
            password=password
        )
        self.user2 = CustomUser.objects.create_user(            
            first_name="test2",
            last_name="test2",
            email="test2@gmail.com",
            password=password
        )
        self.investor1 = Investor.objects.create(
            user=self.user,
            contacts={"contact": "+380950000000"} 
        )
        self.investor2 = Investor.objects.create(
            user=self.user,
            contacts={"contact": "+380990000000"} 
        )
        self.namespace_selection_url = reverse('users:namespace_selection')
        self.user_investor_url = reverse('users:user_investor', 
                                         args=[self.user.user_id, self.investor1.investor_id])
        
        user_credentials = {
            "email": self.user.email,
            "password": password
        }
        response = self.client.post(reverse('users:token_obtain_pair'), data=user_credentials)
        refresh_token = response.data.get("refresh")
        access_token = response.data.get("access")
        self.client.cookies = SimpleCookie({'access_token': str(access_token), 'refresh_token': str(refresh_token)})
        self.client_credentials_headers = {"Authorization": f"Bearer {access_token}"}

    def tearDown(self):
        CustomUser.objects.all().delete()
        Investor.objects.all().delete()

    def test_user_can_view_update_or_delete_his_investor(self):
        self.client.post(self.namespace_selection_url, {
            'name_space_name': 'investor',
            'name_space_id': self.investor1.investor_id
        }, headers=self.client_credentials_headers)
        
        response = self.client.get(self.user_investor_url, 
                                   headers=self.client_credentials_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['contacts']['contact'], '+380950000000')
        
        response = self.client.patch(self.user_investor_url, {
            'contacts': {'contact': '+380960000000'}
        }, headers=self.client_credentials_headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['contacts']['contact'], '+380960000000')
        
        response = self.client.delete(self.user_investor_url, 
                                      headers=self.client_credentials_headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_can_view_investor_if_namespace_is_startup(self):
        self.client.post(self.namespace_selection_url, {
            'name_space_name': 'startup',
            'name_space_id': self.investor1.investor_id
        }, headers=self.client_credentials_headers)
        
        response = self.client.get(self.user_investor_url, 
                                   headers=self.client_credentials_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_view_investor_if_namespace_is_not_selected(self):
        response = self.client.get(self.user_investor_url, 
                                   headers=self.client_credentials_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_not_update_or_delete_investor_if_namespace_is_startup(self):
        self.client.post(self.namespace_selection_url, {
            'name_space_name': 'startup',
            'name_space_id': self.investor1.investor_id
        }, headers=self.client_credentials_headers)
        
        response = self.client.patch(self.user_investor_url, {
            'contacts': {'contact': '+380960000000'}
        }, headers=self.client_credentials_headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        response = self.client.delete(self.user_investor_url, 
                                      headers=self.client_credentials_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_not_update_or_delete_investor_if_namespace_is_not_selected(self):
        response = self.client.patch(self.user_investor_url, {
            'contacts': {'contact': '+380960000000'}
        }, headers=self.client_credentials_headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        response = self.client.delete(self.user_investor_url, 
                                      headers=self.client_credentials_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_not_update_investor_if_an_other_is_selected(self):
        self.client.post(self.namespace_selection_url, {
            'name_space_name': 'investor',
            'name_space_id': self.investor2.investor_id
        }, headers=self.client_credentials_headers)
        
        response = self.client.patch(self.user_investor_url, {
            'contacts': {'contact': '+380960000000'}
        }, headers=self.client_credentials_headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_view_or_delete_investor_if_an_other_is_selected(self):
        self.client.post(self.namespace_selection_url, {
            'name_space_name': 'investor',
            'name_space_id': self.investor2.investor_id
        }, headers=self.client_credentials_headers)
        
        response = self.client.get(self.user_investor_url, 
                                   headers=self.client_credentials_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.delete(self.user_investor_url, 
                                      headers=self.client_credentials_headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_can_not_view_update_or_delete_investor_of_an_other_user(self):
        self.client.post(self.namespace_selection_url, {
            'name_space_name': 'investor',
            'name_space_id': self.investor1.investor_id
        }, headers=self.client_credentials_headers)
        
        investor = Investor.objects.create(
            user=self.user2,
            contacts={"contact": "+380990000000"} 
        )
        other_user_investor_url = reverse('users:user_investor', 
                                        args=[self.user2.user_id, investor.investor_id])
        
        response = self.client.get(other_user_investor_url, 
                                   headers=self.client_credentials_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        response = self.client.patch(other_user_investor_url, {
            'contacts': {'contact': '+380960000000'}
        }, headers=self.client_credentials_headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        response = self.client.delete(other_user_investor_url, 
                                      headers=self.client_credentials_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


FAKE_RESET_TOKEN = "fake_reset_token"


class PasswordReveryTestCase(UserSetupMixin):
    NEW_PASSWORD = "new_fake_password"

    def setUp(self) -> None:
        super().setUp()

    @patch.object(
        PasswordResetTokenGenerator,
        'make_token',
        lambda *args: FAKE_RESET_TOKEN
    )
    def test_password_recovery(self):
        # make request for password recovery
        response = self.client.post(
            reverse("users:password_reset"),
            data={
                "email": self.test_user.email
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Status code is different from 200"
        )

        # confirm password recovery, set new password
        response = self.client.post(
            reverse("users:password_reset_confirm"),
            data={
                "reset_token": FAKE_RESET_TOKEN,
                "password": self.NEW_PASSWORD,
                "password_confirm": self.NEW_PASSWORD
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Status code is different from 200"
        )

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
        self.client.cookies['refresh_token'] = self.refresh_token
        self.client.cookies['access_token'] = self.access_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_logout_with_valid_token(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        response = self.client.post(reverse('users:token_refresh'), {'refresh': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_with_invalid_token(self):
        self.client.cookies['refresh_token'] = 'invalidtoken'
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Token is invalid or expired.')

    def tearDown(self):
        """ Clean up any created data. """
        self.user.delete()        
