from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib import messages
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView

from av_account.models import AvUser
from av_account.utils import CPARequiredMixin


class TeamListView(CPARequiredMixin, ListView):
    model = AvUser
    template_name = 'av_team/list.html'

    def get_queryset(self):
        return AvUser.objects.filter(firm=self.request.user.firm, is_cpa=True).order_by('-date_created')


class InviteForm(forms.ModelForm):
    class Meta:
        model = AvUser
        fields = ('first_name', 'last_name', 'email')
    
    def __init__(self, *args, **kwargs):
        super(InviteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Invite'))
        self.fields['role'] = forms.ChoiceField(
            choices=[(o.id, str(o).capitalize()) for o in Group.objects.all()]
        )


class TeamInviteView(CPARequiredMixin, FormView):
    form_class = InviteForm
    template_name = 'av_team/invite.html'
    success_url = reverse_lazy('invite')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.firm = self.request.user.firm
        user.send_invitation_code()
        user.save()
        messages.success(self.request, 'Invitation sent to {}.'.format(user.email))
        return super(TeamInviteView, self).form_valid(form)
