from django.forms import ModelForm
from django.views.generic import ListView, FormView

from av_account.models import AvUser
from av_account.utils import ReadyRequiredMixin


class ClientListView(ReadyRequiredMixin, ListView):
    model = AvUser
    template_name = 'av_clients/list.html'
    queryset = AvUser.objects.order_by('-date_created')[:10]


class InviteForm(ModelForm):

    class Meta:
        model = AvUser
        fields = ('first_name', 'last_name', 'email')


class ClientInviteView(ReadyRequiredMixin, FormView):
    form_class = InviteForm
    template_name = 'av_clients/invite.html'

