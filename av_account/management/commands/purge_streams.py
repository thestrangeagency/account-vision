from datetime import timedelta

import stripe
from actstream.models import Action
from django.core.management.base import BaseCommand
from django.utils import timezone

from av_core import settings


class Command(BaseCommand):
    help = 'Purges old actions'

    def handle(self, *args, **options):
        actions = Action.objects.filter(timestamp__lte=timezone.now() - timedelta(days=14))
        self.stdout.write('Found %s old actions.' % len(actions))

        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        count = 0
        for action in actions:
            action.delete()
            # action.timestamp = timezone.now() - timedelta(days=7)
            # action.save()
            count += 1
            print(action.id)

        self.stdout.write(self.style.SUCCESS('Deleted %s actions.' % count))
