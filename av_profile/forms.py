from crispy_forms.helper import FormHelper
from django.forms import ModelForm
from django.forms import forms

from av_account.models import Bank
from av_utils.utils import FormSubmit


class BankingForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(BankingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(FormSubmit('submit', 'Save'))

    class Meta:
        model = Bank
        fields = ['routing', 'account']

    def clean_account(self):
        account = self.cleaned_data.get('account')
        if '•' in account:
            raise forms.ValidationError(u'Please enter your account number.')
        else:
            return account
