import json

from rest_framework.reverse import reverse
from rest_framework import status

from forum.tests_setup import UserSetupMixin
from startups.models import StartupSize, Startup
from projects.models import Project, ProjectStatus
from users.models import CustomUser


class StartupSizesTestCase(UserSetupMixin):
    CREATE_OBJ_COUNT: int = 5

    def setUp(self) -> None:
        super().setUp()

        for i in range(self.CREATE_OBJ_COUNT):
            StartupSize.objects.create(
                name="test size",
                people_count_min=20,
                people_count_max=30
            )

    def test_startup_sizes_list(self):
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


class BaseUserStartupsTestCase(UserSetupMixin):

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

        self.startup_size = StartupSize.objects.create(
            name="test size", people_count_min=20, people_count_max=30
        )

        self.startup3 = Startup.objects.create(
            user=self.test_user,
            name='test name3',
            size=self.startup_size,
            location='test location',
            description='test description',
            contacts={'phone': 'test phone'}
        )

        project_status = ProjectStatus.objects.create(title='title test')

        self.project = Project.objects.create(
            startup=self.startup3, status=project_status, title='title test'
        )

        self.startup3.project = self.project
        self.startup3.save()

        self.other_test_user = CustomUser.objects.create_user(
            first_name="other_test_first",
            last_name="other_test_last",
            email="other_test@gmail.com",
            password="other_test_password"
        )


class UserStartupsTestCase(BaseUserStartupsTestCase):

    def test_get_startups_list(self):
        response = self.client.get(reverse('users:user_startups', kwargs={'user_id': self.test_user.user_id}))
        expected_data = [
            {
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
            },
            {
                "startup_id": self.startup3.startup_id,
                "size": {
                    "size_id": self.startup_size.size_id,
                    "name": self.startup_size.name,
                    "people_count_min": self.startup_size.people_count_min,
                    "people_count_max": self.startup_size.people_count_max
                },
                "project": {
                    "title": self.project.title,
                    "last_updated": self.project.last_updated.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                },
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
        ]

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Status code is different from 200"
        )
        self.assertEqual(
            response.json(),
            expected_data,
            "Received json does not match the expected one"
        )

    def test_get_startups_empty_list(self):
        response = self.client.get(reverse('users:user_startups', kwargs={'user_id': 6666}))

        self.assertEqual(response.status_code, status.HTTP_200_OK, "Status code is different from 200")

        self.assertEqual(len(response.json()), 0, "The number of objects received is more than 0")

    def test_create_startup(self):
        response = self.client.post(
            reverse('users:user_startups', kwargs={'user_id': self.test_user.user_id}),
            {
                'user': self.test_user.user_id,
                'name': 'test name4',
                'location': 'test location',
                'description': 'test description',
                'contacts': json.dumps({'phone': 'test phone'})
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Status code is different from 201")

        self.assertIn('startup_id', response.json())

        startup = Startup.objects.get(startup_id=response.json()['startup_id'])

        self.assertEqual(startup.user, self.test_user)
        self.assertEqual(startup.name, 'test name4')
        self.assertEqual(startup.location, 'test location')
        self.assertEqual(startup.startup_logo, None)
        self.assertEqual(startup.description, 'test description')
        self.assertIsNotNone(startup.last_updated)
        self.assertIsNotNone(startup.created_at)
        self.assertEqual(startup.contacts, {'phone': 'test phone'})
        self.assertEqual(startup.is_deleted, False)
        self.assertEqual(startup.size, None)
        with self.assertRaises(Project.DoesNotExist):
            startup.project
        self.assertEqual(startup.startup_id, response.json()['startup_id'])

    def test_create_startup_failed(self):
        response = self.client.post(
            reverse('users:user_startups', kwargs={'user_id': self.test_user.user_id}),
            {'user': self.test_user.user_id, 'name': 'test name5'}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "Status code is different from 400")
        self.assertEqual(
            response.json(),
            {
                'location': ['This field is required.'],
                'description': ['This field is required.'],
                'contacts': ['This field is required.']
            },
            "Response body does not match the expected one"
        )

    def test_create_startup_failed_bad_user_id(self):
        response = self.client.post(
            reverse('users:user_startups', kwargs={'user_id': self.test_user.user_id}),
            {
                'user': self.other_test_user.user_id,
                'name': 'test name4',
                'location': 'test location',
                'description': 'test description',
                'contacts': json.dumps({'phone': 'test phone'})
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "Status code is different from 400")
        self.assertEqual(
            response.json(),
            {'user': ['User does not match the one from url']},
            "Response body does not match the expected one"
        )


class UserStartupTestCase(BaseUserStartupsTestCase):

    def test_get_startup(self):
        response = self.client.get(
            reverse(
                'users:user_startup',
                kwargs={'user_id': self.test_user.user_id, 'startup_id': self.startup3.startup_id}
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, "Status code is different from 200")

        self.assertTrue(isinstance(response.json(), dict))

        self.assertIn('startup_id', response.json())
        self.assertEqual(response.json()['startup_id'], self.startup3.startup_id, "startup_id is not correct")

        self.assertIn('size', response.json())
        self.assertTrue(isinstance(response.json()['size'], dict))
        self.assertEqual(len(response.json()['size']), 4, "Length of size object is not correct")

        self.assertIn('project', response.json())
        self.assertTrue(isinstance(response.json()['project'], dict))
        self.assertListEqual(
            list(response.json()['project'].keys()), ['title', 'last_updated'], "Project keys are bad"
        )

    def test_get_startup_failed(self):
        for user_id, startup_id in [
            (7777, self.startup3.startup_id),
            (self.test_user.user_id, 8888),
            (self.test_user.user_id, self.startup2.startup_id)
        ]:
            with self.subTest(user_id=user_id, startup_id=startup_id):
                response = self.client.get(
                    reverse('users:user_startup', kwargs={'user_id': user_id, 'startup_id': startup_id})
                )

                self.assertEqual(
                    response.status_code, status.HTTP_404_NOT_FOUND, "Status code is different from 404"
                )
                self.assertEqual(
                    response.json(),
                    {'detail': 'No Startup matches the given query.'},
                    "Response body does not match the expected one"
                )

    def test_update_startup(self):
        response = self.client.patch(
            reverse(
                'users:user_startup',
                kwargs={'user_id': self.test_user.user_id, 'startup_id': self.startup3.startup_id}
            ),
            {'name': 'test new name', 'location': 'test mew location'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, "Status code is different from 200")

        self.assertIn('user', response.json())
        self.assertEqual(response.json()['user'], self.test_user.user_id, "user_id is not correct")

        self.assertIn('name', response.json())
        self.assertEqual(response.json()['name'], 'test new name', "name is not correct")

        self.assertIn('location', response.json())
        self.assertEqual(response.json()['location'], 'test mew location', "location is not correct")

        startup = Startup.objects.get(startup_id=self.startup3.startup_id)

        self.assertEqual(startup.name, 'test new name', "name is not correct")

        self.assertEqual(startup.location, 'test mew location', "location is not correct")

    def test_update_startup_failed_bad_request(self):
        response = self.client.patch(
            reverse(
                'users:user_startup',
                kwargs={'user_id': self.test_user.user_id, 'startup_id': self.startup3.startup_id}
            ),
            {'name': "test" * 201, 'location': 'test mew location'}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "Status code is different from 400")
        self.assertEqual(
            response.json(),
            {'name': ['Ensure this field has no more than 200 characters.']},
            "Response body does not match the expected one"
        )

        startup = Startup.objects.get(startup_id=self.startup3.startup_id)

        self.assertNotEqual(startup.location, 'test mew location', "Field was updated")

        self.assertNotEqual(startup.name, "test" * 201, "Field was updated")

    def test_update_startup_failed_not_found(self):
        for user_id, startup_id in [
            (3333, self.startup3.startup_id),
            (self.test_user.user_id, 4444),
            (self.test_user.user_id, self.startup2.startup_id)
        ]:
            with self.subTest(user_id=user_id, startup_id=startup_id):
                response = self.client.patch(
                    reverse('users:user_startup', kwargs={'user_id': user_id, 'startup_id': startup_id}),
                    {'location': 'test mew location'}
                )

                self.assertEqual(
                    response.status_code, status.HTTP_404_NOT_FOUND, "Status code is different from 404"
                )
                self.assertEqual(
                    response.json(),
                    {'detail': 'No Startup matches the given query.'},
                    "Response body does not match the expected one"
                )

    def test_delete_startup(self):
        response = self.client.delete(
            reverse(
                'users:user_startup',
                kwargs={'user_id': self.test_user.user_id, 'startup_id': self.startup3.startup_id}
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, "Status code is different from 204")

        self.assertIsNone(response.data, "Content exists")

        startup = Startup.objects.get(startup_id=self.startup3.startup_id)

        self.assertTrue(startup.is_deleted)

    def test_delete_startup_failed(self):
        for user_id, startup_id in [
            (5555, self.startup1.startup_id),
            (self.test_user.user_id, 6666),
            (self.test_user.user_id, self.startup2.startup_id)
        ]:
            with self.subTest(user_id=user_id, startup_id=startup_id):
                response = self.client.delete(
                    reverse('users:user_startup', kwargs={'user_id': user_id, 'startup_id': startup_id})
                )

                self.assertEqual(
                    response.status_code, status.HTTP_404_NOT_FOUND, "Status code is different from 404"
                )
                self.assertEqual(
                    response.json(),
                    {'detail': 'No Startup matches the given query.'},
                    "Response body does not match the expected one"
                )
