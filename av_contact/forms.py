from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.exceptions import ValidationError
from django.forms import ModelForm, IntegerField

from .models import Contact


class ContactForm(ModelForm):
    robot_test = IntegerField(label="Betty has three apples. Bob has five. How many apples do they have together?")

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Send'))

    def clean_robot_test(self):
        data = self.cleaned_data['robot_test']
        if data != 8:
            raise ValidationError("Seems like you might be a robot!")
        return data

    class Meta:
        model = Contact
        exclude = ('date_created',)
