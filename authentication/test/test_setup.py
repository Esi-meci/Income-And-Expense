from rest_framework.test import APITestCase
from django.urls import reverse
from faker import Faker
fake = Faker()

class TestSetUp(APITestCase):

    def setUp(self):
        self.register_url = reverse('registers')
        self.login_url = reverse('Login')
        
        self.user_data={
            'email':    fake.email(),
            'username': fake.email().split('@')[0],
            'password': fake.email(),
        }
        return super().setUp()

    def tearDown(self):
        return super().tearDown()