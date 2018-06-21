from django.contrib import messages
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView, DetailView

from av_account.models import AvUser
from av_account.utils import CPAAdminRequiredMixin
from av_team.forms import InviteForm


class TeamListView(CPAAdminRequiredMixin, ListView):
    model = AvUser
    template_name = 'av_team/list.html'

    def get_queryset(self):
        return AvUser.objects.filter(firm=self.request.user.firm, is_cpa=True).order_by('-date_created')


class TeamDetailView(CPAAdminRequiredMixin, DetailView):
    model = AvUser
    template_name = 'av_team/detail.html'
    context_object_name = 'member'

    def get_user(self):
        return get_object_or_404(AvUser, email=self.kwargs['username'], firm=self.request.user.firm)

    def get_object(self, queryset=None):
        return self.get_user()


class TeamInviteView(CPAAdminRequiredMixin, FormView):
    form_class = InviteForm
    template_name = 'av_team/invite.html'
    success_url = reverse_lazy('team-invite')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.firm = self.request.user.firm
        user.is_cpa = True
        user.save()
        group = Group.objects.get(id=form.cleaned_data['role'])
        user.groups.add(group)
        user.send_team_invitation_code()
        messages.success(self.request, 'Invitation sent to {} with {} permissions.'.format(user.email, group))
        return super(TeamInviteView, self).form_valid(form)
