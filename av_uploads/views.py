import json
import uuid
from datetime import datetime
from urllib.parse import unquote

import os
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, \
    HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.views import View
from django.views.generic import TemplateView
from rest_framework import permissions, viewsets, serializers
from rest_framework.views import APIView

from av_account.models import AvUser
from av_account.utils import CPARequiredMixin, FullRequiredMixin
from av_returns.models import Return
from av_uploads.models import S3File
from .utils import get_aws_v4_signature, get_aws_v4_signing_key, get_s3direct_destinations, get_s3_url


class UploadParamsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        upload_data = {
            'object_key': '',
            'access_key_id': '',
            'region': '',
            'bucket': '',
            'bucket_url': '',
            'cache_control': '',
            'content_disposition': '',
            'acl': '',
            'server_side_encryption': '',
        }
        return HttpResponse(json.dumps(upload_data), content_type='application/json')

    def post(self, request):
        try:
            file_name = request.POST['file_name']
            file_type = request.POST['file_type']
            file_size = request.POST['file_size']
            destination = get_s3direct_destinations().get(request.POST['destination'])
            year = request.POST['year']
        except MultiValueDictKeyError:
            return HttpResponseBadRequest(json.dumps({'error': 'Missing params.'}), content_type='application/json')

        if not destination:
            return HttpResponseBadRequest(json.dumps({'error': 'File destination does not exist.'}), content_type='application/json')
        try:
            file_size = int(file_size)
        except ValueError:
            return HttpResponseBadRequest(json.dumps({'error': 'Bad params.'}), content_type='application/json')

        if 'target' in request.POST and request.user.is_cpa:
            try:
                file_target = AvUser.objects.get(id=request.POST['target'])
            except ObjectDoesNotExist:
                return HttpResponseNotFound(json.dumps({'error': 'User not found.'}),
                                            content_type='application/json')
        else:
            file_target = None

        # Validate request and destination config:
        allowed = destination.get('allowed')
        auth = destination.get('auth')
        key = destination.get('key')
        content_length_range = destination.get('content_length_range')

        if auth and not auth(request.user):
            return HttpResponseForbidden(json.dumps({'error': 'Permission denied.'}), content_type='application/json')

        if (allowed and file_type not in allowed) and allowed != '*':
            return HttpResponseBadRequest(json.dumps({'error': 'Invalid file type (%s).' % file_type}),
                                          content_type='application/json')

        if content_length_range and not content_length_range[0] <= file_size <= content_length_range[1]:
            return HttpResponseBadRequest(
                json.dumps({'error': 'Invalid file size (must be between %s and %s bytes).' % content_length_range}),
                content_type='application/json')

        # Generate object key
        if not key:
            return HttpResponseServerError(json.dumps({'error': 'Missing destination path.'}),
                                           content_type='application/json')
        file_id = uuid.uuid4().hex
        folder = str(request.user.id)
        path = os.path.join(folder, file_id)
        object_key = os.path.join(key, path)

        bucket = destination.get('bucket') or settings.AWS_BUCKET_NAME
        region = destination.get('region') or getattr(settings, 'AWS_REGION', None) or 'us-east-1'
        endpoint = 's3.amazonaws.com' if region == 'us-east-1' else ('s3-%s.amazonaws.com' % region)

        # AWS credentials are not required for publicly-writable buckets
        access_key_id = getattr(settings, 'AWS_ACCESS_KEY', None)

        bucket_url = 'https://{0}/{1}'.format(endpoint, bucket)

        upload_data = {
            'object_key': object_key,
            'access_key_id': access_key_id,
            'region': region,
            'bucket': bucket,
            'bucket_url': bucket_url,
            'cache_control': destination.get('cache_control'),
            'content_disposition': destination.get('content_disposition'),
            'acl': destination.get('acl') or 'public-read',
            'server_side_encryption': destination.get('server_side_encryption'),
        }

        if request.user.is_cpa:
            # cpa uploading a file for a user
            try:
                tax_return = Return.objects.get(user=file_target, year=year)
            except ObjectDoesNotExist:
                return HttpResponseNotFound(json.dumps({'error': 'No return found for given year.'}),
                                            content_type='application/json')
        else:
            # regular user uploading a file for review
            try:
                tax_return = Return.objects.get(user=request.user, year=year)
            except ObjectDoesNotExist:
                return HttpResponseNotFound(json.dumps({'error': 'No return found for given year.'}),
                                            content_type='application/json')

        file = S3File(
            user=request.user,
            target_user=file_target,
            tax_return=tax_return,
            name=file_name,
            type=file_type,
            size=file_size,
            s3_key=object_key,
            s3_bucket=bucket,
            s3_region=region,
        )

        file.save()

        return HttpResponse(json.dumps(upload_data), content_type='application/json')


class UploadSignatureView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            message = unquote(request.POST['to_sign'])
            signing_date = request.POST['datetime']
        except MultiValueDictKeyError:
            return HttpResponseBadRequest(json.dumps({'error': 'Missing params.'}), content_type='application/json')

        try:
            signing_date = datetime.strptime(signing_date, '%Y%m%dT%H%M%SZ')
        except ValueError:
            return HttpResponseBadRequest(json.dumps({'error': 'Bad params.'}), content_type='application/json')

        signing_key = get_aws_v4_signing_key(settings.AWS_SECRET_ACCESS_KEY, signing_date, settings.AWS_REGION, 's3')
        signature = get_aws_v4_signature(signing_key, message)
        return HttpResponse(signature)


class UploadCompleteView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            object_key = request.POST['object_key']
        except MultiValueDictKeyError:
            return HttpResponseBadRequest(json.dumps({'error': 'Missing params.'}), content_type='application/json')

        if not object_key:
            return HttpResponseNotFound(json.dumps({'error': 'No key provided.'}), content_type='application/json')
        try:
            file = S3File.objects.get(user=request.user, s3_key=object_key)
        except S3File.DoesNotExist:
            return HttpResponseNotFound(json.dumps({'error': 'Key error.'}), content_type='application/json')
        file.uploaded = True
        file.save()

        # removing this and relying instead on return state change notification
        # if file.target_user is not None:
        #     send_new_upload_email(file.target_user, file.tax_return.year)

        return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')


class FileSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField('make_url')
    s3_url = serializers.SerializerMethodField()

    def make_url(self, obj):
        kwargs = {
            'year': obj.tax_return.year,
            'pk': obj.id,
        }
        url = reverse('s3file-detail', kwargs=kwargs)
        return self.context['request'].build_absolute_uri(url)

    def get_s3_url(self, file):
        return get_s3_url(file)

    class Meta:
        model = S3File
        fields = '__all__'


class FileViewSet(viewsets.ModelViewSet):
    queryset = S3File.objects.all()
    serializer_class = FileSerializer
    permission_classes = (permissions.IsAuthenticated,)
    model = S3File
    http_method_names = ['get', 'patch', 'head', 'delete']

    def get_queryset(self):
        year = self.kwargs['year']
        return self.model.objects.filter(user=self.request.user, tax_return__year=year)

    def get_serializer_context(self):
        context = super(FileViewSet, self).get_serializer_context()
        context['year'] = self.kwargs['year']
        return context


class CpaFileViewSet(viewsets.ModelViewSet):
    queryset = S3File.objects.all()
    serializer_class = FileSerializer
    permission_classes = (permissions.IsAuthenticated,)
    model = S3File
    http_method_names = ['get', 'patch', 'head', 'delete']

    def get_queryset(self):
        year = self.kwargs['year']
        target = self.kwargs['target']
        return self.model.objects.filter(user=self.request.user, tax_return__year=year, target_user=target)

    def get_serializer_context(self):
        context = super(CpaFileViewSet, self).get_serializer_context()
        context['year'] = self.kwargs['year']
        context['target'] = self.kwargs['target']
        return context


class DownloadsViewSet(viewsets.ModelViewSet):
    queryset = S3File.objects.all()
    serializer_class = FileSerializer
    permission_classes = (permissions.IsAuthenticated,)
    model = S3File
    http_method_names = ['get', 'head']

    def get_queryset(self):
        year = self.kwargs['year']
        return self.model.objects.filter(tax_return__year=year, target_user=self.request.user)


class CpaUserView(CPARequiredMixin, TemplateView):
    template_name = 'uploads/cpa-user.html'

    def get_context_data(self, **kwargs):
        context = super(CpaUserView, self).get_context_data(**kwargs)
        context['users'] = AvUser.objects.exclude(groups__name='cpa')
        return context


class CpaReturnView(CPARequiredMixin, TemplateView):
    template_name = 'uploads/cpa-return.html'

    def get_context_data(self, **kwargs):
        context = super(CpaReturnView, self).get_context_data(**kwargs)
        target_id = kwargs.get('id', None)
        target = AvUser.objects.get(pk=target_id)
        context['target'] = target
        context['returns'] = Return.objects.filter(user=target)
        return context


class CpaUploadsView(CPARequiredMixin, TemplateView):
    template_name = 'uploads/cpa-uploads.html'

    def get_context_data(self, **kwargs):
        context = super(CpaUploadsView, self).get_context_data(**kwargs)
        target_id = kwargs.get('id', None)
        year = kwargs.get('year', None)
        target = AvUser.objects.get(pk=target_id)
        context['target'] = target
        context['year'] = year
        return context


class UploadUrlView(FullRequiredMixin, View):

    def get(self, request, id):
        file = get_object_or_404(S3File, id=id)
        if file.user == self.request.user or (self.request.user.is_cpa and file.user.firm == self.request.user.firm):
            url = get_s3_url(file)
            return HttpResponseRedirect(url)
        else:
            return HttpResponseForbidden()
