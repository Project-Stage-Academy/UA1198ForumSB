import json

from rest_framework.reverse import reverse
from rest_framework import status
from unittest.mock import patch

from forum.tests_setup import UserSetupMixin
from projects.models import Project, ProjectStatus
from startups.models import Startup, StartupSize
from projects.serializers import ProjectSerializer
from users.models import CustomUser


class UserStartupProjectViewTests(UserSetupMixin):

    def setUp(self):
        super().setUp()

        startup_size = StartupSize.objects.create(
            name='small',
            people_count_min = 1,
            people_count_max = 5
        )
        self.project_status = ProjectStatus.objects.create(
            title="in progress",
            description='in progress'
        )
        self.startup = Startup.objects.create(
            user=self.test_user,
            name="Test Startup",
            location="Test Location",
            contacts={"contacts": "Test Contacts"}
        )
        self.startup2 = Startup.objects.create(
            user=self.test_user,
            name="Test Startup 2",
            location="Test Location 2",
            contacts={"contacts": "Test Contacts"}
        )
        self.project = Project.objects.create(
            startup=self.startup,
            status=self.project_status,
            title="Project Title",
            description="description"
        )
        
        self.url = reverse('users:user_startup_project', args=[self.test_user.user_id, self.startup.startup_id])
        self.patch_url = reverse('users:user_startup_project', args=[self.test_user.user_id, self.startup2.startup_id])
        self.valid_payload = {
            'startup': self.startup2.startup_id,
            'status': self.project_status.status_id,
            'user': self.test_user.user_id,
            'title': 'New Project Title',
            'description': 'New Description',
        }
        self.valid_update_payload = {
            'title': 'New Project Title',
            'description': 'New Description'
        }
   
    @patch('users.permissions.get_token_payload_from_cookies')
    def test_get_project(self, mock_get_token_payload):
        mock_get_token_payload.return_value = {
            'user_id': self.test_user.user_id,
            'name_space_id': self.startup.startup_id,
            'name_space_name': 'startup'
        }

        response = self.client.get(self.url)
        project = Project.objects.get(pk=self.project.pk)
        serializer = ProjectSerializer(project)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    @patch('projects.views.send_notification')
    @patch('users.permissions.get_token_payload_from_cookies')
    def test_create_project(self, mock_get_token_payload, mock_send_notification):
        mock_get_token_payload.return_value = {
            'user_id': self.test_user.user_id,
            'name_space_id': self.startup.startup_id,
            'name_space_name': 'startup'
        }

        response = self.client.post(self.patch_url, data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_send_notification.assert_called_once()
        
    @patch('projects.views.send_notification')
    @patch('projects.views.notify_investors_via_email')
    @patch('users.permissions.get_token_payload_from_cookies')
    def test_update_project(self, mock_get_token_payload, mock_send_notification, mock_notify_investors_via_email):
        mock_get_token_payload.return_value = {
            'user_id': self.test_user.user_id,
            'name_space_id': self.startup.startup_id,
            'name_space_name': 'startup'
        }

        response = self.client.patch(self.url, data=json.dumps(self.valid_update_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.objects.get(pk=self.project.pk)
        self.assertEqual(project.title, self.valid_update_payload['title'])
        self.assertEqual(project.description, self.valid_update_payload['description'])
        mock_send_notification.assert_called_once()
        mock_notify_investors_via_email.assert_called_once()
    
    @patch('projects.views.send_notification')
    @patch('users.permissions.get_token_payload_from_cookies')
    def test_delete_project(self, mock_get_token_payload, mock_send_notification):
        mock_get_token_payload.return_value = {
            'user_id': self.test_user.user_id,
            'name_space_id': self.startup.startup_id,
            'name_space_name': 'startup'
        }

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_send_notification.assert_called_once()
        # project = Project.objects.get(pk=self.project.pk)
        # self.assertTrue(project.is_deleted)

    @patch('users.permissions.get_token_payload_from_cookies')
    def test_create_project_with_invalid_payload(self, mock_get_token_payload):
        mock_get_token_payload.return_value = {
            'user_id': self.test_user.user_id,
            'name_space_id': self.startup.startup_id,
            'name_space_name': 'startup'
        }

        invalid_payload = {
            "title": "",  
            "description": "New project description",
            "budget": "not_a_number"  
        }
        response = self.client.post(self.url, data=invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('users.permissions.get_token_payload_from_cookies')
    def test_unauthorized_access(self, mock_get_token_payload):
        
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('users.permissions.get_token_payload_from_cookies')
    def test_access_non_existent_project(self, mock_get_token_payload):
        mock_get_token_payload.return_value = {
            'user_id': self.test_user.user_id,
            'name_space_id': self.startup.startup_id,
            'name_space_name': 'startup'
        }

        non_existent_url = reverse('users:user_startup_project', args=[self.test_user.user_id, 999])
        response = self.client.get(non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('users.permissions.get_token_payload_from_cookies')
    def test_delete_non_existent_project(self, mock_get_token_payload):
        mock_get_token_payload.return_value = {
            'user_id': self.test_user.user_id,
            'name_space_id': self.startup.startup_id,
            'name_space_name': 'startup'
        }

        non_existent_url = reverse('users:user_startup_project', args=[self.test_user.user_id, 999])
        response = self.client.delete(non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('users.permissions.get_token_payload_from_cookies')
    def test_update_project_with_invalid_data(self, mock_get_token_payload):
        mock_get_token_payload.return_value = {
            'user_id': self.test_user.user_id,
            'name_space_id': self.startup.startup_id,
            'name_space_name': 'startup'
        }

        invalid_update_payload = {
            "title": "",  
            "description": "Updated description",
            "budget": "not_a_number"  
        }
        response = self.client.patch(self.url, data=invalid_update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    