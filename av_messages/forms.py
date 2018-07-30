from django import forms
from django.forms import ModelChoiceField, HiddenInput
from django_messages.forms import ComposeForm

from av_account.models import AvUser


class BootstrapComposeForm(ComposeForm):
    subject = forms.CharField(
        label="Subject",
        max_length=140,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        )
    )
    body = forms.CharField(
        label="Message",
        widget=forms.Textarea(
            attrs={
                'rows': '8',
                'cols': '55',
                'class': 'form-control',
            }
        )
    )


class AvUserMessageComposeForm(BootstrapComposeForm):
    recipient = forms.CharField(label="", required=False, max_length=64, widget=HiddenInput())

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AvUserMessageComposeForm, self).__init__(*args, **kwargs)

    def full_clean(self):
        super(AvUserMessageComposeForm, self).full_clean()
        if not self.is_bound:  # Stop further processing.
            return

        if self.cleaned_data['recipient']:
            # already have a recipient, so must be a reply
            cpa = AvUser.objects.get(firm=self.user.firm, is_cpa=True, id=self.cleaned_data['recipient'])
            self.cleaned_data['recipient'] = [cpa]
        else:
            # not a reply, default to firm boss
            cpa = AvUser.objects.get(id=self.user.firm.boss.id, is_cpa=True)
            self.cleaned_data['recipient'] = [cpa]


class UserModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name_and_email()


class CPAMessageComposeForm(BootstrapComposeForm):
    recipient = UserModelChoiceField(
        queryset=AvUser.objects.none(),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        )
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CPAMessageComposeForm, self).__init__(*args, **kwargs)
        self.fields['recipient'].queryset = AvUser.objects.filter(firm=self.user.firm).exclude(id=self.user.id)

    def full_clean(self):
        super(CPAMessageComposeForm, self).full_clean()
        if not self.is_bound:  # Stop further processing.
            return

        # wrap in array as the parent form expects one
        self.cleaned_data['recipient'] = [self.cleaned_data['recipient']]
