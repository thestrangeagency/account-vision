from actstream.models import actor_stream
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView
from django.views.generic.base import ContextMixin

from av_account.models import AvUser


class HomeView(TemplateView):
    
    def get_template_names(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_cpa:
                return ['home_cpa.html']
            else:
                return ['home_client.html']
        else:
            return ['home.html']
    
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        actions = []
        if self.request.user.is_authenticated:
            if self.request.user.is_cpa:
                users = AvUser.objects.filter(firm=self.request.user.firm, is_cpa=False)
                for user in users:
                    stream = actor_stream(user)
                    for action in stream:
                        actions.append(action)
        context['actions'] = actions
        return context


class AbstractTableView(ListView):
    fields = {}

    def get_context_data(self, **kwargs):
        context = super(AbstractTableView, self).get_context_data(**kwargs)
        context['fields'] = self.fields
        return context
