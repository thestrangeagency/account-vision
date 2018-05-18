from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import SuccessURLAllowedHostsMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django_agent_trust import revoke_other_agents
from django_agent_trust import trust_agent

from .forms import AccountForm
from .forms import BankingForm
from .forms import DevicesForm
from .forms import PhoneNumberForm
from .forms import ResendVerificationEmailForm
from .forms import SecurityQuestionsForm
from .forms import AvUserCreationForm
from .forms import VerificationForm
from av_account.models import Bank
from av_account.models import UserLogin
from av_account.models import UserSecurity
from av_account.utils import ReadyRequiredMixin
from av_core import logger
from utils.utils import get_object_or_None


class RegistrationView(FormView):
    template_name = 'register.html'
    form_class = AvUserCreationForm

    def form_valid(self, form):
        user = form.save()

        password = self.request.POST.get('password1', None)
        authenticated = authenticate(
            username=user.email,
            password=password
        )

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

    def get_form(self):
        if self.request.POST:
            return self.form_class(self.request.POST)
        else:
            security = get_object_or_None(UserSecurity, user=self.request.user)
            form = self.form_class(instance=security)
            # hide answers
            for i in range(1, 4):
                if 'answer{}'.format(i) in form.initial:
                    form.initial['answer{}'.format(i)] = '••••••••'
            return form

    def form_valid(self, form):
        user = self.request.user
        security = get_object_or_None(UserSecurity, user=self.request.user)
        if security is None:
            security = form.save(commit=False)
            security.user = user
        for i in range(1, 4):
            form_answer = form.cleaned_data['answer{}'.format(i)]
            # only save new answers
            if form_answer is not '' and form_answer is not None and '•' not in form_answer:
                security.set_answer(i, form_answer)
        security.save()

        return super(SecurityQuestionsView, self).form_valid(form)


class PhoneNumberView(LoginRequiredMixin, FormView):
    template_name = 'phone.html'
    form_class = PhoneNumberForm
    success_url = reverse_lazy('verification')

    def get_form(self):
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
    success_url = reverse_lazy('created')

    def get_form(self):
        return self.form_class(user=self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        self.request.user.is_verified = True
        self.request.user.save()
        trust_agent(self.request)
        return super(VerificationView, self).form_valid(form)


class TrustView(LoginRequiredMixin, SuccessURLAllowedHostsMixin, FormView):
    """
    Used to establish trust for a new user agent
    Can also be used to verify a new phone number, since phone number verification is already implied
    """
    template_name = 'trust.html'
    form_class = VerificationForm
    success_url = reverse_lazy('returns')

    def get_form(self):
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


class DevicesView(ReadyRequiredMixin, FormView):
    template_name = 'devices.html'
    form_class = DevicesForm
    success_url = reverse_lazy('devices')

    def form_valid(self, form):
        revoke_other_agents(self.request)
        return render(self.request, self.template_name, {'form': form, 'revoked': True})


class LoginsView(ReadyRequiredMixin, ListView):
    model = UserLogin
    template_name = 'logins.html'
    queryset = UserLogin.objects.order_by('-date_created')[:10]


class BankingView(ReadyRequiredMixin, FormView):
    template_name = 'banking.html'
    form_class = BankingForm
    success_url = reverse_lazy('banking')

    def get_form(self):
        bank, created = Bank.objects.get_or_create(user=self.request.user)
        if self.request.POST:
            return self.form_class(instance=bank, **self.get_form_kwargs())
        else:
            form = self.form_class(instance=bank, **self.get_form_kwargs())
            account = form.initial['account']
            if account is not None:
                form.initial['account'] = '•' * (len(account) - 4) + account[-4:]
            return form

    def form_valid(self, form):
        form.save()
        return super(BankingView, self).form_valid(form)


class EditView(ReadyRequiredMixin, FormView):
    template_name = 'edit.html'
    form_class = AccountForm
    success_url = reverse_lazy('edit')

    def get_form(self):
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


class EmailVerificationView(TemplateView):
    template_name = 'email_verification.html'

    def get_context_data(self, **kwargs):
        context = super(EmailVerificationView, self).get_context_data(**kwargs)

        # find user matching verification code
        code = self.kwargs['code']
        try:
            user = TaxUser.objects.get(email_verification_code=code)
            user.is_email_verified = True
            user.save()
            context['verified'] = True
        except ObjectDoesNotExist:
            logger.warn('Attempted to verify with bad code')
            context['verified'] = False
            pass

        return context
