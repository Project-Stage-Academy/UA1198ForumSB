from unittest.mock import patch

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.reverse import reverse
from rest_framework import status

from forum.tests_setup import UserSetupMixin


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
