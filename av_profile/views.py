from actstream import action
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView

from av_account.models import Bank, Address
from av_account.utils import ClientRequiredMixin
from .forms import BankingForm, MyInfoForm, AddressForm


class BankingView(ClientRequiredMixin, FormView):
    template_name = 'av_profile/banking.html'
    form_class = BankingForm
    success_url = reverse_lazy('banking')

    def get_form(self, form_class=None):
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


class MyInfoView(ClientRequiredMixin, FormView):
    template_name = 'av_profile/info_my.html'
    form_class = MyInfoForm
    success_url = reverse_lazy('identity')
    
    def get_form_kwargs(self):
        kwargs = super(MyInfoView, self).get_form_kwargs()
        kwargs.update({
            'instance': self.request.user,
        })
        return kwargs
    
    def form_valid(self, form):
        form.save()
        # add form update to activity stream
        for field in form.changed_data:
            verb = 'updated {} on'.format(form[field].label.lower())
            action.send(self.request.user, verb=verb, target=form.instance)
        return super(MyInfoView, self).form_valid(form)


class AddressView(ClientRequiredMixin, FormView):
    template_name = 'av_profile/info_address.html'
    form_class = AddressForm
    success_url = reverse_lazy('address')
    
    def get_form_kwargs(self):
        kwargs = super(AddressView, self).get_form_kwargs()
        if not hasattr(self.request.user, 'address'):
            self.request.user.address = Address.objects.create(user=self.request.user)
            self.request.user.save()
        kwargs.update({
            'instance': self.request.user.address,
        })
        return kwargs
    
    def form_valid(self, form):
        form.save()
        # add form update to activity stream
        for field in form.changed_data:
            verb = 'updated {} on'.format(form[field].label.lower())
            action.send(self.request.user, verb=verb, target=form.instance)
        return super(AddressView, self).form_valid(form)
