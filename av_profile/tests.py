from django.test import TestCase
from django.urls.base import reverse

from av_account.models import AvUser, Address
from av_core import settings


class ReturnsTestCase(TestCase):

    def setUp(self):
        self.user = AvUser.objects.create_user(
            email='test@example.com',
            password='password',
        )
        self.user.is_verified = True
        self.user.is_email_verified = True
        self.user.is_onboard = True
        self.user.is_paid = True
        self.user.phone = '(310) 666-3912'
        self.user.save()

    def login(self):
        self.client.login(
            username=self.user.email,
            password='password'
        )
        self.client.get(reverse('force_trust'))
    
    def test_identity(self):
        url = reverse('identity')

        data = {
            'first_name': 'Fred',
            'ssn': '123121234',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '{}?next={}'.format(settings.LOGIN_URL, url))

        self.login()
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        user = AvUser.objects.get(email=self.user.email)
        self.assertEqual(user.first_name, data['first_name'])
        self.assertEqual(user.ssn, data['ssn'])

    def test_zero_ssn(self):
        url = reverse('identity')
        self.login()

        data = {
            'ssn': '023121234',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        user = AvUser.objects.get(email=self.user.email)
        self.assertEqual(user.ssn, data['ssn'])

    def test_short_ssn(self):
        url = reverse('identity')
        self.login()

        data = {
            'ssn': '12345678',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')

    def test_long_ssn(self):
        url = reverse('identity')
        self.login()

        data = {
            'ssn': '1234567890',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')

    def test_address(self):
        url = reverse('address')
        
        address1 = '55 street'
        city = 'Boise'
        state = 'OH'
        zip_code = '12345'
        
        data = {
            'address1': address1,
            'city': city,
            'state': state,
            'zip': zip_code,
        }

        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '{}?next={}'.format(settings.LOGIN_URL, url))

        self.login()
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, url)
    
        address = Address.objects.get(user=self.user)
        self.assertEqual(address.address1, address1)
        self.assertEqual(address.city, city)
        self.assertEqual(address.state, state)
        self.assertEqual(address.zip, zip_code)
