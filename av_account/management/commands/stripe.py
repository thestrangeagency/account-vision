import datetime

import stripe
from django.core.management.base import BaseCommand

from av_account.models import AvUser
from av_core import settings


class Command(BaseCommand):
    help = 'Synchronizes with Stripe'

    def handle(self, *args, **options):
        cpas = AvUser.objects.filter(is_cpa=True)
        self.stdout.write('Found %s CPA accounts.' % len(cpas))

        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        count = 0
        for cpa in cpas:
            if cpa.stripe_id:

                customer = stripe.Customer.retrieve(cpa.stripe_id)
                if customer is not None and customer.subscriptions.total_count > 0:
                
                    subscription = customer.subscriptions.data[0]
                    
                    cpa.trial_end = datetime.datetime.fromtimestamp(subscription.trial_end, datetime.timezone.utc)
                    cpa.save()
                    count += 1

        self.stdout.write(self.style.SUCCESS('Updated %s CPA accounts.' % count))
