import random
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

from swipe.models import House, HouseNews, HouseImage, ClientHouseFavourites, DeveloperHouse
from users.models import User, Developer


class TestHouseViewSetAPI(APITestCase):
    """ Test module for houses API """

    faker = Faker()

    def create_client(self, black_list: tuple=tuple()) -> tuple[User, str]:
        '''create test client'''
        phone_numbers = ['+38(093)134-02-39', '+38(093)135-02-39', '+38(093)136-02-39']
        for phone_number in black_list:
            phone_numbers.remove(phone_number)
        user_data = {'phone_number': random.choice(phone_numbers), 
            'email': self.faker.email(), 'password': self.faker.name()}
        phone_numbers.remove(user_data["phone_number"])
        self.client.post('/auth/users/', user_data)
        u = User.objects.get(email=user_data['email'])
        u.is_active = True
        u.save()
        return u, user_data['password']

    def client_authenticate(self) -> User:
        '''create client and authorize it'''
        u, user_password = self.create_client()
        response = self.client.post('/auth/token/login/', {'email': u.email, 'password': user_password})
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

    def test_unauthorized_user_can_not_create_house(self):
        res = self.client.post('/swipe/api/houses/', dict(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=5, floors=13
        ))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_client_can_not_create_house(self):
        self.client_authenticate()
        res = self.client.post('/swipe/api/houses/', dict(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=5, floors=13
        ))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_developer_can_create_house(self):
        self.developer_authenticate()
        res = self.client.post('/swipe/api/houses/', dict(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=5, floors=13
        ))
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
    def test_admin_can_create_house(self):
        self.admin_authenticate()
        res = self.client.post('/swipe/api/houses/', dict(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=5, floors=13
        ))
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_developer_can_get_list_of_its_houses(self):
        House.objects.create(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=5, floors=13
        )

        self.developer_authenticate()
        self.client.post('/swipe/api/houses/', dict(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=5, floors=13
        ))
        res = self.client.get('/swipe/api/houses/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_developer_can_get_its_house(self):
        self.developer_authenticate()
        response = self.client.post('/swipe/api/houses/', dict(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=5, floors=13
        ))
        pk = response.data.get('id')
        res = self.client.get(f'/swipe/api/houses/{pk}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data['status'], str)
        self.assertEqual(res.data['status'], '2')

    def test_admin_can_get_all_houses(self):
        self.admin_authenticate()
        House.objects.create(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=5, floors=13
        )
        House.objects.create(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=5, floors=13
        )
        res = self.client.get(f'/swipe/api/houses/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_developer_can_update_its_house(self):
        self.developer_authenticate()
        response = self.client.post('/swipe/api/houses/', dict(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=5, floors=13
        ))
        pk = response.data.get('id')
        res = self.client.put(f'/swipe/api/houses/{pk}/', dict(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=5, floors=13
        ))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.patch(f'/swipe/api/houses/{pk}/', dict(
            name=self.faker.name(),
            description=self.faker.address(),
        ))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_developer_can_delete_its_house(self):
        self.developer_authenticate()
        response = self.client.post('/swipe/api/houses/', dict(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=5, floors=13
        ))
        pk = response.data.get('id')
        res = self.client.delete(f'/swipe/api/houses/{pk}/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_client_can_not_update_house_information(self):
        u = self.developer_authenticate()
        response = self.client.post('/swipe/api/houses/', dict(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=5, floors=13
        ))
        pk = response.data.get('id')

        Developer.objects.get(user=u).delete()

        res = self.client.patch(f'/swipe/api/houses/{pk}/', dict(
            name=self.faker.name(),
            description=self.faker.address(),
        ))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_developer_can_add_house_news(self):
        self.developer_authenticate()
        response = self.client.post('/swipe/api/houses/', dict(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=5, floors=13
        ))
        house_pk = response.data.get('id')
        response = self.client.post('/swipe/api/house_news/', dict(
            house=house_pk,
            header=self.faker.name(),
            body=self.faker.address()
        ))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_client_can_not_add_house_news(self):
        self.client_authenticate()
        house = House.objects.create(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=5, floors=13
        )
        response = self.client.post('/swipe/api/house_news/', dict(
            house=house.pk,
            header=self.faker.name(),
            body=self.faker.address()
        ))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_developer_can_delete_house_news(self):
        self.developer_authenticate()
        response = self.client.post('/swipe/api/houses/', dict(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=5, floors=13
        ))
        house_pk = response.data.get('id')
        response = self.client.post('/swipe/api/house_news/', dict(
            house=house_pk,
            header=self.faker.name(),
            body=self.faker.address()
        ))
        news_pk = response.data.get('id')
        response = self.client.delete(f'/swipe/api/house_news/{news_pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
