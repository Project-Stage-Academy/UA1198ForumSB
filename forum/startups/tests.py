from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status

from forum.tests_setup import TestUserSetupMixin
from startups.models import StartupSize


class StartupsTestCase(TestUserSetupMixin):
    CREATE_OBJ_COUNT: int = 5

    def setUp(self) -> None:
        self.setup_test_user()

        for i in range(self.CREATE_OBJ_COUNT):
            tmp_size_obj = StartupSize.objects.create(
                name="test size",
                people_count_min=20,
                people_count_max=30
            )
            StartupSize.objects.get(size_id=tmp_size_obj.size_id)

    def test_industries_list(self):
        response = self.client.get(reverse('startup_sizes-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), self.CREATE_OBJ_COUNT)
