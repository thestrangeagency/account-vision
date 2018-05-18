import string

from secrets import choice

from django.contrib.auth import hashers
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.signals import user_logged_in
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from ipware.ip import get_ip
from phonenumber_field.modelfields import PhoneNumberField
from twilio.rest import Client

from av_emails.utils import send_verification_email
from av_core import logger
from av_core import settings
from av_utils.utils import TimeStampedModel


class Person(TimeStampedModel):
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    middle_name = models.CharField(_('middle name'), max_length=150, blank=True)
    dob = models.DateField(null=True, blank=True)
    ssn = models.CharField(
        validators=[RegexValidator(regex='^\d{9}$', message='SSN should be 9 digits.', code='bad_ssn')],
        max_length=9,
        blank=True,
    )

    class Meta:
        abstract = True


class AvUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class AvUser(Person, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    phone = PhoneNumberField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_cpa = models.BooleanField(default=False)

    # 2FA via SMS
    verification_code = models.CharField(max_length=4, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    # email
    is_email_verified = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=16, null=True, blank=True)
    previous_email = models.EmailField(verbose_name='previous email address', max_length=255, null=True, blank=True)

    objects = AvUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        # The user is identified by their email address
        full_name = '%s %s %s' % (self.first_name, self.last_name, self.email)
        return full_name.strip()

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def send_verification_code(self):
        if self.phone is None or self.phone is '':
            logger.error('Attempted to send verification without a phone number')
            return

        # create verification code
        self.verification_code = ''.join([choice(string.ascii_uppercase + string.digits) for _ in range(4)])
        self.is_verified = False
        self.save()

        # send sms
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        from_number = settings.TWILIO_FROM_NUMBER

        client = Client(account_sid, auth_token)

        client.messages.create(
            to="+{}{}".format(self.phone.country_code, self.phone.national_number),
            from_=from_number,
            body="Your Account Vision verification code is: " + self.verification_code
        )

    def send_email_verification_code(self):
        self.email_verification_code = ''.join([choice(string.ascii_uppercase + string.digits) for _ in range(16)])
        self.is_email_verified = False
        self.save()
        send_verification_email(self)

    def __str__(self):
        return self.email


class Address(models.Model):
    user = models.OneToOneField(AvUser, on_delete=models.CASCADE)
    address1 = models.CharField("Address line 1", max_length=1024)
    address2 = models.CharField("Address line 2", max_length=1024, blank=True)
    city = models.CharField("City", max_length=1024)
    state = models.CharField("State", max_length=2)
    zip = models.CharField("ZIP / Postal code", max_length=10)


class SecurityQuestion(models.Model):
    question = models.CharField(max_length=128)

    def __str__(self):
        return self.question


# more easily restrict question/answer count and partial updates by codifying in a model
class UserSecurity(TimeStampedModel):
    user = models.OneToOneField(AvUser, on_delete=models.CASCADE)

    question1 = models.ForeignKey(SecurityQuestion, on_delete=models.CASCADE, related_name='question1')
    question2 = models.ForeignKey(SecurityQuestion, on_delete=models.CASCADE, related_name='question2')

    answer1 = models.CharField(max_length=128)
    answer2 = models.CharField(max_length=128)

    def set_answer(self, index, answer):
        if 1 <= index <= 2:
            setattr(self, 'answer{}'.format(index), hashers.make_password(answer.upper()))
        else:
            raise IndexError('Answer out of range')

    def test_answer(self, index, answer):
        if 1 <= index <= 2:
            return hashers.check_password(answer.upper(), getattr(self, 'answer{}'.format(index)))
        else:
            return False


class UserLogin(models.Model):
    """User login history"""
    user = models.ForeignKey(AvUser)
    ip = models.CharField(max_length=64, null=True)
    date_created = models.DateTimeField(_('date created'), default=timezone.now)


def update_user_login(sender, request, user, **kwargs):
    UserLogin.objects.create(user=user, ip=get_ip(request))


user_logged_in.connect(update_user_login)


class Communications(models.Model):
    user = models.OneToOneField(AvUser, on_delete=models.CASCADE)
    registration_reminders = models.IntegerField(default=0)


class Bank(models.Model):
    user = models.OneToOneField(AvUser, on_delete=models.CASCADE)
    routing = models.CharField("Routing number", max_length=9, blank=False, null=True, help_text="9 digits")
    account = models.CharField("Account number", max_length=16, blank=False, null=True, help_text="Usually 10 to 12 digits")