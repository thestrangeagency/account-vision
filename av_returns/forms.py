import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, MultiWidgetField, HTML, Button
from django.forms import ModelForm, SelectDateWidget, modelformset_factory, Form, DecimalField, BooleanField, forms
from django.urls import reverse

from av_account.models import AvUser, Address
from av_returns.models import Spouse, Dependent
from av_returns.utils import FreezableFormView
from av_utils.utils import FormSubmit


class CustomSelectDateWidget(SelectDateWidget):
    def get_context(self, name, value, attrs):
        context = super(CustomSelectDateWidget, self).get_context(name, value, attrs)
        context['widget']['subwidgets'][0]['label'] = 'Date of Birth'
        return context


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
                years=list(range(datetime.datetime.now().year-100, datetime.datetime.now().year-15)),
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


class SpouseForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(SpouseForm, self).__init__(*args, **kwargs)
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
        model = Spouse
        fields = ['first_name', 'last_name', 'middle_name', 'dob', 'ssn']
        widgets = {
            'dob': CustomSelectDateWidget(
                empty_label=("Choose Year", "Choose Month", "Choose Day"),
                years=list(range(datetime.datetime.now().year - 100, datetime.datetime.now().year - 15)),
            ),
        }


class DependentsFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(DependentsFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
            HTML("{% if forloop.revcounter0 == 0 %}<h5>Add a new dependent below:</h5>{% endif %}"),
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
            Div(
                Div('relationship', css_class='col-md-4'),
                css_class='row'
            ),
            Div(
                HTML("{% if forloop.revcounter0 == 0 %}<span style='display: none;'>{% endif %}"),
                Div('DELETE', css_class='col-md-4'),
                HTML("{% if forloop.revcounter0 == 0 %}</span>{% endif %}"),
                css_class='row'
            ),
        )
        self.render_required_fields = True
        self.add_input(FormSubmit('submit', 'Save'))


# not very DRY but there seems to be no way to neatly freeze the helper
class FrozenDependentsFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(FrozenDependentsFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
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
            Div(
                Div('relationship', css_class='col-md-4'),
                css_class='row mb-4'
            ),
            Div(
                HTML("{% if forloop.revcounter0 == 0 %}"+FreezableFormView.get_html()+"{% endif %}"),
                css_class='row'
            ),
        )
        self.render_required_fields = True
        self.add_input(FormSubmit('submit', 'Save', disabled=True))


class DependentForm(ModelForm):
    class Meta:
        model = Dependent
        fields = ['first_name', 'last_name', 'middle_name', 'dob', 'ssn', 'relationship']
        widgets = {
            'dob': CustomSelectDateWidget(
                empty_label=("Choose Year", "Choose Month", "Choose Day"),
                years=list(range(datetime.datetime.now().year - 100, datetime.datetime.now().year - 15)),
            ),
        }


DependentsFormSet = modelformset_factory(Dependent, form=DependentForm, can_delete=True, extra=1, max_num=9)
FrozenDependentsFormSet = modelformset_factory(Dependent, form=DependentForm, can_delete=False, extra=0, max_num=9)


class ExpenseForm(Form):

    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Save'))

        # list of default expenses
        # TODO perhaps let's store these in the DB, pending conversations about ordering and grouping
        default_expenses = [
            'Office Supplies',
            'Mortgage Interest',
            'Insurance Premiums',
            'Medical Expenses',
            'Real Estate Taxes',
        ]

        for i, expense in enumerate(default_expenses):
            self.fields['expense_%s' % i] = DecimalField(
                label=expense,
                max_digits=16,
                decimal_places=2,
                required=False)


class EFileForm(Form):
    state = BooleanField(required=False, label='I give permission for EZtax101 to file my state return')
    federal = BooleanField(required=False, label='I give permission for EZtax101 to file my federal return')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EFileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Continue'))

    def clean_state(self):
        if not self.cleaned_data.get('state'):
            raise forms.ValidationError(u'You must give EZtax101 permission to file to proceed.')
        return self.cleaned_data.get('state')

    def clean_federal(self):
        if not self.cleaned_data.get('federal'):
            raise forms.ValidationError(u'You must give EZtax101 permission to file to proceed.')
        return self.cleaned_data.get('federal')