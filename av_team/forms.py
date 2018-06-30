from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.models import Group

from av_account.models import AvUser, Firm


def role_field():
    return forms.ChoiceField(
        choices=[(o.id, str(o).capitalize()) for o in Group.objects.all()],
        required=False,
        help_text='Only Admins can invite, modify, or remove your team members.'
    )


class InviteForm(forms.ModelForm):
    class Meta:
        model = AvUser
        fields = ('first_name', 'last_name', 'email')
    
    def __init__(self, *args, **kwargs):
        super(InviteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Invite'))
        self.fields['role'] = role_field()


class DetailForm(forms.ModelForm):
    class Meta:
        model = AvUser
        fields = ('first_name', 'last_name')
    
    def __init__(self, *args, **kwargs):
        can_delete = kwargs.pop('can_delete', None)
        super(DetailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Save'))
        if can_delete:
            self.helper.add_input(Submit('delete', 'Delete', css_class='mx-2 btn-warning'))
        self.fields['role'] = role_field()


class TeamSettingsForm(forms.ModelForm):
    class Meta:
        model = Firm
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(TeamSettingsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Save'))
