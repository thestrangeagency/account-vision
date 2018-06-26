from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.utils import timezone

from account.models import TaxUser, Communications
from emails.utils import send_abandoned_email


class Command(BaseCommand):
    help = 'Emails abandoned registrations'

    def handle(self, *args, **options):
        # find users who registered but have not paid in 24 hrs
        users = TaxUser.objects.filter(is_paid=False, date_created__lt=timezone.now() + timedelta(-1))
        self.stdout.write('Found %s abandoned registrations.' % len(users))

        count = 0
        for user in users:
            # use Communications to keep track of previously sent reminders
            try:
                comms = Communications.objects.get(user=user)
            except ObjectDoesNotExist:
                comms = Communications.objects.create(user=user)

            self.stdout.write('%s reminders previously sent to user %s' % (comms.registration_reminders, user.id))

            if comms.registration_reminders == 0:
                # send reminder
                self.stdout.write('Sending reminder to %s' % user.id)
                send_abandoned_email(user)
                count = count + 1
                comms.registration_reminders = 1
                comms.save()

        self.stdout.write(self.style.SUCCESS('Sent %s reminders' % count))
