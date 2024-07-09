from rest_framework.reverse import reverse
from rest_framework import status
from forum.tests_setup import UserSetupMixin

from projects.models import Industry


class IndustryModelTestCase(UserSetupMixin):
    CREATE_INDUSTRY_COUNT: int = 3

    def setUp(self) -> None:
        self.setup_test_user()

        # create industries
        for i in range(self.CREATE_INDUSTRY_COUNT):
            tmp_industry = Industry.objects.create(
                name=f"industry {i}",
                description=f"test description {i}"
            )
            Industry.objects.get(industry_id=tmp_industry.industry_id)

    def test_projects_industries(self):
        response = self.client.get(reverse('industries-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), self.CREATE_INDUSTRY_COUNT)
