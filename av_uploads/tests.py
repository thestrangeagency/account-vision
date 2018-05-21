from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from av_account.models import AvUser
from av_returns.models import Return
from av_uploads.models import S3File


class UploadAPITestCase(APITestCase):

    def setUp(self):
        self.user = AvUser.objects.create_user(
            email='test@example.com',
            password='password',
        )
        self.user.save()

        self.year = 1984
        self.my_return = Return(
            user=self.user,
            year=self.year,
        )
        self.my_return.save()

        self.group = Group(name='cpa')
        self.group.save()

        self.cpa = AvUser.objects.create_user(
            email='cpa@example.com',
            password='password',
        )
        self.cpa.groups.add(self.group)
        self.cpa.save()

    def test_params_protected(self):
        url = reverse('upload_params')

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_params_missing(self):
        url = reverse('upload_params')
        data = {
        }

        self.client.login(username=self.user.email, password='password')

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_params(self):
        url = reverse('upload_params')
        data = {
            'file_name': '',
            'file_type': '',
            'file_size': '',
            'destination': ''
        }

        self.client.login(username=self.user.email, password='password')

        response = self.client.post(url, data)
        self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND))

    def test_params(self):
        url = reverse('upload_params')
        data = {
            'file_name': 'x.txt',
            'file_type': 'txt',
            'file_size': '444',
            'destination': 'uploads',
            'year': self.my_return.year,
        }

        self.client.login(username=self.user.email, password='password')

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_signature_protected(self):
        url = reverse('upload_signature')

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_signature_missing(self):
        url = reverse('upload_signature')
        data = {
        }

        self.client.login(username=self.user.email, password='password')

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_signature(self):
        url = reverse('upload_signature')
        data = {
            'to_sign': '',
            'datetime': '',
        }

        self.client.login(username=self.user.email, password='password')

        response = self.client.post(url, data)
        self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND))

    def test_signature(self):
        url = reverse('upload_signature')
        data = {
            'to_sign': 'blah',
            'datetime': '20080903T205635Z',
        }

        self.client.login(username=self.user.email, password='password')

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_complete_protected(self):
        url = reverse('upload_complete')

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_complete_missing(self):
        url = reverse('upload_complete')
        data = {
        }

        self.client.login(username=self.user.email, password='password')

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_complete(self):
        url = reverse('upload_complete')
        data = {
            'object_key': '',
        }

        self.client.login(username=self.user.email, password='password')

        response = self.client.post(url, data)
        self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND))

    def test_complete(self):
        self.test_params()
        file = S3File.objects.first()

        self.assertEqual(file.uploaded, False)

        url = reverse('upload_complete')
        data = {
            'object_key': file.s3_key,
        }

        self.client.login(username=self.user.email, password='password')

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        file = S3File.objects.first()
        self.assertEqual(file.uploaded, True)

    def test_files_protected(self):
        url = reverse('s3file-list', args=[self.year])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_files(self):
        self.test_params()
        url = reverse('s3file-list', args=[self.year])

        self.client.login(username=self.user.email, password='password')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertContains(response, 'x.txt')

    def test_cpa_params(self):
        url = reverse('upload_params')
        data = {
            'file_name': 'cpa.txt',
            'file_type': 'txt',
            'file_size': '444',
            'destination': 'uploads',
            'year': self.my_return.year,
            'target': self.user.id,
        }

        self.client.login(username=self.cpa.email, password='password')

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cpa_files(self):
        self.test_cpa_params()
        self.client.login(username=self.user.email, password='password')

        url = reverse('s3file-list', args=[self.year])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(response, 'cpa.txt')

        url = reverse('download-list', args=[self.year])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'cpa.txt')

    def test_user_bad_target_params(self):
        # targeting another user by a user should just upload to own files
        url = reverse('upload_params')
        data = {
            'file_name': 'cpa.txt',
            'file_type': 'txt',
            'file_size': '444',
            'destination': 'uploads',
            'year': self.my_return.year,
            'target': self.cpa.id,
        }

        self.client.login(username=self.user.email, password='password')

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('s3file-list', args=[self.year])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'cpa.txt')

        url = reverse('download-list', args=[self.year])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(response, 'cpa.txt')

    def test_description(self):
        # user edits description
        self.test_params()
        data = {
            'description': 'blah',
        }

        self.client.login(username=self.user.email, password='password')

        file = S3File.objects.first()
        url = reverse('s3file-detail', args=[self.year, file.id])
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        file = S3File.objects.first()
        self.assertEqual(data['description'], file.description)

    def test_cpa_description(self):
        # cpa edits description
        self.test_cpa_params()
        data = {
            'description': 'blah',
        }

        self.client.login(username=self.cpa.email, password='password')

        file = S3File.objects.first()
        url = reverse('s3file-detail', args=[self.year, file.id])
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        file = S3File.objects.first()
        self.assertEqual(data['description'], file.description)
