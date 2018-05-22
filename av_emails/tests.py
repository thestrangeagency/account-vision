from django.core import mail
from django.test import TestCase
from django_messages.models import Message

from av_account.models import AvUser
from av_returns.models import Return


class EmailTest(TestCase):

    def setUp(self):
        self.user = AvUser.objects.create_user(
            email='test@example.com',
            password='password',
        )
        self.user.save()

        self.cpa = AvUser.objects.create_user(
            email='cpa@example.com',
            password='password',
        )
        self.cpa.save()

        self.year = 1984
        self.my_return = Return(
            user=self.user,
            year=self.year,
        )
        self.my_return.save()

    # new user emails have been disabled
    # def test_new_user(self):
    #     self.assertEqual(len(mail.outbox), 2)
    #     self.assertEqual(mail.outbox[0].to[0], self.user.email)
    #     self.assertEqual(mail.outbox[1].to[0], self.cpa.email)

    # def test_new_message(self):
    #     mail.outbox = []
    #
    #     Message.objects.create(sender=self.user, recipient=self.cpa)
    #
    #     self.assertEqual(len(mail.outbox), 1)
    #     self.assertEqual(mail.outbox[0].to[0], self.cpa.email)
    #
    # def test_return_update(self):
    #     mail.outbox = []
    #
    #     self.my_return.is_first_time = True
    #     self.my_return.save()
    #     self.assertEqual(len(mail.outbox), 0)
    #
    #     self.my_return.return_status = Return.REVIEW
    #     self.my_return.is_first_time = False
    #     self.my_return.save()
    #     self.assertEqual(len(mail.outbox), 1)
    #     self.assertEqual(mail.outbox[0].to[0], self.cpa.email)
