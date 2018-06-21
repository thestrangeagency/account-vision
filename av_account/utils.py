from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views import View
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
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if not user.is_verified:
                user.send_verification_code()
                return redirect_to_login(self.request.get_full_path(), settings.VERIFY_URL, self.get_redirect_field_name())
            if not request.agent.is_trusted:
                send_untrusted_device_email(user, get_ip(request))
                user.send_verification_code()
                return redirect_to_login(self.request.get_full_path(), settings.VERIFY_URL, self.get_redirect_field_name())
        return super(VerifiedAndTrustedRequiredMixin, self).dispatch(request, *args, **kwargs)


class FullRequiredMixin(VerifiedAndTrustedRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        self.required_user_state = 'ready'
        if request.user.is_authenticated:
            if not request.user.is_full_cred():
                return redirect(reverse('disabled'))
            # removing email verification as a condition for using the site. turn it back on here if needed
            if not request.user.is_email_verified:
                return redirect(reverse('email_verify'))
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
