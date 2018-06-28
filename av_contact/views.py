from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import ContactForm


class ContactView(FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact')
    
    def get_initial(self):
        initial = super(ContactView, self).get_initial()
        if not self.request.user.is_anonymous():
            initial['name'] = self.request.user
            initial['email'] = self.request.user.email
        return initial

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Thank you for reaching out! Someone on our team will get back to you shortly.")
        return super(ContactView, self).form_valid(form)
