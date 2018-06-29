from actstream.models import user_stream
from django.views.generic import TemplateView, ListView

from av_account.utils import StripePlansMixin


class HomeView(TemplateView, StripePlansMixin):
    
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
        if self.request.user.is_authenticated:
            if self.request.user.is_cpa:
                context['stream'] = user_stream(self.request.user, with_user_activity=True)
        return context


class AbstractTableView(ListView):
    fields = {}

    def get_context_data(self, **kwargs):
        context = super(AbstractTableView, self).get_context_data(**kwargs)
        context['fields'] = self.fields
        return context
