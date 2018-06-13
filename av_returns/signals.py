from actstream import action
from django.db.models.signals import post_save
from django.dispatch import receiver

from av_returns.models import Return, Dependent, Spouse, Expense


@receiver(post_save, sender=Return)
def return_post_save(sender, instance, created, *args, **kwargs):
    action.send(instance.user, verb='updated', target=instance)


@receiver(post_save, sender=Spouse)
def spouse_post_save(sender, instance, created, *args, **kwargs):
    action.send(instance.tax_return.user, verb='updated', target=instance)


@receiver(post_save, sender=Dependent)
def dependent_post_save(sender, instance, created, *args, **kwargs):
    action.send(instance.tax_return.user, verb='updated', target=instance)


@receiver(post_save, sender=Expense)
def expense_post_save(sender, instance, created, *args, **kwargs):
    action.send(instance.tax_return.user, verb='updated', target=instance)
