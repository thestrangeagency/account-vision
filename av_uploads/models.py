from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.urls import reverse_lazy

from av_returns.models import Return
from av_utils.utils import TimeStampedModel
from .utils import delete_s3_object


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
    
    def url(self):
        return reverse_lazy('upload-url', args=[self.id])


@receiver(models.signals.post_delete, sender=S3File)
def s3file_post_delete(sender, instance, *args, **kwargs):
    delete_s3_object(instance)
