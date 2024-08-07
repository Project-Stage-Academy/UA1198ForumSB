import json

from rest_framework.reverse import reverse
from rest_framework import status
from unittest.mock import patch

from forum.tests_setup import UserSetupMixin
from projects.models import Project, ProjectStatus
from startups.models import Startup, StartupSize
from ..serializers import ProjectSerializer


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
        self.url2 = reverse('users:user_startup_project', args=[self.test_user.user_id, self.startup2.startup_id])
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

    @patch('users.permissions.get_token_payload_from_cookies')
    def test_create_project(self, mock_get_token_payload, mock_send_notification):
        mock_get_token_payload.return_value = {
            'user_id': self.test_user.user_id,
            'name_space_id': self.startup.startup_id,
            'name_space_name': 'startup'
        }

        response = self.client.post(self.url2, data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    @patch('users.permissions.get_token_payload_from_cookies')
    def test_update_project(self, mock_get_token_payload):
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
    
    @patch('users.permissions.get_token_payload_from_cookies')
    def test_delete_project(self, mock_get_token_payload):
        mock_get_token_payload.return_value = {
            'user_id': self.test_user.user_id,
            'name_space_id': self.startup.startup_id,
            'name_space_name': 'startup'
        }

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # project = Project.objects.get(pk=self.project.pk)
        # self.assertTrue(project.is_deleted)
    