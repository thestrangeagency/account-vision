from actstream import action
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from av_uploads.models import S3File
from av_uploads.utils import delete_s3_object


@receiver(post_save, sender=S3File)
def s3file_post_save(sender, instance, created, *args, **kwargs):
    action.send(instance.user, verb='updated', target=instance)


@receiver(post_delete, sender=S3File)
def s3file_post_delete(sender, instance, *args, **kwargs):
    delete_s3_object(instance)