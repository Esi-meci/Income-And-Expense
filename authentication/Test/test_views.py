from .test_setup import TestSetUp
from ..models import User
class TestViews(TestSetUp):
    def test_registration_denail_when_invalid_data(self):
        res = self.client.post(self.register_url)
        self.assertEqual(res.status_code, 400)

    def test_registration_working(self):
        res = self.client.post(self.register_url, self.user_data, format='json')
        # import pdb
        # pdb.set_trace()
        self.assertEqual(res.data['email'], self.user_data['email'])
        self.assertEqual(res.data['username'], self.user_data['username'])
        self.assertEqual(res.status_code, 201)

    def test_login_denailed_for_unverified_email(self):
        self.client.post(self.register_url, self.user_data, format='json')
        res = self.client.post(self.login_url, self.user_data, format='json')
        self.assertEqual(res.status_code, 401)

    def test_login_successful_for_verified_email(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        email = response.data['email']
        user = User.objects.get(email = email)
        user.is_verified = True
        user.save()
        res = self.client.post(self.login_url, self.user_data, format='json')
        self.assertEqual(res.status_code, 200)