from unittest import TestCase
from unittest.mock import patch
from django.core.exceptions import ValidationError

from projects.utils import get_changed_fields
from projects.notifications import send_notification
from projects.models import Project, ProjectStatus
from .tests_project_setup import ProjectSetupMixin

from forum.tests_setup import UserSetupMixin
from forum.settings import EMAIL_HOST
from startups.models import Startup
from users.models import CustomUser



class NotificationTests(UserSetupMixin):

    def setUp(self):
        super().setUp()
  
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

    @patch('projects.notifications.send_email_task')
    @patch('projects.notifications.build_email_message')
    def test_send_notification_create(self, mock_build_email_message, mock_send_email_task):
        mock_build_email_message.return_value = "Email body content"
        send_notification(self.project, 'create')

        mock_build_email_message.assert_called_once_with(
            "email/project_notifications_for_startup.txt",
            {
                "project_name": self.project.title,
                "action": 'create',
                "startup_name": self.startup.name
            }
        )

        mock_send_email_task.delay.assert_called_once_with(
            subject="Project Create",
            body="Email body content",
            sender=EMAIL_HOST,
            receivers=[self.startup.user.email],
        )

class UtilsTests(TestCase):

    def setUp(self):
        self.test_user = CustomUser(
            first_name="test_first",
            last_name="test_last",
            email="test@gmail.com",
            password="test_password"
        )
        self.startup = Startup(
            user=self.test_user,
            name="Test Startup",
            location="Test Location",
            contacts={"contacts": "Test Contacts"}
        )

        self.project_status = ProjectStatus(
            title="in progress",
            description='in progress'
        )

    def test_get_changed_fields_with_correct_data(self):

        old_instance = Project(
            startup=self.startup,
            status=self.project_status,
            title="Project Title",
            description="description"
        )
        new_instance = Project(
            startup=self.startup,
            status=self.project_status,
            title="Updated Project Title",
            description="Updated description"
        )

        result = get_changed_fields(old_instance=old_instance, new_instance=new_instance)
        validated_data ={ 
            "title": {
                'old': "Project Title",
                'new': "Updated Project Title"
            },
            "description": {
                'old': "description",
                'new': "Updated description"
            }
        }
        self.assertEqual(result, validated_data)
    
    def test_get_changed_fields_with_not_correct_data(self):
        old_instance = Project(
            startup=self.startup,
            status=self.project_status,
            title="Project Title",
            description="description"
        )
        new_instance = Project(
            startup=self.startup,
            status=self.project_status,
            title="Updated Project Title",
            description="Not updated description"
        )

        result = get_changed_fields(old_instance=old_instance, new_instance=new_instance)
        validated_data ={ 
            "title": {
                'old': "Project Title",
                'new': "Updated Project Title"
            },
            "description": {
                'old': "description",
                'new': "Updated description"
            }
        }
        self.assertNotEqual(result, validated_data)

    def test_get_changed_fields_with_not_correct_instance(self):
        old_instance = Startup(
            user=self.test_user,
            name="Test Startup",
            location="Test Location",
            contacts={"contacts": "Test Contacts"}
        )
        new_instance = Project(
            startup=self.startup,
            status=self.project_status,
            title="Updated Project Title",
            description="Not updated description"
        )

        with self.assertRaises(ValidationError):
            get_changed_fields(old_instance=old_instance, new_instance=new_instance)