import json
from abc import ABC
from unittest import TestCase

from investors.models import Investor
from projects.models import Project, ProjectStatus, ProjectSubscription
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from startups.models import Startup
from users.models import CustomUser

from communications.utils import StartupNotificationManager
from forum.tests_setup import UserSetupMixin


class NotificationListMixin(ABC):
    def get_notifications(self) -> list:
        response = self.client.get(reverse("notification_list"))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Status code is different from 200"
        )

        json_data = response.json()
        self.assertIsNot(
            len(json_data),
            0,
            "There is no notification exist"
        )

        for notification in json_data:
            response = self.client.put(
                reverse(
                    "notification_detail",
                    kwargs={
                        "notification_id": notification["notification_id"]
                    }
                ),
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                "Status code is different from 200"
            )


class NotificationTrigger(TestCase, NotificationListMixin):
    def __init__(self) -> None:
        super().__init__()

        self.client = APIClient()

        self.test_user: CustomUser = CustomUser.objects.create_user(
            first_name="test_first",
            last_name="test_last",
            email="test2@gmail.com",
            password="test_password"
        )

        token = AccessToken.for_user(self.test_user)
        self.client.cookies["access_token"] = token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        self.client.cookies["namespace"] = "startup"
        response = self.client.post(
            reverse('users:user_startups', kwargs={'user_id': self.test_user.user_id}),
            {
                'user': self.test_user.user_id,
                'name': 'test name4',
                'location': 'test location',
                'description': 'test description',
                'contacts': json.dumps({'phone': 'test phone'})
            }
        )
        self.startup_id = response.json()["startup_id"]

        self.notification_initiator_namespace = Startup.objects.get(
            startup_id=self.startup_id
        )

        project_status = ProjectStatus.objects.create(title='test status')

        self.project = Project.objects.create(
            startup=self.notification_initiator_namespace,
            status=project_status,
            title='title test'
        )

    def send_notification(self, message: str) -> None:
        snm = StartupNotificationManager(self.notification_initiator_namespace)
        snm.push_notification(message)


class ReceiveNotificationTestCase(UserSetupMixin, NotificationListMixin):
    TEST_NOTIFICATION: str = "Test notification"

    def setUp(self) -> None:
        super().setUp()

        self.notification_trigger = NotificationTrigger()

        self.test_investor = Investor.objects.create(user=self.test_user)

        ProjectSubscription.objects.create(
            project=self.notification_trigger.project,
            investor=self.test_investor,
            part=10
        )

    def test_send_and_read_notification(self):
        self.notification_trigger.send_notification(self.TEST_NOTIFICATION)

        self.get_notifications()

    def test_send_message_and_get_notification(self):
        participants_list = [
            {
                "user_id": self.test_user.user_id,
                "namespace": "investor",
                "namespace_id": self.test_investor.investor_id
            },
            {
                "user_id": self.notification_trigger.test_user.user_id,
                "namespace": "startup",
                "namespace_id": self.notification_trigger.startup_id
            },
        ]
        response = self.client.post(
            reverse("create_conversation"),
            {
                "participants": participants_list
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201,
            "Room is not exists and it's unable to create"
        )

        json_response: dict = response.json()
        self.assertIsNotNone(
            json_response.get("conversation_id"),
            "conversation_id was not provided"
        )

        conversation_id = json_response.get("conversation_id")

        response = self.client.post(
            reverse("send_message"),
            {
                "room": conversation_id,
                "author": participants_list[0],
                "content": "test message"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201,
            "Message was not created"
        )

        self.notification_trigger.get_notifications()
