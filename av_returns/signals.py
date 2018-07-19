from actstream import action
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from av_core import logger
from av_returns.models import Return, Dependent, Spouse, Expense


@receiver(post_save, sender=Return)
def return_post_save(sender, instance, created, *args, **kwargs):
    verb = 'updated'
    action.send(instance.user, verb=verb, target=instance)
    logger.info('action: {}, {}, {}'.format(instance.user, verb, instance))


@receiver(post_save, sender=Spouse)
def spouse_post_save(sender, instance, created, *args, **kwargs):
    verb = 'updated'
    action.send(instance.tax_return.user, verb=verb, target=instance)
    logger.info('action: {}, {}, {}'.format(instance.tax_return.user, verb, instance))


@receiver(post_save, sender=Dependent)
def dependent_post_save(sender, instance, created, *args, **kwargs):
    verb = 'updated'
    action.send(instance.tax_return.user, verb=verb, target=instance)
    logger.info('action: {}, {}, {}'.format(instance.tax_return.user, verb, instance))


@receiver(post_delete, sender=Dependent)
def dependent_post_delete(sender, instance, *args, **kwargs):
    verb = 'deleted a dependent'
    action.send(instance.tax_return.user, verb=verb, target=instance)
    logger.info('action: {}, {}, {}'.format(instance.tax_return.user, verb, instance))


@receiver(post_save, sender=Expense)
def expense_post_save(sender, instance, created, *args, **kwargs):
    verb = 'updated'
    action.send(instance.tax_return.user, verb=verb, target=instance)
    logger.info('action: {}, {}, {}'.format(instance.tax_return.user, verb, instance))
