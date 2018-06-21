from django.contrib import messages
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView, UpdateView, DetailView, DeleteView

from av_account.models import AvUser
from av_account.utils import CPAAdminRequiredMixin, UserViewMixin
from av_team.forms import InviteForm, DetailForm
from av_utils.utils import SimpleFormMixin


class TeamListView(CPAAdminRequiredMixin, ListView):
    model = AvUser
    template_name = 'av_team/list.html'

    def get_queryset(self):
        return AvUser.objects.filter(firm=self.request.user.firm, is_cpa=True).order_by('-date_created')


class TeamDetailView(CPAAdminRequiredMixin, UserViewMixin, UpdateView, SimpleFormMixin):
    model = AvUser
    template_name = 'av_team/detail.html'
    context_object_name = 'member'
    form_class = DetailForm
    form_message_type = 'team member'

    def get_initial(self):
        initial = super(TeamDetailView, self).get_initial()
        initial['role'] = self.get_user().groups.first().id
        return initial

    def post(self, request, *args, **kwargs):
        if 'delete' in request.POST:
            return HttpResponseRedirect(reverse_lazy('team-delete', args=[self.get_user().email]))
        else:
            return super(TeamDetailView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        user.groups.clear()
        group = Group.objects.get(id=form.cleaned_data['role'])
        user.groups.add(group)
        return super(TeamDetailView, self).form_valid(form)


class TeamDeleteView(CPAAdminRequiredMixin, UserViewMixin, DeleteView):
    model = AvUser
    success_url = reverse_lazy('team')

    def delete(self, request, *args, **kwargs):
        user = self.get_user()
        messages.success(self.request, 'Deleted {} {} ({}).'.format(user.first_name, user.last_name, user.email))
        return super(TeamDeleteView, self).delete(request)
    

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


class TeamActivityView(CPAAdminRequiredMixin, UserViewMixin, DetailView):
    model = AvUser
    template_name = 'av_team/activity.html'
    context_object_name = 'member'

