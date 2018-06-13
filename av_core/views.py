from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView


class HomeView(TemplateView):
    template_name = 'home.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            if self.request.user.is_cpa:
                return redirect('clients')
            else:
                return redirect('returns')
        else:
            return super(HomeView, self).dispatch(request, *args, **kwargs)


class AbstractTableView(ListView):
    fields = {}

    def get_context_data(self, **kwargs):
        context = super(AbstractTableView, self).get_context_data(**kwargs)
        context['fields'] = self.fields
        return context
