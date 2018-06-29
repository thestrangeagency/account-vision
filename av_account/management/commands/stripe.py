import datetime

import stripe
from django.core.management.base import BaseCommand

from av_account.models import Communications, Firm
from av_core import settings
from av_emails.utils import send_trial_end_email


class Command(BaseCommand):
    help = 'Synchronizes with Stripe'

    def handle(self, *args, **options):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # retrieve all plans at once for speed
        plans = stripe.Plan.list()

        # pluck out the plans we are interested in
        # default to a monthly plan, so as not to automatically charge for a whole year
        plan_a = next(x for x in plans.data if x.id == settings.STRIPE_PLANS['monthly']['a'])
        plan_b = next(x for x in plans.data if x.id == settings.STRIPE_PLANS['monthly']['b'])
        plan_c = next(x for x in plans.data if x.id == settings.STRIPE_PLANS['monthly']['c'])
        
        # grab all cpa accounts
        firms = Firm.objects.all()
        self.stdout.write('Found %s firms.' % len(firms))
        
        # iterate over all firms
        count = 0
        for firm in firms:
            
            # ensure firm has stripe id
            if firm.stripe_id:

                # grab customer object and ensure we do have a subscription
                customer = stripe.Customer.retrieve(firm.stripe_id)
                if customer is not None and customer.subscriptions.total_count > 0:
                
                    # get firm subscription
                    subscription = customer.subscriptions.data[0]
                    
                    # update trial end time
                    firm.trial_end = datetime.datetime.fromtimestamp(subscription.trial_end, datetime.timezone.utc)
                    firm.save()
                    count += 1
                    
                    # may need to email the boss
                    boss = firm.boss

                    # look up past communications to see if we've already emailed about an ending trial
                    comms, created = Communications.objects.get_or_create(user=boss)
                    
                    if firm.trial_days_left() <= 3 and comms.trial_end_reminders < 1:
                        # get usage counts
                        cpa_count = firm.cpa_count()
                        client_count = firm.client_count()
                        
                        # figure out candidate plan based on usage
                        plan = plan_a
                        if cpa_count > int(plan_a.metadata.max_cpa) or client_count > int(plan_a.metadata.max_client):
                            plan = plan_b
                            if cpa_count > int(plan_b.metadata.max_cpa) or client_count > int(plan_b.metadata.max_client):
                                plan = plan_c
                        plan.amount = round(plan.amount/100)
                        
                        send_trial_end_email(boss, plan.metadata.name, plan.amount)
                        
                        # record that email was sent
                        comms.trial_end_reminders = comms.trial_end_reminders + 1
                        comms.save()

        self.stdout.write(self.style.SUCCESS('Updated %s firms.' % count))
