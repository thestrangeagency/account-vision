from django.contrib import auth
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse, reverse_lazy

from av_account.models import AvUser
from av_clients.views import UploadFileForm


class ImportTestCase(TestCase):

    def setUp(self):
        self.password = 'aT%In<Yo'
        self.user = AvUser.objects.create_user(
            email='test@example.com',
            password=self.password,
            is_cpa=True,
        )
        self.user.phone = '(310) 666-3912'
        self.user.is_verified = True
        self.user.is_email_verified = True
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
        file = open('av_clients/test_files/plain.csv', 'rb')
        file_dict = {'file': SimpleUploadedFile('whatever.csv', file.read())}
        form = UploadFileForm(files=file_dict)
        self.assertTrue(form.is_valid())

    def test_no_extension(self):
        self.login()

        file = open('av_clients/test_files/plain')

        response = self.client.post(reverse('import'), {'file': file})
        form = response.context['form']
        self.assertFalse(form.is_valid())

    def test_plain(self):
        self.login()

        file = open('av_clients/test_files/plain.csv')
        response = self.client.post(reverse('import'), {'file': file})
        form = response.context['form']
        self.assertTrue(form.is_valid())
        self.assertEquals(response.status_code, 200)

        response = self.client.post(reverse('import'))
        form = response.context['form']
        self.assertTrue(form.is_valid())
