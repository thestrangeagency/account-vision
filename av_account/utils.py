import stripe
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic.base import ContextMixin
from ipware.ip import get_ip

from av_account.models import AvUser
from av_core import settings
from av_emails.utils import send_untrusted_device_email


class UserStateRequiredMixin(LoginRequiredMixin):
    required_user_state = 'none'
    
    def render_to_response(self, context, **response_kwargs):
        context['required_user_state'] = self.required_user_state
        return super(UserStateRequiredMixin, self).render_to_response(context, **response_kwargs)


class VerifiedAndTrustedRequiredMixin(UserStateRequiredMixin):
    """
    Requires phone number to have been verified and device to be trusted
    """
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if not user.is_verified:
                # does user have a phone number yet?
                if user.phone is None:
                    return redirect('phone')
                else:
                    user.send_verification_code()
                    return redirect_to_login(self.request.get_full_path(), settings.VERIFY_URL, self.get_redirect_field_name())
            if not request.agent.is_trusted:
                send_untrusted_device_email(user, get_ip(request))
                user.send_verification_code()
                return redirect_to_login(self.request.get_full_path(), settings.VERIFY_URL, self.get_redirect_field_name())
        return super(VerifiedAndTrustedRequiredMixin, self).dispatch(request, *args, **kwargs)


class FullyVerifiedRequiredMixin(VerifiedAndTrustedRequiredMixin):
    """
    Requires email and phone number to have been verified and device to be trusted
    """
    def dispatch(self, request, *args, **kwargs):
        self.required_user_state = 'verified phone and email'
        if request.user.is_authenticated:
            if not request.user.is_email_verified:
                return redirect(reverse('email_verify'))
        return super(FullyVerifiedRequiredMixin, self).dispatch(request, *args, **kwargs)


class FullRequiredMixin(FullyVerifiedRequiredMixin):
    """
    Ensure the user is a client or is a cpa who has paid or is trialing
    """
    def dispatch(self, request, *args, **kwargs):
        self.required_user_state = 'ready'
        if request.user.is_authenticated:
            if not request.user.is_full_cred():
                if request.user.is_cpa:
                    if request.user.firm is None:
                        return redirect(reverse('firm'))
                    elif request.user.firm.stripe_id is None:
                        return redirect(reverse('payment'))
                    else:
                        return redirect(reverse('disabled'))
        return super(FullRequiredMixin, self).dispatch(request, *args, **kwargs)


class ClientRequiredMixin(FullRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_cpa:
                return redirect(reverse('home'))
        return super(ClientRequiredMixin, self).dispatch(request, *args, **kwargs)


class CPARequiredMixin(FullRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_cpa:
                return redirect(reverse('home'))
        return super(CPARequiredMixin, self).dispatch(request, *args, **kwargs)


class CPAAdminRequiredMixin(CPARequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_admin():
                return redirect(reverse('home'))
        return super(CPARequiredMixin, self).dispatch(request, *args, **kwargs)


class UserViewMixin(View):
    def get_user(self):
        return get_object_or_404(AvUser, email=self.kwargs['username'], firm=self.request.user.firm)
    
    def get_object(self, queryset=None):
        return self.get_user()


class StripeMixin(View):
    def dispatch(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        return super(StripeMixin, self).dispatch(request, *args, **kwargs)
    
    def get_subscription(self):
        customer = stripe.Customer.retrieve(self.request.user.firm.stripe_id)
        return customer.subscriptions.data[0]
    
    def change_plan(self, plan_id):
        subscription = self.get_subscription()
        stripe.Subscription.modify(subscription.id,
                                   cancel_at_period_end=False,
                                   items=[{
                                       'id': subscription['items']['data'][0].id,
                                       'plan': plan_id,
                                   }]
                                   )


class StripePlansMixin(ContextMixin, StripeMixin):
    def get_context_data(self, **kwargs):
        context = super(StripePlansMixin, self).get_context_data(**kwargs)
        
        # retrieve all plans at once for speed
        plans = stripe.Plan.list()
        
        # pluck out the plans we are interested in
        plan_a = next(x for x in plans.data if x.id == settings.STRIPE_PLANS['yearly']['a'])
        plan_b = next(x for x in plans.data if x.id == settings.STRIPE_PLANS['yearly']['b'])
        plan_c = next(x for x in plans.data if x.id == settings.STRIPE_PLANS['yearly']['c'])
        
        plan_am = next(x for x in plans.data if x.id == settings.STRIPE_PLANS['monthly']['a'])
        plan_bm = next(x for x in plans.data if x.id == settings.STRIPE_PLANS['monthly']['b'])
        plan_cm = next(x for x in plans.data if x.id == settings.STRIPE_PLANS['monthly']['c'])
        
        # calculate display versions of prices
        plan_a.amount = round(plan_a.amount / 1200)
        plan_b.amount = round(plan_b.amount / 1200)
        plan_c.amount = round(plan_c.amount / 1200)
        
        plan_am.amount = round(plan_am.amount / 100)
        plan_bm.amount = round(plan_bm.amount / 100)
        plan_cm.amount = round(plan_cm.amount / 100)
        
        # show monthly option in yearly plans
        plan_a.metadata.monthly = plan_am.amount
        plan_b.metadata.monthly = plan_bm.amount
        plan_c.metadata.monthly = plan_cm.amount
        
        plan_a.metadata.post = 'a'
        plan_b.metadata.post = 'b'
        plan_c.metadata.post = 'c'
        
        # if logged in, check usage to calculate plan availability
        if self.request.user.is_authenticated:
            cpa_count = self.request.user.cpa_count()
            client_count = self.request.user.client_count()
            
            if cpa_count > int(plan_a.metadata.max_cpa) or client_count > int(plan_a.metadata.max_client):
                plan_a.metadata.disabled = True
            
            context['cpa_count'] = cpa_count
            context['client_count'] = client_count
        
        context['plans'] = [plan_a, plan_b, plan_c]
        
        return context
