import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, MultiWidgetField
from django.forms import ModelForm
from django.forms import forms

from av_account.models import Bank, Address, AvUser
from av_returns.forms import CustomSelectDateWidget
from av_utils.utils import FormSubmit


class MyInfoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(MyInfoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('first_name', css_class='col-md-4'),
                Div('last_name', css_class='col-md-4'),
                Div('middle_name', css_class='col-md-4'),
                css_class='row'
            ),
            MultiWidgetField('dob', template='bootstrap4/date_field.html'),
            Div(
                Div('ssn', css_class='col-md-4'),
                css_class='row'
            ),
        )
        self.helper.add_input(FormSubmit('submit', 'Save'))
    
    class Meta:
        model = AvUser
        fields = ['first_name', 'last_name', 'middle_name', 'dob', 'ssn']
        widgets = {
            'dob': CustomSelectDateWidget(
                empty_label=("Choose Year", "Choose Month", "Choose Day"),
                years=list(range(datetime.datetime.now().year - 100, datetime.datetime.now().year - 15)),
            ),
        }


class AddressForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div('address1', css_class=''),
            Div('address2', css_class=''),
            Div('city', css_class=''),
            Div(
                Div('state', css_class='col-md-8'),
                Div('zip', css_class='col-md-4'),
                css_class='row'
            ),
        )
        self.helper.add_input(FormSubmit('submit', 'Save'))
    
    class Meta:
        model = Address
        fields = ['address1', 'address2', 'city', 'state', 'zip']


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
