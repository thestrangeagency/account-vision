from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import Group
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from .models import AvUser, SecurityQuestion, UserSecurity, Firm


class AccountTestCase(TestCase):

    def setUp(self):
        self.password = 'aT%In<Yo'
        self.user = AvUser.objects.create_user(
            email='test@example.com',
            password=self.password,
        )
        # self.user.phone = '(310) 666-3912'
        self.user.save()

        self.firm = Firm(
            name='acme'
        )
        self.firm.stripe_id = 'bogus'
        self.firm.is_paid = False
        self.firm.trial_end = timezone.now() + timezone.timedelta(days=14)
        self.firm.save()
        
        self.cpa = AvUser.objects.create_user(
            email='cpa@example.com',
            password=self.password,
            is_cpa=True,
        )
        # self.cpa.phone = '(310) 666-3912'
        self.cpa.firm = self.firm
        self.cpa.save()

        self.question1 = SecurityQuestion(question="a?")
        self.question1.save()
        self.question2 = SecurityQuestion(question="b?")
        self.question2.save()
        self.question3 = SecurityQuestion(question="c?")
        self.question3.save()

        self.group = Group(name='admin')
        self.group.save()

    def login(self):
        self.client.login(
            username=self.user.email,
            password=self.password
        )
        self.client.get(reverse('force_trust'))
        
    def test_access(self):
        self.assertTrue(self.user.is_full_cred())
        self.assertTrue(self.cpa.is_full_cred())

    def test_expired_trial(self):
        with freeze_time(timezone.now() + timezone.timedelta(days=31)):
            self.assertTrue(self.user.is_full_cred())
            self.assertFalse(self.cpa.is_full_cred())

        # pay after expiration
        self.cpa.firm.is_paid = True
        self.assertTrue(self.cpa.is_full_cred())

    def test_register(self):
        mail.outbox = []

        url = reverse('register')
        user_email = 'test1@example.com'
        data = {
            'email': user_email,
            'password1': self.password,
            'password2': self.password,
        }

        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('firm'))
        
        user = auth.get_user(self.client)
        assert user.is_authenticated()

        # ensure new account email is sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], user_email)

        # ensure verification code works
        self.assertEqual(user.is_email_verified, False)
        code = user.email_verification_code
        url = reverse('confirmation', args=[code])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        user = AvUser.objects.get(email=user_email)
        self.assertEqual(user.is_email_verified, True)

    def test_firm(self):
        self.test_register()
        self.client.get(reverse('force_trust'))
        
        url = reverse('firm')
        data = {}

        # empty firm name
        
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('terms'))

        # firm name
        
        data = {
            'name': 'Damage Inc.'
        }

        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('terms'))

        user = auth.get_user(self.client)
        firm = user.firm

        self.assertEqual(firm.boss, user)
        self.assertEqual(firm.name, data['name'])

        # change firm name

        data = {
            'name': 'Inc. Corp. Ltd.'
        }

        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('terms'))

        user = auth.get_user(self.client)
        firm = user.firm

        self.assertEqual(firm.boss, user)
        self.assertEqual(firm.name, data['name'])
        
    def test_edit(self):
        self.user.is_verified = True
        self.user.is_email_verified = True
        self.user.save()

        mail.outbox = []
        self.login()

        url = reverse('edit')
        data = {
            'email': 'new@example.com'
        }

        response = self.client.post(url, data, follow=True)
        # target will redirect because now email needs verification
        self.assertRedirects(response, reverse('email_verify'))

        # ensure confirmation email was sent
        self.assertEqual(len(mail.outbox), 1)

        user = AvUser.objects.get(email=data['email'])

        # ensure verification code works
        self.assertEqual(user.is_email_verified, False)
        code = user.email_verification_code
        url = reverse('confirmation', args=[code])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        user = AvUser.objects.get(email=data['email'])
        self.assertEqual(user.is_email_verified, True)

    def test_edit_add_phone(self):
        self.user.is_verified = False
        self.user.is_2fa = False
        self.user.is_email_verified = True
        self.user.save()
        
        self.login()
    
        url = reverse('edit')
        data = {
            'email': self.user.email,
            'phone': '3106663912',
            'is2fa': False,
        }
    
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, url)

        user = AvUser.objects.get(email=self.user.email)
        self.assertEqual(user.phone, data['phone'])

    def test_edit_change_phone(self):
        self.test_edit_add_phone()
    
        url = reverse('edit')
        data = {
            'email': self.user.email,
            'phone': '1 (424) 243-6299‬',
            'is2fa': False,
        }
    
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, url)
    
        user = AvUser.objects.get(email=self.user.email)
        self.assertEqual(user.phone, data['phone'])

    def test_edit_add_phone_2fa(self):
        self.user.is_verified = False
        self.user.is_2fa = False
        self.user.is_email_verified = True
        self.user.save()
    
        self.login()
    
        url = reverse('edit')
        data = {
            'email': self.user.email,
            'phone': '3106663912',
            'is_2fa': True,
        }
    
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '{}?next={}'.format(settings.VERIFY_URL, url))
    
        user = AvUser.objects.get(email=self.user.email)
        self.assertEqual(user.phone, data['phone'])
        self.assertTrue(user.is_2fa)

    def test_edit_change_phone_then_2fa(self):
        self.user.is_verified = True
        self.user.save()
        
        # changing phone should set is_verified to false
        self.test_edit_change_phone()

        user = AvUser.objects.get(email=self.user.email)
        
        url = reverse('edit')
        data = {
            'email': user.email,
            'phone': user.phone,
            'is_2fa': True,
        }
    
        # turning on 2fa should now redirect to trust view because is_verified is now false
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '{}?next={}'.format(settings.VERIFY_URL, url))
    
        user = AvUser.objects.get(email=self.user.email)
        self.assertTrue(user.is_2fa)
        
        # submit code
        url = settings.VERIFY_URL
        data = {
            'verification_code': user.verification_code,
        }
        
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # can turn off 2fa

        url = reverse('edit')
        data = {
            'email': user.email,
            'phone': user.phone,
            'is_2fa': False,
        }

        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, url)
        
        # and on again

        data = {
            'email': user.email,
            'phone': user.phone,
            'is_2fa': True,
        }

        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, url)

    def test_edit_no_phone(self):
        self.user.is_verified = False
        self.user.is_2fa = False
        self.user.is_email_verified = True
        self.user.save()
    
        self.login()
    
        url = reverse('edit')
        data = {
            'email': self.user.email,
            'phone': '',
            'is_2fa': True,
        }
    
        response = self.client.post(url, data, follow=False)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'enter a valid phone number')
    
        user = AvUser.objects.get(email=self.user.email)
        
        # 2fa should not be enabled without a phone
        self.assertFalse(user.is_2fa)

    def test_2fa(self):
        self.user.is_verified = False
        self.user.is_2fa = False
        self.user.is_email_verified = True
        self.user.save()

        mail.outbox = []
        
        self.client.login(
            username=self.user.email,
            password=self.password
        )
    
        url = reverse('edit')

        # get edit page, note: haven't turned on agent trust on login
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '{}?next={}'.format(settings.VERIFY_URL, url))
        
        # verification code sent via email
        self.assertEqual(len(mail.outbox), 1)
        
        # turn on 2fa
        self.user.is_verified = True
        self.user.is_2fa = True
        self.user.phone = '3106663912'
        self.user.save()

        # still haven't turned on agent trust, so should redirect with 2fa now turned on
        response = self.client.get(url, follow=False)
        self.assertRedirects(response, '{}?next={}'.format(settings.VERIFY_URL, url))

        # verification code sent via phone this time, so outbox doesn't change
        self.assertEqual(len(mail.outbox), 1)

        # trust this client
        self.client.get(reverse('force_trust'))

        # force verify user
        self.user.is_verified = True
        self.user.save()

        # get edit page, should load now with 2fa and trust
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        url = reverse('login')
        data = {
            'username': self.user.email,
            'password': self.password,
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        # login will attempt to access returns, which in turn will redirect because of django-agent-trust
        # self.assertRedirects(response, settings.LOGIN_REDIRECT_URL)
        user = auth.get_user(self.client)
        assert user.is_authenticated()

    def test_logout(self):
        self.client.login(
            username=self.user.email,
            password=self.password
        )
        user = auth.get_user(self.client)
        assert user.is_authenticated()

        url = reverse('logout')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, settings.LOGOUT_REDIRECT_URL, fetch_redirect_response=False)
        user = auth.get_user(self.client)
        assert not user.is_authenticated()

    # def test_security_anonymous(self):
    #     url = reverse('questions')
    #     data = {}
    #
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, 302)
    #
    # def test_security(self):
    #     self.client.login(username=self.user.email, password=self.password)
    #     url = reverse('questions')
    #     data = {
    #         'question1': self.question1.id,
    #         'answer1': 'a',
    #         'question2': self.question2.id,
    #         'answer2': 'b',
    #         'question3': self.question3.id,
    #         'answer3': 'c',
    #     }
    #
    #     response = self.client.post(url, data)
    #
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, reverse('phone'))
    #
    #     # ensure answer saved
    #     us = UserSecurity.objects.get(user=self.user)
    #     self.assertTrue(us.test_answer(1, data['answer1']))
    #     self.assertFalse(us.test_answer(1, 'whatever'))
    #
    # def test_security_partial(self):
    #     self.client.login(username=self.user.email, password=self.password)
    #     url = reverse('questions')
    #
    #     data = {
    #         'question1': self.question1.id,
    #         'answer1': 'a',
    #         'question2': self.question2.id,
    #         'answer2': 'b',
    #         'question3': self.question3.id,
    #         'answer3': 'c',
    #     }
    #
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, 302)
    #
    #     data = {
    #         'question1': self.question1.id,
    #         'answer1': 'a',
    #         'question2': self.question2.id,
    #         'answer2': '••••',
    #         'question3': self.question3.id,
    #         'answer3': '••••••••',
    #     }
    #
    #     # ensure partial update ok
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, 302)
    #     us = UserSecurity.objects.get(user=self.user)
    #     self.assertTrue(us.test_answer(1, data['answer1']))
    #     self.assertFalse(us.test_answer(2, data['answer2']))
    #     self.assertTrue(us.test_answer(2, 'b'))
    #
    # def test_security_unique(self):
    #     self.client.login(username=self.user.email, password=self.password)
    #     url = reverse('questions')
    #     data = {
    #         'question1': self.question1.id,
    #         'answer1': 'a',
    #         'question2': self.question2.id,
    #         'answer2': 'b',
    #         'question3': self.question2.id,
    #         'answer3': 'c',
    #     }
    #
    #     self.client.post(url, data)
    #     self.assertRaises(ValidationError)
    #
    # def test_phone_empty(self):
    #     url = reverse('phone')
    #     data = {
    #     }
    #
    #     self.client.post(url, data)
    #     self.assertRaises(ValidationError)
    #
    # def test_phone_bad(self):
    #     url = reverse('phone')
    #     data = {
    #         'phone': '3',
    #     }
    #
    #     self.client.post(url, data)
    #     self.assertRaises(ValidationError)
    #
    # def test_phone(self):
    #     # have to answer security questions first or else will get redirected back to security page
    #     self.test_security()
    #     self.client.logout()
    #
    #     url = reverse('phone')
    #     data = {
    #         'phone': '3106663912',
    #     }
    #
    #     # try anonymous
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_302_FOUND)
    #     self.assertRedirects(response, '{}?next={}'.format(settings.LOGIN_URL, url))
    #
    #     self.client.login(username=self.user.email, password=self.password)
    #
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_302_FOUND)
    #     self.assertRedirects(response, reverse('verification'))
    #
    # def test_verification(self):
    #     self.user.verification_code = 'zzzz'
    #     self.user.save()
    #
    #     url = reverse('verification')
    #     data = {
    #         'verification_code': '1234',
    #     }
    #
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_302_FOUND)
    #     self.assertRedirects(response, '{}?next={}'.format(settings.LOGIN_URL, reverse('verification')))
    #
    #     self.client.login(username=self.user.email, password=self.password)
    #
    #     # incorrect code
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    #     # user not yet verified
    #     user = AvUser.objects.get(email=self.user.email)
    #     self.assertFalse(user.is_verified)
    #
    #     data = {
    #         'verification_code': user.verification_code,
    #     }
    #
    #     # correct code
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_302_FOUND)
    #     self.assertRedirects(response, reverse('client_created'), status_code=302, target_status_code=200)
    #
    #     # user verified
    #     user = AvUser.objects.get(email=self.user.email)
    #     self.assertTrue(user.is_verified)


class AccountAPITestCase(APITestCase):

    def setUp(self):
        self.password = 'aT%In<Yo'
        self.user = AvUser.objects.create_user(
            email='test@example.com',
            password=self.password,
        )
        self.user.save()

    def login(self):
        self.client.login(
            username=self.user.email,
            password=self.password
        )
        self.client.get(reverse('force_trust'))

    def test_create_account(self):
        """
        no one should be able to create a user
        """
        url = reverse('avuser-list')
        data = {
            'email': 'x@x.com',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.login()
        user = auth.get_user(self.client)
        assert user.is_authenticated()

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update(self):
        """
        logged in user should be able to update self
        """
        url = reverse('avuser-detail', args=[self.user.id])
        data = {
            'first_name': 'fred',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.login()
        user = auth.get_user(self.client)
        assert user.is_authenticated()

        response = self.client.patch(url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(AvUser.objects.get(email=user.email).first_name, data['first_name'])

        # removed user updates via api, so shouldn't be allowed
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_other(self):
        """
        no one should be able to update another user
        """
        user2 = AvUser.objects.create_user(
            email='x@x.com',
            password=self.password,
        )
        user2.save()

        url = reverse('avuser-detail', args=[user2.id])
        data = {
            'first_name': 'fred',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.login()
        user = auth.get_user(self.client)
        assert user.is_authenticated()

        response = self.client.patch(url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # removed user updates via api, so shouldn't be allowed
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_anonymous(self):
        """
        no one should be able to create a user
        """
        url = reverse('avuser-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_email(self):
        """
        user should not be able to update email
        """
        url = reverse('avuser-detail', args=[self.user.id])
        data = {
            'email': 'x@x.com',
        }

        self.login()

        response = self.client.patch(url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

        user = AvUser.objects.get(id=self.user.id)
        self.assertEqual(user.email, self.user.email)
        self.assertNotEqual(user.email, data['email'])

        # removed user updates via api, so shouldn't be allowed
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # def test_address(self):
    #     url = reverse('address-list')
    #     data = {
    #         'address1': 'a',
    #         'city': 'a',
    #         'state': 'a',
    #         'zip': 'a',
    #     }
    #
    #     # try anonymous post
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     self.client.login(username=self.user.email, password=self.password)
    #
    #     # try authenticated post
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     address = Address.objects.get()
    #     self.assertEqual(address.address1, data['address1'])
    #
    #     # change address
    #     url = reverse('address-detail', args=[address.id])
    #     data = {
    #         'address1': 'b',
    #     }
    #
    #     response = self.client.patch(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    #     address = Address.objects.get()
    #     self.assertEqual(address.address1, data['address1'])
