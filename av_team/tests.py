import urllib

from django.contrib import auth
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from av_account.models import AvUser, Firm
from av_core import settings


class TeamTestCase(TestCase):
    def setUp(self):
        self.password = 'password'
        
        self.firm = Firm(
            name='acme'
        )
        self.firm.save()
        
        self.user = AvUser.objects.create_user(
            email='test@example.com',
            password=self.password,
        )
        self.user.firm = self.firm
        self.user.is_verified = True
        self.user.is_email_verified = True
        self.user.save()

        self.group = Group(name='admin')
        self.group.save()
        
        self.cpa = AvUser.objects.create_user(
            email='cpa@example.com',
            password=self.password,
            is_cpa=True,
        )
        self.cpa.firm = self.firm
        self.cpa.is_verified = True
        self.cpa.is_email_verified = True
        self.cpa.first_name = 'fred'
        self.cpa.last_name = 'smith'
        self.cpa.save()
        self.cpa.groups.add(self.group)
    
    def login_user(self):
        self.client.login(
            username=self.user.email,
            password=self.password
        )
        self.client.get(reverse('force_trust'))
        user = auth.get_user(self.client)
        assert user.is_authenticated()
    
    def login_cpa(self):
        self.client.login(
            username=self.cpa.email,
            password=self.password
        )
        self.client.get(reverse('force_trust'))
        user = auth.get_user(self.client)
        assert user.is_authenticated()
    
    def change_cpa_firm(self):
        firm = Firm(
            name='not acme'
        )
        firm.save()
        self.cpa.firm = firm
        self.cpa.save()
    
    def try_anonymous(self, url):
        # should redirect to login
        # note that Django url encodes the @ symbol in user email so we have to encode it here to match
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, '{}?next={}'.format(settings.LOGIN_URL, urllib.parse.quote(url)))
        
    def try_non_admin(self, url):
        # remove cpa from admin group
        self.cpa.groups.clear()
    
        # should redirect home
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('home'))

    def test_list_view(self):
        url = reverse('team')
        
        self.try_anonymous(url)
        self.login_cpa()
        
        # should get team member list
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.cpa.first_name)
        self.assertContains(response, self.cpa.last_name)
        self.assertContains(response, self.cpa.email)
        
    def test_non_admin_list_view(self):
        url = reverse('team')
        self.login_cpa()
        self.try_non_admin(url)

    def test_detail_view(self):
        url = reverse('team-detail', args=[self.cpa.email])
        
        self.try_anonymous(url)
        self.login_cpa()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.cpa.first_name)
        self.assertContains(response, self.cpa.last_name)
        
    def test_detail_change(self):
        url = reverse('team-detail', args=[self.cpa.email])
        data = {
            'last_name': 'x',
            'role': 1,
        }
        self.login_cpa()
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, url)

        cpa = AvUser.objects.get(email=self.cpa.email)
        self.assertEqual(cpa.last_name, data['last_name'])

    def test_non_admin_detail_view(self):
        url = reverse('team-detail', args=[self.cpa.email])
        self.login_cpa()
        self.try_non_admin(url)

    def test_invite(self):
        url = reverse('team-invite')
        data = {
            'email': 'a@a.com',
            'last_name': 'y',
            'role': 1,
        }
        
        self.try_anonymous(url)
        self.login_cpa()

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, url)

        cpa = AvUser.objects.get(email=data['email'])
        self.assertEqual(cpa.last_name, data['last_name'])

    def test_non_admin_invite(self):
        url = reverse('team-invite')
        self.login_cpa()
        self.try_non_admin(url)
