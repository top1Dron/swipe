from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User, Client, Developer, Agent, Notary


class TestUserAuth(APITestCase):
    faker = Faker()

    def client_authenticate(self) -> User:
        '''create client and authorize it'''

        user_data = {'phone_number': '+38(093)134-02-39', 
            'email': self.faker.email(), 'password': self.faker.name()}
        self.client.post('/auth/users/', user_data)
        u = User.objects.get(email=user_data['email'])
        u.is_active = True
        u.save()
        response = self.client.post('/auth/token/login/', {'email': user_data['email'], 'password': user_data['password']})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}'
        )
        return u
    
    def developer_authenticate(self) -> User:
        '''create developer and authorize it'''
        u = self.client_authenticate()
        Developer.objects.create(user=u)
        return u

    def admin_authenticate(self) -> User:
        '''create admin and authorize it'''
        u = self.client_authenticate()
        u.is_superuser = True
        u.is_staff = True
        u.save()
        return u

    def test_user_is_client(self):
        u = self.client_authenticate()
        self.assertNotEqual(u.user_client, None)

    def test_user_is_not_developer(self):
        u = self.client_authenticate()
        self.assertEqual(u.user_developer, None)

    def test_user_is_developer(self):
        u = self.developer_authenticate()
        self.assertNotEqual(u.user_developer, None)

    def test_user_is_not_admin(self):
        u = self.client_authenticate()
        self.assertEqual(u.is_superuser, False)

    def test_user_is_admin(self):
        u = self.admin_authenticate()
        self.assertEqual(u.is_superuser, True)

    def test_client_can_not_get_list_of_clients(self):
        self.client_authenticate()
        res = self.client.get('/users/api/clients/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_get_list_of_clients(self):
        self.admin_authenticate()
        res = self.client.get('/users/api/clients/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)