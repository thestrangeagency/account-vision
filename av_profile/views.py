from django.urls import reverse_lazy

from av_account.models import Bank, Address
from av_account.utils import ClientRequiredMixin
from av_utils.utils import SimpleFormMixin
from .forms import BankingForm, MyInfoForm, AddressForm


class BankingView(ClientRequiredMixin, SimpleFormMixin):
    template_name = 'av_profile/banking.html'
    form_class = BankingForm
    success_url = reverse_lazy('banking')
    form_message_type = 'banking information'

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


class MyInfoView(ClientRequiredMixin, SimpleFormMixin):
    template_name = 'av_profile/info_my.html'
    form_class = MyInfoForm
    success_url = reverse_lazy('identity')
    form_message_type = 'identity'
    
    def get_form_kwargs(self):
        kwargs = super(MyInfoView, self).get_form_kwargs()
        kwargs.update({
            'instance': self.request.user,
        })
        return kwargs
    

class AddressView(ClientRequiredMixin, SimpleFormMixin):
    template_name = 'av_profile/info_address.html'
    form_class = AddressForm
    success_url = reverse_lazy('address')
    form_message_type = 'address'
    
    def get_form_kwargs(self):
        kwargs = super(AddressView, self).get_form_kwargs()
        if not hasattr(self.request.user, 'address'):
            self.request.user.address = Address.objects.create(user=self.request.user)
            self.request.user.save()
        kwargs.update({
            'instance': self.request.user.address,
        })
        return kwargs
