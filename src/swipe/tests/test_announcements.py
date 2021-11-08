import logging
import random

from django.urls import reverse_lazy
from django.utils import timezone
from faker import Faker
from rest_framework import status
from rest_framework.request import Request
from rest_framework.test import APITestCase, APIRequestFactory
from swipe import serializers

from swipe.models import Announcement, AnnouncementImage, ClientAnnouncementFavourites, Flat, House
from swipe.serializers import AnnouncementListSerializer
from swipe.views import announcements
from users.models import User, Developer


logger = logging.getLogger(__name__)


class GetAllAnnouncementsTest(APITestCase):
    """ Test class for getting list of announcements API"""

    def setUp(self):
        self.faker = Faker()
        self.factory = APIRequestFactory()
        self.admin_user = User.objects.create_superuser(email='admin@admin.com', 
            phone_number='+38(098)134-02-39', password='123')
        self.first_client = User.objects.create_user(email='first_client@gmail.com', 
            phone_number='+38(098)135-02-39', password='123').client
        self.announcement_cottege = Announcement.objects.create(**{
            "address": self.faker.name(),
            "foundation_document": "1",
            "appointment": "1",
            "rooms": "1",
            "layout": "1",
            "state": "1",
            "total_area": random.uniform(1.0, 70.0),
            "has_balcony": "1",
            "calculation_options": "1",
            "commision": random.randint(1, 100),
            "communication": self.faker.name(),
            "description": self.faker.name(),
            "price": random.randint(14000, 45000),
            "moder_status": '2',
            "available_status": '1',
            "advertiser": self.first_client
        })
        self.announcement_cottege2 = Announcement.objects.create(**{
            "address": self.faker.name(),
            "foundation_document": "1",
            "appointment": "1",
            "rooms": "1",
            "layout": "1",
            "state": "1",
            "total_area": random.uniform(1.0, 70.0),
            "has_balcony": "1",
            "calculation_options": "1",
            "commision": random.randint(1, 100),
            "communication": self.faker.name(),
            "description": self.faker.name(),
            "price": random.randint(14000, 45000),
            "moder_status": '1',
            "available_status": '2',
            "advertiser": self.first_client
        })

    def test_unauthorized_user_can_not_get_list_of_announcements(self):
        response = self.client.get(reverse_lazy('swipe:announcement-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_client_can_get_only_available_and_moderated_announcements_list(self):
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}'
        )
        
        response = self.client.get(reverse_lazy('swipe:announcement-list'))
        request = self.factory.get(reverse_lazy('swipe:announcement-list'))
        announcements = Announcement.objects.filter(moder_status='2', available_status='1')
        serializer = AnnouncementListSerializer(announcements, many=True, context={'request': Request(request)})
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_get_announcements_list(self):
        response = self.client.post('/auth/token/login/', {'email': self.admin_user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}'
        )
        
        response = self.client.get(reverse_lazy('swipe:announcement-list'))
        request = self.factory.get(reverse_lazy('swipe:announcement-list'))
        announcements = Announcement.objects.all().order_by('-publication_date')
        serializer = AnnouncementListSerializer(announcements, many=True, context={'request': Request(request)})
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateAnnouncementTest(APITestCase):
    '''Test class for POST create announcement'''
    def setUp(self):
        self.faker = Faker()
        self.admin_user = User.objects.create_superuser(email='admin@admin.com', 
            phone_number='+38(098)134-02-39', password='123')
        self.first_client = User.objects.create_user(email='first_client@gmail.com', 
            phone_number='+38(098)135-02-39', password='123').client
        self.valid_form = {
            "address": self.faker.name(),
            "foundation_document": "1",
            "appointment": "1",
            "rooms": "1",
            "layout": "1",
            "state": "1",
            "total_area": random.uniform(1.0, 70.0),
            "has_balcony": "1",
            "calculation_options": "1",
            "commision": random.randint(1, 100),
            "communication": self.faker.name(),
            "description": self.faker.name(),
            "price": random.randint(14000, 45000),
            "advertiser": self.first_client.pk,
            'images': [dict()]
        }

        self.invalid_form = {
            "address": self.faker.name(),
            "foundation_document": 1,
            "appointment": "1",
            "rooms": "1",
            "layout": "1",
            "state": "1",
            "total_area": random.uniform(1.0, 70.0),
            "has_balcony": "1",
            "calculation_options": "1",
            "commision": random.randint(1, 100),
            "communication": self.faker.name(),
            "description": self.faker.name(),
            "price": random.randint(14000, 45000),
            "advertiser": self.first_client
        }

    def test_unauthorized_user_can_not_create_announcements(self):
        response = self.client.post(reverse_lazy('swipe:announcement-list'), self.valid_form)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def valid_announcement_creation(self):
        #TODO API accepts empty list of images, but not here
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}'
        )
        response = self.client.post(reverse_lazy('swipe:announcement-list'), self.valid_form)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['calculation_options'], '1')
        self.assertEqual(response.data['rooms'], '1')
        self.assertEqual(response.data['foundation_document'], '1')

    def test_invalid_announcement_creation(self):
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}'
        )
        response = self.client.post(reverse_lazy('swipe:announcement-list'), self.invalid_form)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GetClientAnnouncementsTest(APITestCase):
    '''Test class for GET client announcements'''

    def setUp(self):
        self.faker = Faker()
        self.factory = APIRequestFactory()
        self.admin_user = User.objects.create_superuser(email='admin@admin.com', 
            phone_number='+38(098)134-02-39', password='123')
        self.first_client = User.objects.create_user(email='first_client@gmail.com', 
            phone_number='+38(098)135-02-39', password='123').client
        self.second_client = User.objects.create_user(email='second_client@gmail.com', 
            phone_number='+38(098)136-02-39', password='123').client
        self.client_announcement = Announcement.objects.create(**{
            "address": self.faker.name(),
            "foundation_document": "1",
            "appointment": "1",
            "rooms": "1",
            "layout": "1",
            "state": "1",
            "total_area": random.uniform(1.0, 70.0),
            "has_balcony": "1",
            "calculation_options": "1",
            "commision": random.randint(1, 100),
            "communication": self.faker.name(),
            "description": self.faker.name(),
            "price": random.randint(14000, 45000),
            "moder_status": '2',
            "available_status": '1',
            "advertiser": self.first_client
        })
        self.not_client_announcement = Announcement.objects.create(**{
            "address": self.faker.name(),
            "foundation_document": "1",
            "appointment": "1",
            "rooms": "1",
            "layout": "1",
            "state": "1",
            "total_area": random.uniform(1.0, 70.0),
            "has_balcony": "1",
            "calculation_options": "1",
            "commision": random.randint(1, 100),
            "communication": self.faker.name(),
            "description": self.faker.name(),
            "price": random.randint(14000, 45000),
            "moder_status": '2',
            "available_status": '1',
            "advertiser": self.second_client
        })

    def test_unauthorized_user_can_not_get_list_of_his_announcements(self):
        response = self.client.get(reverse_lazy('swipe:announcement-get_client_announcements'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_get_his_announcements_list(self):
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}'
        )
        
        response = self.client.get(reverse_lazy('swipe:announcement-get_client_announcements'))
        request = self.factory.get(reverse_lazy('swipe:announcement-get_client_announcements'))
        all_announcements = Announcement.objects.all().order_by('-publication_date')
        client_announcements = Announcement.objects.filter(advertiser=self.first_client).order_by('-publication_date')
        all_announcements_serializer = AnnouncementListSerializer(all_announcements, many=True, context={'request': Request(request)})
        client_announcements_serializer = AnnouncementListSerializer(client_announcements, many=True, context={'request': Request(request)})
        self.assertEqual(response.data, client_announcements_serializer.data)
        self.assertNotEqual(response.data, all_announcements_serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetClientAnnouncementFavouritesTest(APITestCase):
    '''Test class for GET client announcement favourites'''

    def setUp(self):
        self.faker = Faker()
        self.factory = APIRequestFactory()
        self.first_client = User.objects.create_user(email='first_client@gmail.com', 
            phone_number='+38(098)135-02-39', password='123').client
        self.client_announcement = Announcement.objects.create(**{
            "address": self.faker.name(),
            "foundation_document": "1",
            "appointment": "1",
            "rooms": "1",
            "layout": "1",
            "state": "1",
            "total_area": random.uniform(1.0, 70.0),
            "has_balcony": "1",
            "calculation_options": "1",
            "commision": random.randint(1, 100),
            "communication": self.faker.name(),
            "description": self.faker.name(),
            "price": random.randint(14000, 45000),
            "moder_status": '2',
            "available_status": '1',
            "advertiser": self.first_client
        })
        self.not_client_announcement = Announcement.objects.create(**{
            "address": self.faker.name(),
            "foundation_document": "1",
            "appointment": "1",
            "rooms": "1",
            "layout": "1",
            "state": "1",
            "total_area": random.uniform(1.0, 70.0),
            "has_balcony": "1",
            "calculation_options": "1",
            "commision": random.randint(1, 100),
            "communication": self.faker.name(),
            "description": self.faker.name(),
            "price": random.randint(14000, 45000),
            "moder_status": '2',
            "available_status": '1',
            "advertiser": self.first_client
        })
        ClientAnnouncementFavourites.objects.create(announcement=self.client_announcement, client=self.first_client)

    def test_get_client_list_of_announcement_favourites(self):
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}'
        )
        response = self.client.get(reverse_lazy('swipe:announcement-get_client_favourites'))
        request = self.factory.get(reverse_lazy('swipe:announcement-get_client_favourites'))
        client_announcement_favourites = Announcement.objects.filter(
            pk__in=[cf.announcement.pk for cf in ClientAnnouncementFavourites.objects.filter(
                client=self.first_client
            )]
        )
        serializer = AnnouncementListSerializer(client_announcement_favourites, many=True, context={'request': Request(request)})
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AddToFavouritesAndRemoveTest(APITestCase):
    '''Test for add announcement to favourites'''

    def setUp(self):
        self.faker = Faker()
        self.factory = APIRequestFactory()
        self.first_client = User.objects.create_user(email='first_client@gmail.com', 
            phone_number='+38(098)135-02-39', password='123').client
        self.announcement = Announcement.objects.create(**{
            "address": self.faker.name(),
            "foundation_document": "1",
            "appointment": "1",
            "rooms": "1",
            "layout": "1",
            "state": "1",
            "total_area": random.uniform(1.0, 70.0),
            "has_balcony": "1",
            "calculation_options": "1",
            "commision": random.randint(1, 100),
            "communication": self.faker.name(),
            "description": self.faker.name(),
            "price": random.randint(14000, 45000),
            "moder_status": '2',
            "available_status": '1',
            "advertiser": self.first_client
        })

    def test_add_announcement_to_client_favourites_and_remove_it(self):
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}'
        )
        response = self.client.post(reverse_lazy('swipe:announcement-add_to_client_favourites', kwargs={'pk': self.announcement.pk}), {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.delete(reverse_lazy('swipe:announcement-remove_from_client_favourites', kwargs={'pk': self.announcement.pk}), {})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.delete(reverse_lazy('swipe:announcement-remove_from_client_favourites', kwargs={'pk': self.announcement.pk}), {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GetUnmoderatedAnnouncementsTest(APITestCase):
    '''Test for getting unmoderated announcements'''

    def setUp(self):
        self.faker = Faker()
        self.factory = APIRequestFactory()
        self.first_client = User.objects.create_user(email='first_client@gmail.com', 
            phone_number='+38(098)135-02-39', password='123').client
        self.admin_user = User.objects.create_superuser(email='admin@admin.com', 
            phone_number='+38(098)134-02-39', password='123')
        self.announcement = Announcement.objects.create(**{
            "address": self.faker.name(),
            "foundation_document": "1",
            "appointment": "1",
            "rooms": "1",
            "layout": "1",
            "state": "1",
            "total_area": random.uniform(1.0, 70.0),
            "has_balcony": "1",
            "calculation_options": "1",
            "commision": random.randint(1, 100),
            "communication": self.faker.name(),
            "description": self.faker.name(),
            "price": random.randint(14000, 45000),
            "moder_status": '1',
            "available_status": '1',
            "advertiser": self.first_client
        })
        self.announcement2 = Announcement.objects.create(**{
            "address": self.faker.name(),
            "foundation_document": "1",
            "appointment": "1",
            "rooms": "1",
            "layout": "1",
            "state": "1",
            "total_area": random.uniform(1.0, 70.0),
            "has_balcony": "1",
            "calculation_options": "1",
            "commision": random.randint(1, 100),
            "communication": self.faker.name(),
            "description": self.faker.name(),
            "price": random.randint(14000, 45000),
            "moder_status": '2',
            "available_status": '1',
            "advertiser": self.first_client
        })

    def test_client_can_not_get_list_of_unmoderated_announcements(self):
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}'
        )
        response = self.client.get(reverse_lazy('swipe:announcement-get_unmoderated_announcements'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_getting_list_of_unmoderated_announcements(self):
        response = self.client.post('/auth/token/login/', {'email': self.admin_user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}'
        )
        response = self.client.get(reverse_lazy('swipe:announcement-get_unmoderated_announcements'))
        request = self.factory.get(reverse_lazy('swipe:announcement-get_unmoderated_announcements'))
        announcements = Announcement.objects.filter(moder_status='1').order_by('publication_date')
        serializer = AnnouncementListSerializer(announcements, many=True, context={'request': Request(request)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, serializer.data)


class AnnouncementDetailsTest(APITestCase):
    '''Test class for getting announcement details, update and delete announcement API'''

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
        self.flat = Flat.objects.create(house=self.house, housing=1, section=1, floor=1, number=1, status=True, square_meter_price=12500)
        self.announcement = Announcement.objects.create(**{
            "address": self.faker.name(),
            'flat': self.flat,
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

        self.valid_patch_data = {
            "foundation_document": "1",
            "appointment": "1",
            "rooms": "1",
        }

        self.invalid_patch_data = {
            "foundation_document": "100",
            "appointment": "100",
            "rooms": "100",
        }
    
    def test_unauthorized_user_can_not_get_announcement_details(self):
        response = self.client.get(reverse_lazy('swipe:announcement-detail', kwargs={'pk': self.announcement.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_client_can_get_announcement_details(self):
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')
        response = self.client.get(reverse_lazy('swipe:announcement-detail', kwargs={'pk': self.announcement.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['flat'], self.flat.pk)
        self.assertEqual(response.data['appointment'], '1')
        self.assertEqual(response.data['calculation_options'], '1')
        self.assertEqual(response.data['state'], '1')
        self.assertAlmostEqual(response.data['total_area'], 40.2)

    def test_announcement_deletion(self):
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')
        response = self.client.delete(reverse_lazy('swipe:announcement-detail', kwargs={'pk': self.announcement.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_valid_announcement_update(self):
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')
        response = self.client.patch(reverse_lazy('swipe:announcement-detail', kwargs={'pk': self.announcement.pk}), self.valid_patch_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_announcement_update(self):
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')
        response = self.client.patch(reverse_lazy('swipe:announcement-detail', kwargs={'pk': self.announcement.pk}), self.invalid_patch_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
class UpdateAnnouncementToTheTopOfTheListTest(APITestCase):
    '''Test class for updating announcement to the top of the announcements\' list'''

    def setUp(self):
        self.faker = Faker()
        self.factory = APIRequestFactory()
        self.admin_user = User.objects.create_superuser(email='admin@admin.com', 
            phone_number='+38(098)134-02-39', password='123')
        self.first_client = User.objects.create_user(email='first_client@gmail.com', 
            phone_number='+38(098)135-02-39', password='123').client
        self.second_client = User.objects.create_user(email='second_client@gmail.com', 
            phone_number='+38(098)136-02-39', password='123').client
        self.announcement_cottege = Announcement.objects.create(**{
            "address": self.faker.name(),
            "foundation_document": "1",
            "appointment": "1",
            "rooms": "1",
            "layout": "1",
            "state": "1",
            "total_area": random.uniform(1.0, 70.0),
            "has_balcony": "1",
            "calculation_options": "1",
            "commision": random.randint(1, 100),
            "communication": self.faker.name(),
            "description": self.faker.name(),
            "price": random.randint(14000, 45000),
            "moder_status": '2',
            "available_status": '1',
            "advertiser": self.first_client
        })
        self.announcement_cottege2 = Announcement.objects.create(**{
            "address": 'test address',
            "foundation_document": "1",
            "appointment": "1",
            "rooms": "1",
            "layout": "1",
            "state": "1",
            "total_area": random.uniform(1.0, 70.0),
            "has_balcony": "1",
            "calculation_options": "1",
            "commision": random.randint(1, 100),
            "communication": self.faker.name(),
            "description": self.faker.name(),
            "price": random.randint(14000, 45000),
            "moder_status": '2',
            "available_status": '1',
            "advertiser": self.second_client
        })

    def test_unauthorized_user_can_not_update_announcement_to_the_top(self):
        response = self.client.patch(reverse_lazy('swipe:announcement-to_the_top', 
            kwargs={'pk': self.announcement_cottege.pk}), 
            {'publication_date': str(timezone.now())})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_client_can_not_update_not_his_announcement_to_the_top(self):
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')
        response = self.client.patch(
            reverse_lazy('swipe:announcement-to_the_top', kwargs={'pk': self.announcement_cottege2.pk}), 
            {'publication_date': str(timezone.now())})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_client_can_not_update_not_his_announcement_to_the_top(self):
        response = self.client.post('/auth/token/login/', {'email': self.first_client.user.email, 'password': '123'})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')
        response = self.client.patch(
            reverse_lazy('swipe:announcement-to_the_top', kwargs={'pk': self.announcement_cottege.pk}), 
            {'publication_date': str(timezone.now())})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse_lazy('swipe:announcement-list'))
        self.assertEqual(response.data['results'][0]['id'], self.announcement_cottege.pk)
        self.assertNotEqual(response.data['results'][0]['address'], 'test address')
