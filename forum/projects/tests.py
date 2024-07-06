from rest_framework.test import APITestCase
from rest_framework import status


class ProjectTestCase(APITestCase):
    def test_projects_industries(self):
        response = self.client.get("/startups/projects/industries/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
