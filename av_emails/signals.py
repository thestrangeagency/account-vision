from django.db import models
from django.dispatch import receiver
from django_messages.models import Message

from av_account.models import AvUser
from av_contact.models import Contact
from av_emails.utils import send_new_message_email, send_new_user_email, send_new_contact_email


@receiver(models.signals.post_save, sender=Message)
def message_post_save(sender, instance, created, *args, **kwargs):
    if created:
        send_new_message_email(instance)


@receiver(models.signals.post_save, sender=AvUser)
def user_post_save(sender, instance, created, *args, **kwargs):
    if created:
        # only send new user email to a cpa that has just registered, but not another CPA that was invited to his team
        if instance.is_cpa and instance.firm is None:
            send_new_user_email(instance)


@receiver(models.signals.post_save, sender=Contact)
def return_post_save(sender, instance, created, *args, **kwargs):
    if created:
        send_new_contact_email(instance)