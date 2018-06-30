import urllib

from django.contrib import auth
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from av_account.models import AvUser, Firm
from av_clients.views import UploadFileForm
from av_core import settings
from av_returns.models import Return, Expense
from av_uploads.models import S3File


class ImportTestCase(TestCase):

    def setUp(self):
        self.password = 'aT%In<Yo'

        self.firm = Firm(
            name='acme'
        )
        self.firm.stripe_id = 'bogus'
        self.firm.is_paid = True
        self.firm.save()
        
        self.user = AvUser.objects.create_user(
            email='test@example.com',
            password=self.password,
            is_cpa=True,
        )
        self.user.phone = '(310) 666-3912'
        self.user.is_verified = True
        self.user.is_email_verified = True
        self.user.firm = self.firm
        self.user.save()

    def login(self):
        self.client.login(
            username=self.user.email,
            password=self.password
        )
        self.client.get(reverse('force_trust'))
        user = auth.get_user(self.client)
        assert user.is_authenticated()

    def test_form_bad_extension(self):
        file = open('av_clients/test_files/plain')
        data = {'file', file}
        form = UploadFileForm(data)
        self.assertFalse(form.is_valid())

    def test_form_ok(self):
        file = open('av_clients/test_files/ok.csv', 'rb')
        file_dict = {'file': SimpleUploadedFile('whatever.csv', file.read())}
        form = UploadFileForm(files=file_dict)
        self.assertTrue(form.is_valid())

    def test_no_extension(self):
        self.login()

        file = open('av_clients/test_files/plain')

        response = self.client.post(reverse('import'), {'file': file})
        form = response.context['form']
        self.assertFalse(form.is_valid())

    def test_ok(self):
        self.login()
        mail.outbox = []

        file = open('av_clients/test_files/ok.csv')
        response = self.client.post(reverse('import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('preview'))
        # self.user already exists in db
        self.assertContains(response, 'imported', count=1)

        response = self.client.post(reverse('preview'), follow=True)
        self.assertRedirects(response, reverse('import'))
        # sent to 2 out of 3 users
        self.assertContains(response, 'sent to 2')

        # ensure new user in db
        user = AvUser.objects.get(email='fred@a.com')
        self.assertTrue(user.email_verification_code)

        # ensure invitation emails were sent
        self.assertEqual(len(mail.outbox), 2)

    def test_bad_order(self):
        self.login()

        file = open('av_clients/test_files/bad_order.csv')
        response = self.client.post(reverse('import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('preview'))
        self.assertContains(response, 'Incorrect format')

        response = self.client.post(reverse('preview'), follow=True)
        self.assertRedirects(response, reverse('import'))

        self.assertContains(response, 'sent to 0')

    def test_bad_delimiter(self):
        self.login()

        file = open('av_clients/test_files/bad_delimiter.csv')
        response = self.client.post(reverse('import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('preview'))
        self.assertContains(response, 'Nothing')

        response = self.client.post(reverse('preview'), follow=True)
        self.assertRedirects(response, reverse('import'))

        self.assertContains(response, 'sent to 0')

    def test_unicode(self):
        self.login()
        mail.outbox = []

        file = open('av_clients/test_files/unicode.csv')
        response = self.client.post(reverse('import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('preview'))

        response = self.client.post(reverse('preview'), follow=True)
        self.assertRedirects(response, reverse('import'))
        # sent to 2 users
        self.assertContains(response, 'sent to 2')

        # ensure invitation emails were sent
        self.assertEqual(len(mail.outbox), 2)

    def test_quotes(self):
        self.login()
        mail.outbox = []

        file = open('av_clients/test_files/quoted.csv')
        response = self.client.post(reverse('import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('preview'))
        # two rows contain incorrect quotes
        self.assertContains(response, 'format', count=2)

        response = self.client.post(reverse('preview'), follow=True)
        self.assertRedirects(response, reverse('import'))
        # sent to 1 user
        self.assertContains(response, 'sent to 1')

        # ensure invitation emails were sent
        self.assertEqual(len(mail.outbox), 1)

    def test_dupes(self):
        self.login()
        mail.outbox = []

        file = open('av_clients/test_files/dupes.csv')
        response = self.client.post(reverse('import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('preview'))
        # self.user already exists in db
        self.assertContains(response, 'Duplicate', count=2)

        response = self.client.post(reverse('preview'), follow=True)
        self.assertRedirects(response, reverse('import'))
        # sent to 1 out of 3 users
        self.assertContains(response, 'sent to 1')

        # ensure new user in db
        user = AvUser.objects.get(email='fred@a.com')
        self.assertTrue(user.email_verification_code)

        # ensure invitation emails were sent
        self.assertEqual(len(mail.outbox), 1)


class ClientsTestCase(TestCase):
    
    def setUp(self):
        self.password = 'password'
        
        self.firm = Firm(
            name='acme'
        )
        self.firm.stripe_id = 'bogus'
        self.firm.is_paid = True
        self.firm.save()
        
        self.user = AvUser.objects.create_user(
            email='test@example.com',
            password=self.password,
        )
        self.user.firm = self.firm
        self.user.is_verified = True
        self.user.is_email_verified = True
        self.user.save()
    
        self.year = 1984
        self.my_return = Return(
            user=self.user,
            year=self.year,
        )
        self.my_return.save()
        
        self.expense = Expense(
            tax_return=self.my_return,
            type='food',
            amount='6.66',
            notes='eat'
        )
        self.expense.save()
    
        self.cpa = AvUser.objects.create_user(
            email='cpa@example.com',
            password=self.password,
            is_cpa=True,
        )
        self.cpa.firm = self.firm
        self.cpa.is_verified = True
        self.cpa.is_email_verified = True
        self.cpa.trial_end = timezone.now() + timezone.timedelta(days=14)
        self.cpa.save()

        self.file = S3File(
            user=self.user,
            name='x.txt',
            type='txt',
            size='444',
            tax_return=self.my_return,
        )
        self.file.save()

    def login(self):
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
        firm.stripe_id = 'bogus'
        firm.is_paid = True
        firm.save()
        self.cpa.firm = firm
        self.cpa.save()

    def test_file_url_access(self):
        url = reverse('upload-url', args=[self.file.id])
        # should redirect to login
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, '{}?next={}'.format(settings.LOGIN_URL, url))

        # attempt to get own file
        self.login()
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # another's file
        file = S3File(
            user=self.cpa,
            name='x.txt',
            type='txt',
            size='444',
            tax_return=self.my_return,
        )
        file.save()

        url = reverse('upload-url', args=[file.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cpa_file_url_access(self):
        self.login_cpa()
        
        url = reverse('upload-url', args=[self.file.id])
        
        # client is in CPA's firm
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.change_cpa_firm()

        # client is not in CPA's firm
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_expense_view(self):
        url = reverse('client-detail-return-expenses', args=[self.user.email, self.my_return.year])

        # should redirect to login
        # note that Django url encodes the @ symbol in user email so we have to encode it here to match
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, '{}?next={}'.format(settings.LOGIN_URL, urllib.parse.quote(url)))

        self.login_cpa()

        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.expense.type)
        self.assertContains(response, self.expense.amount)
        self.assertContains(response, self.expense.notes)

        self.change_cpa_firm()

        # client is not in CPA's firm
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
