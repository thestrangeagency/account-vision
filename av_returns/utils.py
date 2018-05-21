from crispy_forms.layout import Button, HTML
from django.urls import reverse
from django.views.generic import FormView

from av_returns.models import Return


class FreezableFormView(FormView):
    def get_form(self, form_class=None):
        form = super(FreezableFormView, self).get_form(form_class)
        tax_return = Return.objects.get(user=self.request.user, year=self.kwargs['year'])
        if tax_return.is_frozen():
            FreezableFormView.freeze_form(form)
        return form

    @staticmethod
    def freeze_form(form):
        if hasattr(form, 'helper'):
            FreezableFormView.freeze_helper(form.helper)
        for field in form.fields:
            form.fields[field].disabled = True
        return form

    @staticmethod
    def freeze_helper(helper):
        button = helper.inputs.pop()
        helper.layout.append(Button('', button.value, css_class='btn-primary disabled'))
        helper.layout.append(HTML(FreezableFormView.get_html()))
        return helper

    @staticmethod
    def get_html():
        return "<small class='text-muted form-text col-md-8 mt-2'> " \
               "Your return is currently being prepared, during this time updates will not be allowed. " \
               "Should you need to add anything, or have questions for our CPAs, please message them " \
               "directly via the <a href='{}'>messaging</a> tab in your account." \
               "</small>".format(reverse('messages_inbox'))
