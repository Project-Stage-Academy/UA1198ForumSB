import unittest
from rest_framework.reverse import reverse
from rest_framework import status

from forum.tests_setup import UserSetupMixin
from projects.models import Industry, Project, ProjectStatus, ProjectSubscription
from startups.models import Startup
from investors.models import Investor


class IndustryModelTestCase(UserSetupMixin):
    CREATE_INDUSTRY_COUNT: int = 3

    def setUp(self) -> None:
        super().setUp()

        # create industries
        for i in range(self.CREATE_INDUSTRY_COUNT):
            Industry.objects.create(
                name=f"industry {i}",
                description=f"test description {i}"
            )

    @unittest.skip("Static data exists in database. Rewrite this test")
    def test_projects_industries(self):
        response = self.client.get(reverse('industries-list'))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Status code is different from 200"
        )
        self.assertEqual(
            len(response.json()),
            self.CREATE_INDUSTRY_COUNT,
            "The number of objects received is not equal to the number created"
        )


class ProjectSubscriptionTestCase(UserSetupMixin):

    def setUp(self) -> None:
        super().setUp()

        self.startup1 = Startup.objects.create(
            user=self.test_user,
            name='test name1',
            location='test location1',
            description='test description1',
            contacts={'phone': 'test phone1'}
        )

        self.startup2 = Startup.objects.create(
            user=self.test_user,
            name='test name2',
            location='test location2',
            description='test description2',
            contacts={'phone': 'test phone2'}
        )

        self.startup3 = Startup.objects.create(
            user=self.test_user,
            name='test name3',
            location='test location3',
            description='test description3',
            contacts={'phone': 'test phone3'}
        )

        self.project1 = Project.objects.create(
            startup=self.startup1,
            status=ProjectStatus.objects.filter().first(),
            budget=10000,
            title='title test1'
        )

        self.project2 = Project.objects.create(
            startup=self.startup2,
            status=ProjectStatus.objects.filter().first(),
            budget=10000,
            title='title test2'
        )

        self.project3 = Project.objects.create(
            startup=self.startup3,
            status=ProjectStatus.objects.filter().first(),
            budget=100,
            title='title test3'
        )

        self.investor1 = Investor.objects.create(user=self.test_user)
        self.investor2 = Investor.objects.create(user=self.test_user)

        self.project_subscription1 = ProjectSubscription.objects.create(
            project=self.project2,
            investor=self.investor1,
            part=555
        )

        self.project_subscription2 = ProjectSubscription.objects.create(
            project=self.project3,
            investor=self.investor2,
            part=100
        )

        post_body = {
            'name_space_id': self.investor1.investor_id,
            'name_space_name': 'investor'
        }
        self.client.post(reverse('users:namespace_selection'), data=post_body)

    def test_project_subscription(self):
        response = self.client.post(
            reverse('project-subscribe', kwargs={'project_id': self.project1.project_id}),
            {'part': 123}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Status code is different from 201")
        self.assertEqual(
            response.json(),
            "The investor has been successfully subscribed to the project.",
            "Response body does not match the expected one"
        )

    def test_project_re_subscription(self):
        response = self.client.post(
            reverse('project-subscribe', kwargs={'project_id': self.project2.project_id}),
            {'part': 123}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "Status code is different from 400")
        self.assertEqual(
            response.json(),
            {'non_field_errors': ['Investor already subscribed to the project.']},
            "Investor subscribed to the project more than once."
        )

    def test_full_budget_project_subscription(self):
        response = self.client.post(
            reverse('project-subscribe', kwargs={'project_id': self.project3.project_id}),
            {'part': 123}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "Status code is different from 400")
        self.assertEqual(
            response.json(),
            {'non_field_errors': ['Budget is full.']},
            "Investor subscribed to the project with full budget."
        )

    def test_bad_namespace_project_subscription(self):
        post_body = {
            'name_space_id': self.startup1.startup_id,
            'name_space_name': 'startup'
        }
        self.client.post(reverse('users:namespace_selection'), data=post_body)

        response = self.client.post(
            reverse('project-subscribe', kwargs={'project_id': self.project2.project_id}),
            {'part': 123}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, "Status code is different from 403")
        self.assertEqual(
            response.json(),
            {'detail': 'You do not have permission to perform this action.'},
            "Startup subscribed to the project."
        )
