import datetime

import stripe
from actstream import action
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import SuccessURLAllowedHostsMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import FormView, DeleteView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django_agent_trust import revoke_other_agents
from django_agent_trust import trust_agent
from ipware.ip import get_ip

from av_account.models import AvUser, Firm
from av_account.models import UserLogin
from av_account.models import UserSecurity
from av_account.utils import FullyVerifiedRequiredMixin, StripeMixin, StripePlansMixin, VerifiedAndTrustedRequiredMixin, \
    FullRequiredMixin
from av_core import logger, settings
from av_utils.utils import get_object_or_None
from .forms import AccountForm, FirmForm, AccountSetPasswordForm
from .forms import AvUserCreationForm
from .forms import DevicesForm
from .forms import PhoneNumberForm
from .forms import ResendVerificationEmailForm
from .forms import SecurityQuestionsForm
from .forms import VerificationForm


class RegistrationView(FormView):
    template_name = 'register.html'
    form_class = AvUserCreationForm

    def form_valid(self, form):
        user = form.save(commit=False)

        # default to cpa user in this flow
        user.is_cpa = True
        user.save()
        # default to admin group
        group = Group.objects.get(name='admin')
        user.groups.add(group)

        # automatically log in
        password = self.request.POST.get('password1', None)
        authenticated = authenticate(
            username=user.email,
            password=password
        )

        # if login worked, continue cpa signup flow
        if authenticated:
            login(self.request, authenticated)
            user.send_email_verification_code()
            return redirect(reverse('questions'))
        else:
            logger.error('Automatic authentication failure.')


class SecurityQuestionsView(LoginRequiredMixin, FormView):
    template_name = 'questions.html'
    form_class = SecurityQuestionsForm
    success_url = reverse_lazy('phone')

    def dispatch(self, request, *args, **kwargs):
        """
        continue to next step if user already has security questions
        """
        user = request.user
        if user.is_authenticated:
            try:
                us = user.usersecurity
            except UserSecurity.DoesNotExist:
                return super(SecurityQuestionsView, self).dispatch(request, *args, **kwargs)
        return redirect(self.success_url)

    def form_valid(self, form):
        security = form.save(commit=False)
        security.user = self.request.user
        # use a custom setter to hash security answers
        for i in range(1, 3):
            form_answer = form.cleaned_data['answer{}'.format(i)]
            security.set_answer(i, form_answer)
        security.save()
        return super(SecurityQuestionsView, self).form_valid(form)


class PhoneNumberView(LoginRequiredMixin, FormView):
    template_name = 'phone.html'
    form_class = PhoneNumberForm
    success_url = reverse_lazy('verification')

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            try:
                us = user.usersecurity
            except UserSecurity.DoesNotExist:
                return redirect('questions')
        return super(PhoneNumberView, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        user = self.request.user
        return self.form_class(instance=user, **self.get_form_kwargs())

    def form_valid(self, form):
        user = form.save(commit=False)
        user.send_verification_code()
        form.save()
        return super(PhoneNumberView, self).form_valid(form)


class VerificationView(LoginRequiredMixin, FormView):
    template_name = 'verification.html'
    form_class = VerificationForm

    def get_form(self, form_class=None):
        return self.form_class(user=self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        self.request.user.is_verified = True
        self.request.user.save()
        trust_agent(self.request)
        return super(VerificationView, self).form_valid(form)

    def get_success_url(self):
        # a cpa will need to set up a firm, regular users are done here
        if self.request.user.is_cpa and self.request.user.firm is None:
            return reverse_lazy('firm')
        else:
            return reverse_lazy('client_created')


class FirmView(VerifiedAndTrustedRequiredMixin, FormView):
    template_name = 'firm.html'
    form_class = FirmForm
    success_url = reverse_lazy('terms')

    def dispatch(self, request, *args, **kwargs):
        """
        continue to next step if user already has a firm
        """
        if request.user.firm is None:
            return super(FirmView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(self.success_url)

    def form_valid(self, form):
        firm = form.save(commit=False)
        firm.boss = self.request.user
        firm.save()
        self.request.user.firm = firm
        self.request.user.save()
        return super(FirmView, self).form_valid(form)


class InvitationView(FormView):
    template_name = 'invitation.html'
    form_class = AccountSetPasswordForm
    user = None

    def dispatch(self, request, *args, **kwargs):
        # find user matching verification code
        code = self.kwargs['code']
        try:
            user = AvUser.objects.get(email_verification_code=code)
            # if password already set, someone is trying to reuse an invite code
            if user.password:
                return redirect(reverse('home'))
        except ObjectDoesNotExist:
            logger.warn('Attempted to accept invite with bad code')
            return None
        self.user = user
        return super(InvitationView, self).dispatch(request, *args, **kwargs)
    
    def get_form(self, form_class=None):
        return self.form_class(user=self.user, **self.get_form_kwargs())

    def form_valid(self, form):
        user = form.save(commit=False)
        # verify email since user received emailed invite code
        user.is_email_verified = True
        user.save()

        # automatically log in
        password = self.request.POST.get('new_password1', None)
        authenticated = authenticate(
            username=user.email,
            password=password
        )

        # if login worked, continue client signup flow
        if authenticated:
            login(self.request, authenticated)
            return redirect(reverse('questions'))
        else:
            logger.error('Automatic authentication failure.')

    def get_context_data(self, **kwargs):
        context = super(InvitationView, self).get_context_data(**kwargs)
        form = self.get_form()
        if form is not None:
            context['user'] = form.user
        else:
            context['user'] = None
        return context


class TrustView(LoginRequiredMixin, SuccessURLAllowedHostsMixin, FormView):
    """
    Used to establish trust for a new user agent
    Can also be used to verify a new phone number, since phone number verification is already implied
    """
    template_name = 'trust.html'
    form_class = VerificationForm
    success_url = reverse_lazy('returns')

    def get_form(self, form_class=None):
        return self.form_class(user=self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        self.request.user.is_verified = True
        self.request.user.save()
        trust_agent(self.request)
        return super(TrustView, self).form_valid(form)

    get_success_url = LoginView.get_success_url
    get_redirect_url = LoginView.get_redirect_url


class NewEmailView(LoginRequiredMixin, FormView):
    template_name = 'email_verification_sent.html'
    form_class = ResendVerificationEmailForm

    def form_valid(self, form):
        self.request.user.send_email_verification_code()
        messages.success(self.request, 'Another verification email has been sent.')
        return render(self.request, self.template_name, {'form': form})


class DevicesView(FullyVerifiedRequiredMixin, FormView):
    template_name = 'devices.html'
    form_class = DevicesForm
    success_url = reverse_lazy('devices')

    def form_valid(self, form):
        revoke_other_agents(self.request)
        return render(self.request, self.template_name, {'form': form, 'revoked': True})


class LoginsView(FullyVerifiedRequiredMixin, ListView):
    model = UserLogin
    template_name = 'logins.html'
    queryset = UserLogin.objects.order_by('-date_created')[:10]

    def get_context_data(self, **kwargs):
        context = super(LoginsView, self).get_context_data(**kwargs)
        context['ip'] = get_ip(self.request)
        return context


class EditView(FullyVerifiedRequiredMixin, FormView):
    template_name = 'edit.html'
    form_class = AccountForm
    success_url = reverse_lazy('edit')

    def get_form(self, form_class=None):
        user = self.request.user
        return self.form_class(instance=user, **self.get_form_kwargs())

    def post(self, request, *args, **kwargs):
        user = request.user
        email = user.email  # grab email before form changes it
        form = self.get_form()
        if form.is_valid():
            if form.cleaned_data['email'] != email:
                user.previous_email = email
                user.send_email_verification_code()
        return super(EditView, self).post(request)

    def form_valid(self, form):
        form.save()
        return super(EditView, self).form_valid(form)


class SelfDeleteView(FullyVerifiedRequiredMixin, DeleteView):
    model = AvUser
    success_url = reverse_lazy('clients')

    def get_object(self, queryset=None):
        return self.request.user
    
    def delete(self, request, *args, **kwargs):
        user = request.user
        
        # add to activity stream, but omit target as target will be deleted, removing the action
        verb = 'deleted {} {} ({}).'.format(user.first_name, user.last_name, user.email)
        action.send(self.request.user, verb=verb, target=None)
        
        messages.success(self.request, verb.capitalize())
        return super(DeleteView, self).delete(request)


class PlanView(FullRequiredMixin, TemplateView, StripeMixin):
    template_name = 'plan.html'

    def get_context_data(self, **kwargs):
        context = super(PlanView, self).get_context_data(**kwargs)

        customer = stripe.Customer.retrieve(self.request.user.firm.stripe_id)
        subscription = customer.subscriptions.data[0]
        plan = subscription.plan
        plan.amount = str(plan.amount)[:-2]  # convert eg 9900 to 99
        
        context['plan'] = plan
        context['status'] = subscription.status
        context['end'] = datetime.datetime.fromtimestamp(subscription.current_period_end, datetime.timezone.utc)
        context['trial_end'] = datetime.datetime.fromtimestamp(subscription.trial_end, datetime.timezone.utc)
        
        context['cpa_count'] = self.request.user.cpa_count()
        context['client_count'] = self.request.user.client_count()
        
        context['last4'] = customer.sources.data[0].card.last4
        
        return context


class ChangePlanView(FullRequiredMixin, TemplateView, StripePlansMixin):
    template_name = 'plan_change.html'
    success_url = reverse_lazy('plan')
    
    def post(self, request, *args, **kwargs):
        
        if request.POST.get('ya'):
            self.change_plan(settings.STRIPE_PLANS['yearly']['a'])
        elif request.POST.get('ma'):
            self.change_plan(settings.STRIPE_PLANS['monthly']['a'])

        elif request.POST.get('yb'):
            self.change_plan(settings.STRIPE_PLANS['yearly']['b'])
        elif request.POST.get('mb'):
            self.change_plan(settings.STRIPE_PLANS['monthly']['b'])

        elif request.POST.get('yc'):
            self.change_plan(settings.STRIPE_PLANS['yearly']['c'])
        elif request.POST.get('mc'):
            self.change_plan(settings.STRIPE_PLANS['monthly']['c'])
        
        else:
            return render(request, self.template_name, self.get_context_data())
        
        return redirect(self.success_url)


class ChangeCardView(FullyVerifiedRequiredMixin, TemplateView, StripeMixin):
    template_name = 'card_change.html'
    success_url = reverse_lazy('plan')

    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
    
        # modify customer payment source
        try:
            stripe.Customer.modify(self.request.user.firm.stripe_id, source=request.POST.get('source'))
    
        except stripe.error.StripeError as e:
            logger.error('Stripe customer modification error: %s', e)
            return redirect(reverse('plan'))
    
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super(ChangeCardView, self).get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLIC_KEY
        return context


class EmailVerificationView(TemplateView):
    template_name = 'email_verification.html'

    def get_context_data(self, **kwargs):
        context = super(EmailVerificationView, self).get_context_data(**kwargs)

        # find user matching verification code
        code = self.kwargs['code']
        try:
            user = AvUser.objects.get(email_verification_code=code)
            user.is_email_verified = True
            user.save()
            context['verified'] = True
        except ObjectDoesNotExist:
            logger.warn('Attempted to verify with bad code')
            context['verified'] = False
            pass

        return context


class NotReadyView(TemplateView):
    
    def get_template_names(self):
        if self.request.user.is_cpa:
            return 'cpa_not_ready.html'
        else:
            return 'client_not_ready.html'
