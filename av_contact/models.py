from django.db import models

from av_utils.utils import TimeStampedModel


class Contact(TimeStampedModel):
    name = models.CharField(blank=False, max_length=64)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=False)
    subject = models.CharField(blank=False, max_length=64)
    message = models.TextField(blank=False)

    def __str__(self):
        return self.email
