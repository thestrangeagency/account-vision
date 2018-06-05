from django.urls import reverse_lazy
from django.views.generic import FormView

from av_account.models import Bank
from av_account.utils import ClientRequiredMixin
from .forms import BankingForm


class BankingView(ClientRequiredMixin, FormView):
    template_name = 'av_profile/banking.html'
    form_class = BankingForm
    success_url = reverse_lazy('banking')

    def get_form(self):
        bank, created = Bank.objects.get_or_create(user=self.request.user)
        if self.request.POST:
            return self.form_class(instance=bank, **self.get_form_kwargs())
        else:
            form = self.form_class(instance=bank, **self.get_form_kwargs())
            account = form.initial['account']
            if account is not None:
                form.initial['account'] = '•' * (len(account) - 4) + account[-4:]
            return form

    def form_valid(self, form):
        form.save()
        return super(BankingView, self).form_valid(form)
