from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import CharField, forms, Form, BooleanField
from django.urls import reverse
from django.utils.safestring import mark_safe


class TermsForm(Form):
    terms = BooleanField(required=False)
    code = CharField(label='Discount Code', required=False)
    codes = {
        'early': 'early_bird',
        '2019': 'one_2019',
    }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TermsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Continue'))
        self.fields['terms'].label = \
            mark_safe('Check to agree to our <a href="%s">terms and conditions</a>.' % reverse('legal'))

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if len(code) == 0:
            return code
        elif code in self.codes:
            return code
        else:
            raise forms.ValidationError(u'This coupon code is invalid')

    def clean_terms(self):
        if not self.cleaned_data.get('terms'):
            raise forms.ValidationError(u'You must agree to our terms and conditions to proceed.')
        else:
            return self.cleaned_data.get('terms')

    def get_coupon(self):
        code = self.cleaned_data.get('code')
        if code in self.codes:
            return self.codes[code]
        else:
            return 0
