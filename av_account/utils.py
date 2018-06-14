from actstream import action
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView
from ipware.ip import get_ip

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


class FormMessageMixin(FormView):
    form_message_type = 'information'
    
    def form_valid(self, form):
        # give user update feedback
        messages.success(self.request, 'Your {} has been updated.'.format(self.form_message_type))
        return super(FormMessageMixin, self).form_valid(form)


class FormActivityMixin(FormView):
    def form_valid(self, form):
        # add form update to activity stream
        for field in form.changed_data:
            verb = 'updated {} on'.format(form[field].label.lower())
            action.send(self.request.user, verb=verb, target=form.instance)
        return super(FormActivityMixin, self).form_valid(form)


class SimpleFormMixin(FormMessageMixin, FormActivityMixin):
    def form_valid(self, form):
        form.save()
        return super(SimpleFormMixin, self).form_valid(form)
