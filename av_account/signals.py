from actstream import action
from django.db.models.signals import post_save
from django.dispatch import receiver

from av_account.models import Address, Bank, AvUser


@receiver(post_save, sender=AvUser)
def user_post_save(sender, instance, created, *args, **kwargs):
    action.send(instance, verb='updated', target=instance)


@receiver(post_save, sender=Address)
def address_post_save(sender, instance, created, *args, **kwargs):
    action.send(instance.user, verb='updated', target=instance)


@receiver(post_save, sender=Bank)
def bank_post_save(sender, instance, created, *args, **kwargs):
    action.send(instance.user, verb='updated', target=instance)
