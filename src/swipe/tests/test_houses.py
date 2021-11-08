import random

from django.urls import reverse_lazy
from faker import Faker
from rest_framework import status
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, APITestCase

from swipe.models import Announcement, Flat, House, HouseNews, HouseImage, ClientHouseFavourites, DeveloperHouse
from swipe.serializers import HouseListSerializer, HouseNewsSerializer, HouseSerializer
from users.models import User, Developer


class GetAllHousesTest(APITestCase):
    """ Test class for getting list of houses API"""

    def setUp(self):
        self.faker = Faker()
        self.factory = APIRequestFactory()
        self.admin_user = User.objects.create_superuser(email='admin@admin.com', 
            phone_number='+38(098)134-02-39', password='123')
        self.first_client = User.objects.create_user(email='first_client@gmail.com', 
            phone_number='+38(098)135-02-39', password='123').client
        self.second_client = User.objects.create_user(email='second_client@gmail.com', 
            phone_number='+38(098)136-02-39', password='123').client
        self.developer = User.objects.create_user(email='developer@gmail.com', 
            phone_number='+38(098)137-02-39', password='123')
        self.developer = Developer.objects.create(user=self.developer)
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
        DeveloperHouse.objects.create(house=house, developer=self.developer)
        House.objects.create(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126747788, 30.721379743314993',
            housings=2, sections=5, floors=13
        )
        flat = Flat.objects.create(house=house, housing=1, section=1, floor=1, number=1, status=True, square_meter_price=12500)
        Announcement.objects.create(**{
            "address": self.faker.name(),
            'flat': flat,
            "foundation_document": "1",
            "appointment": "1",
            "rooms": "1",
            "layout": "1",
            "state": "1",
            "total_area": 40.2,
            "has_balcony": "1",
            "calculation_options": "1",
            "commision": random.randint(1, 20),
            "communication": self.faker.name(),
            "description": self.faker.name(),
            "price": random.randint(14000, 45000),
            "advertiser": self.first_client,
            "moder_status": 2,
            "available_status": 1
        })

    def test_unauthorized_user_can_not_get_houses_list(self):
        response = self.client.get(reverse_lazy('swipe:house-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_client_can_get_active_houses_list(self):
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}'
        )
        response = self.client.get(reverse_lazy('swipe:house-list'))
        request = self.factory.get(reverse_lazy('swipe:house-list'))
        houses = House.objects.filter(pk__in={
            an.flat.house.pk for an in Announcement.objects.all() if an.flat is not None
        })
        serializer = HouseListSerializer(houses, many=True, context={'request': Request(request)})
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_superuser_can_get_houses_list(self):
        response = self.client.post('/auth/token/login/', {'email': self.admin_user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}'
        )
        response = self.client.get(reverse_lazy('swipe:house-list'))
        request = self.factory.get(reverse_lazy('swipe:house-list'))
        houses = House.objects.all()
        serializer = HouseListSerializer(houses, many=True, context={'request': Request(request)})
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_developer_can_get_list_of_his_houses(self):
        response = self.client.post('/auth/token/login/', {'email': self.developer.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}'
        )
        response = self.client.get(reverse_lazy('swipe:house-list'))
        request = self.factory.get(reverse_lazy('swipe:house-list'))
        houses = House.objects.filter(pk__in=[
                dv.house.pk for dv in DeveloperHouse.objects.filter(
                    developer=self.developer)
        ])
        serializer = HouseListSerializer(houses, many=True, context={'request': Request(request)})
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateHouseTest(APITestCase):
    '''Test class for testing house creation API'''

    def setUp(self):
        self.faker = Faker()
        self.admin_user = User.objects.create_superuser(email='admin@admin.com', 
            phone_number='+38(098)134-02-39', password='123')
        self.first_client = User.objects.create_user(email='first_client@gmail.com', 
            phone_number='+38(098)135-02-39', password='123').client
        self.second_client = User.objects.create_user(email='second_client@gmail.com', 
            phone_number='+38(098)136-02-39', password='123').client
        self.developer = User.objects.create_user(email='developer@gmail.com', 
            phone_number='+38(098)137-02-39', password='123')
        self.developer = Developer.objects.create(user=self.developer)

    def test_unauthorized_user_can_not_create_house(self):
        response = self.client.post(reverse_lazy('swipe:house-list'), dict(
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
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_client_can_not_create_house(self):
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}'
        )
        response = self.client.post(reverse_lazy('swipe:house-list'), dict(
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def developer_can_create_house(self):
        #TODO API accepts empty list of images, but not here
        response = self.client.post('/auth/token/login/', {'email': self.developer.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}'
        )
        response = self.client.post(reverse_lazy('swipe:house-list'), dict(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=5, floors=13, images=[]
        ))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def admin_can_create_house(self):
        #TODO API accepts empty list of images, but not here
        response = self.client.post('/auth/token/login/', {'email': self.admin_user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}'
        )
        response = self.client.post(reverse_lazy('swipe:house-list'), {
            "name":self.faker.name(),
            "description":self.faker.address(),
            "status":'2', "type":'1', 
            "_class":'2', "building_technology":'1', "territory":'2',
            "sea_distance":1000.1, "communal_payments":'1', "ceiling_height":2.78,
            "has_gas":'2', "heating_type":'1', "sewerage":'1', "water_supply":'1',
            "calculation_type":'Ипотека', "perpose":'Жилое помещение',
            "summ_in_contract":'Неполная', "coords":'46.43352126727788, 30.721379643314993',
            "housings":2, "sections":5, "floors":13, "images":[]
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class GetHouseDetailsTest(APITestCase):
    '''Test class for getting house details API'''

    def setUp(self):
        self.faker = Faker()
        self.admin_user = User.objects.create_superuser(email='admin@admin.com', 
            phone_number='+38(098)134-02-39', password='123')
        self.first_client = User.objects.create_user(email='first_client@gmail.com', 
            phone_number='+38(098)135-02-39', password='123').client
        self.second_client = User.objects.create_user(email='second_client@gmail.com', 
            phone_number='+38(098)136-02-39', password='123').client
        self.developer = User.objects.create_user(email='developer@gmail.com', 
            phone_number='+38(098)137-02-39', password='123')
        self.developer = Developer.objects.create(user=self.developer)
        self.house = House.objects.create(
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
        flat = Flat.objects.create(house=self.house, housing=1, section=1, floor=1, number=1, status=True, square_meter_price=12500)
        Announcement.objects.create(**{
            "address": self.faker.name(),
            'flat': flat,
            "foundation_document": "1",
            "appointment": "1",
            "rooms": "1",
            "layout": "1",
            "state": "1",
            "total_area": 40.2,
            "has_balcony": "1",
            "calculation_options": "1",
            "commision": random.randint(1, 20),
            "communication": self.faker.name(),
            "description": self.faker.name(),
            "price": random.randint(14000, 45000),
            "advertiser": self.first_client,
            "moder_status": 2,
            "available_status": 1
        })
    
    def test_client_can_get_house_details(self):
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')
        response = self.client.get(reverse_lazy('swipe:house-detail', kwargs={'pk': self.house.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], '2')
        self.assertEqual(response.data['type'], '1')
        self.assertEqual(response.data['calculation_type'], 'Ипотека')


class UpdateHouseTest(APITestCase):
    '''Test class for updating existing house'''
    def setUp(self):
        self.faker = Faker()
        self.developer = User.objects.create_user(email='developer@gmail.com', 
            phone_number='+38(098)137-02-39', password='123')
        self.developer = Developer.objects.create(user=self.developer)
        self.house = House.objects.create(
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
        self.house2 = House.objects.create(
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
        DeveloperHouse.objects.create(house=self.house, developer=self.developer)

    def test_developer_can_not_update_not_his_house(self):
        response = self.client.post('/auth/token/login/', {'email': self.developer.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')
        response = self.client.put(reverse_lazy('swipe:house-detail', kwargs={'pk': self.house2.pk}), {
            "name":self.faker.name(),
            "description":self.faker.address(),
            "status":'1', "type":'2', 
            "_class":'2', "building_technology":'1', "territory":'2',
            "sea_distance":1000.1, "communal_payments":'1', "ceiling_height":2.78,
            "has_gas":'2', "heating_type":'1', "sewerage":'1', "water_supply":'1',
            "calculation_type":'Ипотека', "perpose":'Жилое помещение',
            "summ_in_contract":'Неполная', "coords":'46.43352126727788, 30.721379643314993',
            "housings":2, "sections":5, "floors":13, "images":[]
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.patch(reverse_lazy('swipe:house-detail', kwargs={'pk': self.house2.pk}), {
            "status":'1', "type":'2'
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_developer_can_not_update_not_his_house(self):
        response = self.client.post('/auth/token/login/', {'email': self.developer.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')
        response = self.client.patch(reverse_lazy('swipe:house-detail', kwargs={'pk': self.house.pk}), {
            "status":'1', "type":'2'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DeleteHouseTest(APITestCase):
    """Test class for delete existing house"""
    def setUp(self):
        self.faker = Faker()
        self.developer = User.objects.create_user(email='developer@gmail.com', 
            phone_number='+38(098)137-02-39', password='123')
        self.developer = Developer.objects.create(user=self.developer)
        self.house = House.objects.create(
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
        DeveloperHouse.objects.create(house=self.house, developer=self.developer)

    def test_house_deletion(self):
        response = self.client.post('/auth/token/login/', {'email': self.developer.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')
        response = self.client.delete(reverse_lazy('swipe:house-detail', kwargs={'pk': self.house.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class GetAllHouseNewsTest(APITestCase):
    '''Test class for getting list of all house news'''
        
    def setUp(self):
        self.faker = Faker()
        self.developer = User.objects.create_user(email='developer@gmail.com', 
            phone_number='+38(098)137-02-39', password='123')
        self.developer = Developer.objects.create(user=self.developer)
        self.house = House.objects.create(
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
        DeveloperHouse.objects.create(house=self.house, developer=self.developer)
        HouseNews.objects.create(house=self.house, header=self.faker.name(), body=self.faker.address())
        HouseNews.objects.create(house=self.house, header=self.faker.name(), body=self.faker.address())
        HouseNews.objects.create(house=self.house, header=self.faker.name(), body=self.faker.address())

    def test_get_house_news_list(self):
        response = self.client.post('/auth/token/login/', {'email': self.developer.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')
        response = self.client.get(f'/swipe/api/house_news/?house={self.house.pk}')
        house_news = HouseNews.objects.filter(house=self.house).order_by('-publication_date')
        serializer = HouseNewsSerializer(house_news, many=True)
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateHouseNewsTest(APITestCase):
    '''Test class for creating house news'''

    def setUp(self):
        self.faker = Faker()
        self.first_client = User.objects.create_user(email='first_client@gmail.com', 
            phone_number='+38(098)135-02-39', password='123').client
        self.developer = User.objects.create_user(email='developer@gmail.com', 
            phone_number='+38(098)137-02-39', password='123')
        self.developer = Developer.objects.create(user=self.developer)
        self.house = House.objects.create(
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
        DeveloperHouse.objects.create(house=self.house, developer=self.developer)
        self.valid_form = {
            'house': self.house.pk,
            'header': self.faker.name(),
            'body': self.faker.address()
        }

        self.invalid_form = {
            'house': self.house.pk + 1,
            'header': self.faker.name(),
            'body': self.faker.address()
        }

    def test_create_valid_house_news(self):
        response = self.client.post('/auth/token/login/', {'email': self.developer.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')
        response = self.client.post(f'/swipe/api/house_news/', self.valid_form)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_house_news(self):
        response = self.client.post('/auth/token/login/', {'email': self.developer.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')
        response = self.client.post(f'/swipe/api/house_news/', self.invalid_form)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_client_can_not_create_house(self):
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')
        response = self.client.post(f'/swipe/api/house_news/', self.valid_form)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DeleteHouseNewsTest(APITestCase):
    '''Test class for delete house news'''

    def setUp(self):
        self.faker = Faker()
        self.developer = User.objects.create_user(email='developer@gmail.com', 
            phone_number='+38(098)137-02-39', password='123')
        self.developer = Developer.objects.create(user=self.developer)
        self.house = House.objects.create(
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
        DeveloperHouse.objects.create(house=self.house, developer=self.developer)
        self.house_news_obj = HouseNews.objects.create(house=self.house, header=self.faker.name(), body=self.faker.address())

    def test_valid_house_news_delete(self):
        response = self.client.post('/auth/token/login/', {'email': self.developer.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')
        response = self.client.delete(reverse_lazy('swipe:housenews-detail', kwargs={'pk': self.house_news_obj.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_house_news_delete(self):
        response = self.client.post('/auth/token/login/', {'email': self.developer.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')
        response = self.client.delete(reverse_lazy('swipe:housenews-detail', kwargs={'pk': 100}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class GetClientHouseFavouritesTest(APITestCase):
    '''Test class for GET client house favourites'''

    def setUp(self):
        self.faker = Faker()
        self.factory = APIRequestFactory()
        self.admin_user = User.objects.create_superuser(email='admin@admin.com', 
            phone_number='+38(098)134-02-39', password='123')
        self.first_client = User.objects.create_user(email='first_client@gmail.com', 
            phone_number='+38(098)135-02-39', password='123').client
        self.second_client = User.objects.create_user(email='second_client@gmail.com', 
            phone_number='+38(098)136-02-39', password='123').client
        self.developer = User.objects.create_user(email='developer@gmail.com', 
            phone_number='+38(098)137-02-39', password='123')
        self.developer = Developer.objects.create(user=self.developer)
        self.house = House.objects.create(
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
        DeveloperHouse.objects.create(house=self.house, developer=self.developer)
        House.objects.create(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126747788, 30.721379743314993',
            housings=2, sections=5, floors=13
        )
        ClientHouseFavourites.objects.create(house=self.house, client=self.first_client)

    def test_get_client_list_of_house_favourites(self):
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}'
        )
        response = self.client.get(reverse_lazy('swipe:house-get_client_favourites'))
        request = self.factory.get(reverse_lazy('swipe:house-get_client_favourites'))
        client_house_favourites = House.objects.filter(
            pk__in=[cf.house.pk for cf in ClientHouseFavourites.objects.filter(
                client=self.first_client
            )]
        )
        serializer = HouseListSerializer(client_house_favourites, many=True, context={'request': Request(request)})
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AddToFavouritesAndRemoveTest(APITestCase):
    '''Test for add house to favourites'''

    def setUp(self):
        self.faker = Faker()
        self.factory = APIRequestFactory()
        self.first_client = User.objects.create_user(email='first_client@gmail.com', 
            phone_number='+38(098)135-02-39', password='123').client
        self.developer = User.objects.create_user(email='developer@gmail.com', 
            phone_number='+38(098)137-02-39', password='123')
        self.developer = Developer.objects.create(user=self.developer)
        self.house = House.objects.create(
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
        DeveloperHouse.objects.create(house=self.house, developer=self.developer)

    def test_add_house_to_client_favourites(self):
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}'
        )
        response = self.client.post(reverse_lazy('swipe:house-add_to_client_favourites', kwargs={'pk': self.house.pk}), {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.delete(reverse_lazy('swipe:house-remove_from_client_favourites', kwargs={'pk': self.house.pk}), {})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.delete(reverse_lazy('swipe:house-remove_from_client_favourites', kwargs={'pk': self.house.pk}), {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
