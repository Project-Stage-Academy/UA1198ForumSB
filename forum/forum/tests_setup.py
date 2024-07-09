from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from users.models import CustomUser


class TestUserSetupMixin(APITestCase):
    def setup_test_user(self) -> None:
        new_user = CustomUser.objects.create(
            first_name="test_first",
            last_name="test_last",
            email="test@gmail.com"
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {AccessToken.for_user(new_user)}'
        )

    def tearDown(self) -> None:
        self.client.logout()
