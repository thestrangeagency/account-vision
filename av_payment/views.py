import datetime

import stripe
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import TemplateView, FormView
from django.utils import timezone

from av_account.models import Communications, Firm, AvUser, Address
from av_account.utils import VerifiedAndTrustedRequiredMixin
from av_core import settings, logger
from av_payment.forms import TermsForm
from av_returns.models import Return, Expense, Spouse, Dependent


class TermsView(VerifiedAndTrustedRequiredMixin, FormView):
    template_name = 'av_payment/terms.html'
    form_class = TermsForm
    success_url = reverse_lazy('checkout')

    def dispatch(self, request, *args, **kwargs):
        """
        continue to next step if user has already agreed
        """
        user = request.user
        if user.is_authenticated:
            try:
                comms = Communications.objects.get(user=self.request.user)
                if comms.agreed_terms:
                    return redirect(self.success_url)
            except ObjectDoesNotExist:
                pass
        return super(TermsView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        comms, created = Communications.objects.get_or_create(user=self.request.user)
        comms.agreed_terms = timezone.now()
        comms.save()
        self.request.session['coupon'] = form.get_coupon()
        self.request.session['code'] = form.cleaned_data.get('code')
        return super(TermsView, self).form_valid(form)


class CheckoutView(VerifiedAndTrustedRequiredMixin, TemplateView):
    template_name = 'av_payment/checkout.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            Communications.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return redirect(reverse('terms'))
        if self.request.user.firm.stripe_id is not None:
            return redirect(reverse('home'))
        return super(CheckoutView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # create a customer
        try:
            customer = stripe.Customer.create(
                email=request.user.email,
                source=request.POST.get('source')
            )

        except stripe.error.StripeError as e:
            logger.error('Stripe customer creation error: %s', e)
            return redirect(reverse('error'))

        # log any funny business like an existing subscription
        if customer.subscriptions.total_count != 0:
            logger.error('Creating a customer %s that already has a subscription!', customer.id)

        # check coupon
        if not self.request.session['coupon']:
            self.request.session['coupon'] = None

        # subscribe customer to default plan
        try:
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'plan': settings.STRIPE_DEFAULT_PLAN}],
                trial_from_plan=True,
                coupon=self.request.session['coupon'],
            )

        except stripe.error.StripeError as e:
            logger.error('Stripe subscription error: %s', e)
            return redirect(reverse('error'))

        # if all went well, store results and redirect to ready page
        if subscription is not None:
            firm = self.request.user.firm
            firm.boss = self.request.user
            firm.stripe_id = customer.id
            firm.is_paid = True
            firm.trial_end = datetime.datetime.fromtimestamp(subscription.trial_end, datetime.timezone.utc)
            firm.save()
            self.create_example_client(self.request.user)
            return redirect(reverse('ready'))
        else:
            return redirect(reverse('error'))

    def create_example_client(self, user):
        random = get_random_string(16)
        client = AvUser.objects.create_user(
            email='{}@example.com'.format(random),
            password=random,
        )
        client.is_verified = True
        client.is_2fa = False
        client.is_email_verified = True
        client.firm = user.firm

        client.is_active = True
        client.is_staff = False
        client.is_cpa = False

        client.first_name = 'Client'
        client.last_name = 'Example'
        client.middle_name = 'X'
        client.dob = datetime.datetime.now() - datetime.timedelta(days=30 * 365)
        client.ssn = '000000000'
        client.phone = '3105550101'

        address = Address.objects.create(user=client)
        address.address1 = '808 SW Main St'
        address.address2 = ''
        address.city = 'Portland'
        address.state = 'OR'
        address.zip = '97204'
        address.save()

        client.save()

        a_return = Return(
            user=client,
            year=datetime.datetime.now().year,
        )
        a_return.filing_status = Return.MARRIED_JOINT
        a_return.save()

        expense = Expense(
            tax_return=a_return,
            type='Travel',
            amount='2000.88',
            notes='Paris trip'
        )
        expense.save()

        expense = Expense(
            tax_return=a_return,
            type='Office Supplies',
            amount='300',
            notes='Golden stapler'
        )
        expense.save()

        spouse = Spouse(
            tax_return=a_return,
        )
        spouse.first_name = 'Spouse'
        spouse.last_name = 'Example'
        spouse.middle_name = 'E'
        spouse.dob = datetime.datetime.now() - datetime.timedelta(days=28 * 365)
        spouse.ssn = '000000001'
        spouse.save()

        kid = Dependent(
            tax_return=a_return,
        )
        kid.relationship = Dependent.DAUGHTER
        kid.first_name = 'Daughter'
        kid.last_name = 'Example'
        kid.dob = datetime.datetime.now() - datetime.timedelta(days=8 * 365)
        kid.ssn = '000000002'
        kid.save()

    def get_context_data(self, **kwargs):
        context = super(CheckoutView, self).get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLIC_KEY
        context['code'] = self.request.session['code']
        return context
