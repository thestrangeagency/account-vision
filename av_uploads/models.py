from django.conf import settings
from django.db import models
from django.urls import reverse_lazy

from av_returns.models import Return
from av_utils.utils import TimeStampedModel


class S3File(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='target')
    tax_return = models.ForeignKey(Return)
    name = models.TextField()
    type = models.TextField()
    size = models.BigIntegerField(default=0)
    s3_key = models.TextField()
    s3_bucket = models.TextField()
    s3_region = models.TextField()
    description = models.TextField(blank=True)
    uploaded = models.BooleanField(default=False)
    
    def get_absolute_url(self):
        return reverse_lazy('upload-url', args=[self.id])

    def __str__(self):
        return self.name

    def get_stream_name(self):
        return 'file named {}'.format(self.__str__())

    def get_stream_url(self):
        return self.get_absolute_url()
