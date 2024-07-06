from rest_framework import status
from rest_framework.test import APITestCase


class StartupsTestCase(APITestCase):
    def test_industries_list(self):
        response = self.client.get("/startups/startup_sizes/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
