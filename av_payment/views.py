import datetime

import stripe
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, FormView
from django.utils import timezone

from av_account.models import Communications, Firm
from av_account.utils import VerifiedAndTrustedRequiredMixin
from av_core import settings, logger
from av_payment.forms import TermsForm


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
        self.request.session['discount'] = form.get_discount()
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

        # subscribe customer to default plan
        try:
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'plan': settings.STRIPE_DEFAULT_PLAN}],
                trial_from_plan=True,
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
            return redirect(reverse('ready'))
        else:
            return redirect(reverse('error'))

    def get_context_data(self, **kwargs):
        context = super(CheckoutView, self).get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLIC_KEY
        context['code'] = self.request.session['code']
        return context
