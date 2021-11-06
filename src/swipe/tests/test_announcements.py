import random

from django.urls import reverse_lazy
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

from swipe.models import Announcement, AnnouncementImage, ClientAnnouncementFavourites, Flat, House
from users.models import User, Developer


class TestAnnouncementViewSetAPI(APITestCase):
    """ Test module for houses API """

    faker = Faker()

    def create_client(self, black_list: tuple=tuple()) -> tuple[User, str]:
        '''create test client'''
        phone_numbers = ['+38(093)134-02-39', '+38(093)135-02-39', '+38(093)136-02-39', '+38(096)123-32-54', '+38(067)682-48-94']
        for phone_number in black_list:
            phone_numbers.remove(phone_number)
        user_data = {'phone_number': random.choice(phone_numbers), 
            'email': self.faker.email(), 'password': self.faker.name()}
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

    def test_unauthorized_user_can_not_add_announcement(self):
        res = self.client.post('/swipe/api/announcements/', {
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
            "price": random.randint(14000, 45000)
        })
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_client_can_add_cottege_in_announcement(self):
        u = self.client_authenticate()
        res = self.client.post('/swipe/api/announcements/', {
            "address": self.faker.name(),
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
            "advertiser": u.client.pk,
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_client_can_not_request_adding_flat_to_house(self):
        '''Client can not request cause validation error'''
        u = self.client_authenticate()

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

        res = self.client.post('/swipe/api/flats/', {
            "housing": 3,
            "section": 10,
            "floor": 50,
            "number": 2,
            "house": house.pk
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_client_can_request_adding_flat_to_house(self):
        u = self.client_authenticate()

        house = House.objects.create(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=3, floors=13
        )

        res = self.client.post('/swipe/api/flats/', {
            "housing": 1,
            "section": 2,
            "floor": 2,
            "number": 12,
            "house": house.pk
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_client_can_not_update_flat_status(self):
        u = self.client_authenticate()
        
        house = House.objects.create(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=3, floors=13
        )

        self.client.post('/swipe/api/flats/', {
            "housing": 1,
            "section": 2,
            "floor": 2,
            "number": 12,
            "house": house.pk
        })

        res = self.client.put('/swipe/api/flats/', {
            "housing": 1,
            "section": 2,
            "floor": 2,
            "number": 12,
            'status': True,
            "house": house.pk
        })
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        res = self.client.patch('/swipe/api/flats/', {'status': True})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_developer_can_update_flat_status(self):
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
            housings=2, sections=3, floors=13
        ))

        self.client.post('/swipe/api/flats/', {
            "housing": 1,
            "section": 2,
            "floor": 2,
            "number": 12,
            "house": House.objects.last().pk
        })

        flat_pk = Flat.objects.last().pk
        res = self.client.put(f'/swipe/api/flats/{flat_pk}/', {
            "housing": 1,
            "section": 2,
            "floor": 2,
            "number": 12,
            'status': True,
            "house": House.objects.last().pk
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.patch(f'/swipe/api/flats/{flat_pk}/', {'status': True})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_client_can_add_announcement_with_flat(self):
        u = self.client_authenticate()

        house = House.objects.create(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=3, floors=13
        )

        flat = Flat.objects.create(**{
            "housing": 1,
            "section": 2,
            "floor": 2,
            "number": 12,
            "house": house,
            'status': True
        })

        res = self.client.post('/swipe/api/announcements/', {
            "address": self.faker.name(),
            'flat': flat.pk,
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
            "advertiser": u.client.pk,
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        announcement: Announcement = Announcement.objects.last()
        self.assertEqual(announcement.moder_status, '1')

    def client_can_not_get_access_for_admin_announcements_api(self):
        self.client_authenticate()
        response = self.client.get('/swipe/api/announcements_admin/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def developer_can_not_get_access_for_admin_announcements_api(self):
        self.developer_authenticate()
        response = self.client.get('/swipe/api/announcements_admin/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def admin_can_get_access_for_admin_announcements_api(self):
        self.admin_authenticate()
        response = self.client.get('/swipe/api/announcements_admin/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def admin_can_change_moder_status_and_delete_announcement(self):
        u = self.admin_authenticate()
        house = House.objects.create(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=3, floors=13
        )

        flat = Flat.objects.create(**{
            "housing": 1,
            "section": 2,
            "floor": 2,
            "number": 12,
            "house": house,
            'status': True
        })

        self.client.post('/swipe/api/announcements/', {
            "address": self.faker.name(),
            'flat': flat.pk,
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
            "advertiser": u.client.pk,
        })

        announcement_pk = Announcement.objects.last().pk

        response = self.client.patch(f'/swipe/api/announcements_admin/{announcement_pk}', {
            'moder_status': 2
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Announcement.objects.last().moder_status, '2')

        response = self.client.delete(f'/swipe/api/announcements_admin/{announcement_pk}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_client_can_not_update_someone_elses_announcement(self):
        u = self.client_authenticate()

        another_client = self.create_client((u.phone_number,))

        house = House.objects.create(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=3, floors=13
        )

        flat = Flat.objects.create(**{
            "housing": 1,
            "section": 2,
            "floor": 2,
            "number": 12,
            "house": house,
            'status': True
        })

        self.client.post('/swipe/api/announcements/', {
            "address": self.faker.name(),
            'flat': flat.pk,
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
            "advertiser": another_client[0].client.pk,
        })

        response = self.client.patch(f'/swipe/api/announcements/{Announcement.objects.last().pk}/', {
            "foundation_document": "2"
        })

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_client_can_update_own_announcement(self):
        u = self.client_authenticate()
        house = House.objects.create(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=3, floors=13
        )

        flat = Flat.objects.create(**{
            "housing": 1,
            "section": 2,
            "floor": 2,
            "number": 12,
            "house": house,
            'status': True
        })

        self.client.post('/swipe/api/announcements/', {
            "address": self.faker.name(),
            'flat': flat.pk,
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
            "advertiser": u.client.pk,
        })

        response = self.client.patch(f'/swipe/api/announcements/{Announcement.objects.last().pk}/', {
            "foundation_document": "2"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_client_can_add_announcement_to_favourites_and_delete_it(self):
        u = self.client_authenticate()
        another_client = self.create_client((u.phone_number,))
        house = House.objects.create(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=3, floors=13
        )

        flat = Flat.objects.create(**{
            "housing": 1,
            "section": 2,
            "floor": 2,
            "number": 12,
            "house": house,
            'status': True
        })

        self.client.post('/swipe/api/announcements/', {
            "address": self.faker.name(),
            'flat': flat.pk,
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
            "advertiser": another_client[0].client.pk,
        })

        announcement_pk = Announcement.objects.last().pk
        
        response = self.client.post(reverse_lazy('swipe:announcement_favourites-create', 
            kwargs={'announcement_id': announcement_pk}), {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.delete(reverse_lazy('swipe:announcement_favourites-destroy',
            kwargs={'announcement_id': announcement_pk}), {})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_client_can_update_his_promotion(self):
        u = self.client_authenticate()
        house = House.objects.create(
            name=self.faker.name(),
            description=self.faker.address(),
            status='2', type='1', 
            _class='2', building_technology='1', territory='2',
            sea_distance=1000.1, communal_payments='1', ceiling_height=2.78,
            has_gas='2', heating_type='1', sewerage='1', water_supply='1',
            calculation_type='Ипотека', perpose='Жилое помещение',
            summ_in_contract='Неполная', coords='46.43352126727788, 30.721379643314993',
            housings=2, sections=3, floors=13
        )

        flat = Flat.objects.create(**{
            "housing": 1,
            "section": 2,
            "floor": 2,
            "number": 12,
            "house": house,
            'status': True
        })

        self.client.post('/swipe/api/announcements/', {
            "address": self.faker.name(),
            'flat': flat.pk,
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
            "advertiser": u.client.pk,
        })
        announcement_pk = Announcement.objects.last().pk

        res = self.client.patch(f'/swipe/api/promotions/{announcement_pk}/', {
            'phrase': 1,
            'color': 1,
            'is_turbo': True
        })

        self.assertEqual(res.status_code, status.HTTP_200_OK)
