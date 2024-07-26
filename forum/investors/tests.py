import json

from rest_framework.reverse import reverse
from rest_framework import status

from forum.tests_setup import UserSetupMixin
from .models import Investor, InvestorStartup
from startups.models import Startup


# Create your tests here.
class SavedStartupsByInvestorTestCase(UserSetupMixin):

    def setUp(self) -> None:
        super().setUp()

        self.startup1 = Startup.objects.create(
            user=self.test_user,
            name='test name1',
            location='test location',
            description='test description',
            contacts={'phone': 'test phone'}
        )

        self.startup2 = Startup.objects.create(
            user=self.test_user,
            name='test name2',
            location='test location',
            description='test description',
            contacts={'phone': 'test phone'},
            is_deleted=True
        )

        self.startup3 = Startup.objects.create(
            user=self.test_user,
            name='test name3',
            location='test location',
            description='test description',
            contacts={'phone': 'test phone'}
        )

        self.investor1 = Investor.objects.create(user=self.test_user, contacts={'phone': 'test investor1 phone'})
        self.investor2 = Investor.objects.create(user=self.test_user, contacts={'phone': 'test investor2 phone'})

        InvestorStartup.objects.create(investor=self.investor1, startup=self.startup1)
        InvestorStartup.objects.create(investor=self.investor1, startup=self.startup2)
        InvestorStartup.objects.create(investor=self.investor1, startup=self.startup3)
        InvestorStartup.objects.create(investor=self.investor2, startup=self.startup3)

        post_body = {
            'name_space_id': self.investor1.investor_id,
            'name_space_name': 'investor'
        }
        self.client.post(reverse('users:namespace_selection'), data=post_body)

    def test_get_list_of_saved_startups_by_investor(self):

        startup1 = {
            "startup_id": self.startup1.startup_id,
            "size": None,
            "project": None,
            "name": self.startup1.name,
            "location": self.startup1.location,
            "startup_logo": self.startup1.startup_logo,
            "description": self.startup1.description,
            "last_updated": self.startup1.last_updated.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "created_at": self.startup1.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "contacts": self.startup1.contacts,
            "is_deleted": self.startup1.is_deleted,
            "user": self.test_user.user_id
        }
        startup3 = {
            "startup_id": self.startup3.startup_id,
            "size": None,
            "project": None,
            "name": self.startup3.name,
            "location": self.startup3.location,
            "startup_logo": self.startup3.startup_logo,
            "description": self.startup3.description,
            "last_updated": self.startup3.last_updated.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "created_at": self.startup3.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "contacts": self.startup3.contacts,
            "is_deleted": self.startup3.is_deleted,
            "user": self.test_user.user_id
        }

        for query_params, expected_data in [
            (None, [startup1, startup3]),
            ({'filter': json.dumps({"name": "name1"})}, [startup1]),
            ({'order_by': '-name'}, [startup3, startup1]),
        ]:

            response = self.client.get(
                reverse(
                    'users:saved_startups',
                    kwargs={'user_id': self.test_user.user_id, 'investor_id': self.investor1.investor_id}
                ),
                query_params
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                "Status code is different from 200"
            )
            self.assertEqual(
                response.json(),
                expected_data,
                "Received list does not match the expected one"
            )

    def test_get_list_of_saved_startups_by_investor_failed(self):
        response = self.client.get(
            reverse(
                'users:saved_startups',
                kwargs={'user_id': self.test_user.user_id, 'investor_id': self.investor1.investor_id}
            ),
            {'filter': "name"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "Status code is different from 400")
        self.assertEqual(
            response.json(),
            {'error': 'Invalid filter parameter'},
            "Filter is valid"
        )


class UnsaveStartupByInvestorTestCase(UserSetupMixin):

    def setUp(self):
        super().setUp()

        self.startup1 = Startup.objects.create(
            user=self.test_user,
            name='test name1',
            location='test location',
            description='test description',
            contacts={'phone': 'test phone'}
        )
        self.investor1 = Investor.objects.create(user=self.test_user, contacts={'phone': 'test investor1 phone'})
        InvestorStartup.objects.create(investor=self.investor1, startup=self.startup1)

        post_body = {
            'name_space_id': self.investor1.investor_id,
            'name_space_name': 'investor'
        }
        self.client.post(reverse('users:namespace_selection'), data=post_body)

    def test_unsave_startup(self):
        response = self.client.delete(
            reverse(
                'unsave_startup',
                kwargs={'startup_id': self.startup1.startup_id}
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, "Status code is different from 204")
        self.assertIsNone(response.data, "Content exists")

    def test_unsave_startup_failed(self):
        response = self.client.delete(
            reverse(
                'unsave_startup',
                kwargs={'startup_id': 23456}
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Status code is different from 404")
        self.assertEqual(
            response.json(),
            {'error': 'Subscription is not found'},
            "Response body does not match the expected one"
        )
