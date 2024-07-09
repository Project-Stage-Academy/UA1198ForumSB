from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from users.models import CustomUser


class UserSetupMixin(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.setup_test_user()

    def setup_test_user(self) -> None:
        self.test_user: CustomUser = CustomUser.objects.create_user(
            first_name="test_first",
            last_name="test_last",
            email="test@gmail.com",
            password="test_password"
        )

        token = AccessToken.for_user(self.test_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def tearDown(self) -> None:
        self.client.logout()
