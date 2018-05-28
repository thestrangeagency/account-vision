from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.text import wrap
from django.views.generic import FormView
from django_messages.models import Message

from av_account.utils import FullRequiredMixin
from av_messages.forms import CPAMessageComposeForm, AvUserMessageComposeForm


class MessageView(FormView):
    template_name = 'django_messages/compose.html'
    success_url = reverse_lazy('messages_inbox')

    def get_form_class(self):
        if self.request.user.is_cpa:
            return CPAMessageComposeForm
        else:
            return AvUserMessageComposeForm

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        return form_class(user=self.request.user, **self.get_form_kwargs())


class MessageComposeView(FullRequiredMixin, MessageView):
    
    def form_valid(self, form):
        form.save(sender=self.request.user)
        messages.info(self.request, "Message successfully sent.")
        return super(MessageComposeView, self).form_valid(form)


class MessageReplyView(FullRequiredMixin, MessageView):
    subject_template = "Re: %(subject)s"

    def get_parent(self):
        return get_object_or_404(Message, id=self.kwargs['message_id'])
    
    def form_valid(self, form):
        parent = self.get_parent()
        form.save(sender=self.request.user, parent_msg=parent)
        messages.info(self.request, "Message successfully sent.")
        return super(MessageReplyView, self).form_valid(form)

    def get_initial(self):
        parent = self.get_parent()
        return {
            'body': self.format_quote(parent.sender, parent.body),
            'subject': self.subject_template % {'subject': parent.subject},
            'recipient': [parent.sender.id, ]
        }

    def format_quote(self, sender, body):
        """
        Wraps text at 55 chars and prepends each
        line with `> `.
        Used for quoting messages in replies.
        """
        lines = wrap(body, 55).split('\n')
        for i, line in enumerate(lines):
            lines[i] = "> %s" % line
        quote = '\n'.join(lines)
        return quote
