from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button
from crispy_forms.layout import Hidden
from crispy_forms.layout import Submit
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import UserCreationForm
from django.forms import CharField
from django.forms import Form
from django.forms import ModelForm
from django.forms import forms

from av_core import settings
from av_utils.utils import FormSubmit
from .models import AvUser
from .models import Firm
from .models import UserSecurity


class AvUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(AvUserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Register'))
        self.fields['password1'].help_text = 'Your password can\'t be too similar to your other information / must contain at least 8 characters / can\'t be a commonly used password / can\'t be entirely numeric.'

    class Meta(UserCreationForm.Meta):
        model = AvUser
        fields = ('email',)


class SecurityQuestionsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SecurityQuestionsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Continue'))
        self.fields['question1'].widget.attrs.update({'autofocus': 'autofocus'})

    class Meta:
        model = UserSecurity
        fields = ['question1', 'answer1', 'question2', 'answer2']

    def clean(self):
        cleaned_data = super(SecurityQuestionsForm, self).clean()

        if len(set((cleaned_data['question1'], cleaned_data['question2']))) < 2:
            raise forms.ValidationError("Please select two unique questions")

        return cleaned_data


class PhoneNumberForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PhoneNumberForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Continue'))
        self.fields['phone'].widget.attrs.update({'autofocus': 'autofocus', 'placeholder': '123-555-1212'})

    class Meta:
        model = AvUser
        fields = ['phone', ]
        labels = {
            'phone': 'Please enter your mobile number',
        }

    def clean(self):
        cleaned_data = super(PhoneNumberForm, self).clean()
        if self.errors:
            return cleaned_data

        if 'phone' not in cleaned_data:
            raise forms.ValidationError("Please enter a phone number")

        if len(cleaned_data['phone']) < 10:
            raise forms.ValidationError("Please enter a phone number")

        return cleaned_data


class VerificationForm(Form):
    verification_code = CharField(max_length=4, min_length=4, label='Verification Code')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(VerificationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Continue'))
        self.fields['verification_code'].widget.attrs.update({'autofocus': 'autofocus'})

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code')
        if settings.DEBUG and not settings.TESTING:
            return verification_code
        if self.user.verification_code.upper() == verification_code.upper():
            return verification_code
        else:
            raise forms.ValidationError(u'Verification code does not match.')


class FirmForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FirmForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Continue'))

    class Meta:
        model = Firm
        fields = ('name', )


class DevicesForm(Form):

    def __init__(self, *args, **kwargs):
        super(DevicesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Stop Trusting Other Devices', css_class='btn-danger'))


class ResendVerificationEmailForm(Form):

    def __init__(self, *args, **kwargs):
        super(ResendVerificationEmailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Resend'))


class AccountForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(FormSubmit('submit', 'Save'))

    class Meta:
        model = AvUser
        fields = ['email', 'phone', 'is_2fa']

    def clean(self):
        is_2fa = self.cleaned_data.get('is_2fa')
        phone = self.cleaned_data.get('phone')
        if (phone is None or len(phone) == 0) and is_2fa:
            raise forms.ValidationError('Please enter a valid phone number to enable two factor authentication.')
        return self.cleaned_data


class AccountPasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(AccountPasswordChangeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Save'))
        # not elegant at all but other options aren't really better
        # https://github.com/django-crispy-forms/django-crispy-forms/issues/242
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-secondary', onclick="window.history.back()"))


class AccountPasswordResetForm(PasswordResetForm):

    def __init__(self, *args, **kwargs):
        super(AccountPasswordResetForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Reset', css_class='btn-danger'))
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-secondary', onclick="window.history.back()"))


class AccountSetPasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super(AccountSetPasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Set New Password', css_class='btn-warning'))


class AccountLoginForm(AuthenticationForm):

    def __init__(self, redirect="", *args, **kwargs):
        super(AccountLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Login'))
        self.helper.add_input(Hidden('next', redirect))
