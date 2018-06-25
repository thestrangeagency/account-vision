import stripe
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, FormView

from av_account.utils import VerifiedAndTrustedRequiredMixin
from av_core import settings, logger
from av_emails.utils import send_payment_email
from av_payment.forms import TermsForm


class TermsView(VerifiedAndTrustedRequiredMixin, FormView):
    template_name = 'av_payment/terms.html'
    form_class = TermsForm
    success_url = reverse_lazy('checkout')

    def form_valid(self, form):
        self.request.session['terms'] = True
        self.request.session['discount'] = form.get_discount()
        self.request.session['code'] = form.cleaned_data.get('code')
        return super(TermsView, self).form_valid(form)


class CheckoutView(VerifiedAndTrustedRequiredMixin, TemplateView):
    template_name = 'av_payment/checkout.html'
    price = 9900

    def dispatch(self, request, *args, **kwargs):
        if 'terms' not in self.request.session or not self.request.session['terms']:
            return redirect(reverse('terms'))
        return super(CheckoutView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            customer = stripe.Customer.create(
                email=request.user.email,
                source=request.POST.get('source')
            )

        except stripe.error.StripeError as e:
            logger.error('Stripe customer creation error: %s', e)
            return redirect(reverse('error'))

        try:
            charge = stripe.Charge.create(
                customer=customer.id,
                amount=self.get_context_data()['data_amount'],
                currency='usd',
                description='Tax Filing',
                metadata={'user_id': request.user.id},
            )

            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'plan': 'settings.STRIPE_DEFAULT_PLAN'}],
            )

        except stripe.error.StripeError as e:
            logger.error('Stripe charge error: %s', e)
            return redirect(reverse('error'))

        if charge.paid:
            self.request.user.is_paid = True
            self.request.user.save()
            send_payment_email(self.request.user)
            return redirect(reverse('ready'))
        else:
            return redirect(reverse('error'))

    def get_context_data(self, **kwargs):
        context = super(CheckoutView, self).get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLIC_KEY
        total = self.price - self.request.session['discount']
        context['total'] = "${:.2f}".format(total/100)
        context['data_amount'] = int(total)
        context['code'] = self.request.session['code']
        return context
