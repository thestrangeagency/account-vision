from actstream import action
from django.db.models.signals import post_save
from django.dispatch import receiver

from av_uploads.models import S3File


@receiver(post_save, sender=S3File)
def return_post_save(sender, instance, created, *args, **kwargs):
    action.send(instance.user, verb='updated', target=instance)
