from actstream.models import user_stream
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView

from av_account.utils import StripePlansMixin, ClientRequiredMixin, CPARequiredMixin
from av_returns.models import Return


class HomeView(TemplateView, StripePlansMixin):
    template_name = 'home.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            if self.request.user.is_cpa:
                return redirect('cpa-home')
            else:
                return redirect('client-home')
        return super(HomeView, self).dispatch(request, *args, **kwargs)


class ClientHomeView(ClientRequiredMixin, TemplateView):
    template_name = 'home_client.html'

    def get_context_data(self, **kwargs):
        context = super(ClientHomeView, self).get_context_data(**kwargs)
        context['tax_years'] = Return.objects.filter(user=self.request.user)
        return context


class CpaHomeView(CPARequiredMixin, TemplateView):
    template_name = 'home_cpa.html'

    def get_context_data(self, **kwargs):
        context = super(CpaHomeView, self).get_context_data(**kwargs)
        context['stream'] = user_stream(self.request.user, with_user_activity=True)
        return context


class AbstractTableView(ListView):
    fields = {}

    def get_context_data(self, **kwargs):
        context = super(AbstractTableView, self).get_context_data(**kwargs)
        context['fields'] = self.fields
        return context
