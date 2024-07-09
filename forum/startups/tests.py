from rest_framework.reverse import reverse
from rest_framework import status

from forum.tests_setup import UserSetupMixin
from startups.models import StartupSize


class StartupsTestCase(UserSetupMixin):
    CREATE_OBJ_COUNT: int = 5

    def setUp(self) -> None:
        super().setUp()

        for i in range(self.CREATE_OBJ_COUNT):
            StartupSize.objects.create(
                name="test size",
                people_count_min=20,
                people_count_max=30
            )

    def test_industries_list(self):
        response = self.client.get(reverse('startup_sizes-list'))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Status code is different from 200"
        )
        self.assertEqual(
            len(response.json()),
            self.CREATE_OBJ_COUNT,
            "The number of objects received is not equal to the number created"
        )
