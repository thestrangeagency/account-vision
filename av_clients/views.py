import csv

import os
from tempfile import NamedTemporaryFile

import io
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib import messages
from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, FormView

from av_account.models import AvUser
from av_account.utils import ReadyRequiredMixin
from av_utils.utils import get_object_or_None


class ClientListView(ReadyRequiredMixin, ListView):
    model = AvUser
    template_name = 'av_clients/list.html'

    def get_queryset(self):
        return AvUser.objects.filter(firm=self.request.user.firm, is_cpa=False).order_by('-date_created')


class InviteForm(forms.ModelForm):

    class Meta:
        model = AvUser
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super(InviteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Save'))


class ClientInviteView(ReadyRequiredMixin, FormView):
    form_class = InviteForm
    template_name = 'av_clients/invite.html'
    success_url = reverse_lazy('invite')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.firm = self.request.user.firm
        user.send_invitation_code()
        user.save()
        messages.success(self.request, 'Invitation sent to {}.'.format(user.email))
        return super(ClientInviteView, self).form_valid(form)


class UploadFileForm(forms.Form):
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Upload'))

    def clean_file(self):
        file = self.cleaned_data.get('file', False)

        # wrong extension
        if not file.name.endswith('.csv'):
            raise ValidationError('Your upload does not appear to be a CSV file.')

        # too big
        if file.multiple_chunks():
            raise ValidationError('Your upload is too big. (%.2f MB)' % (file.size / (1024 * 1024)))

        return file


class CommitUploadForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(CommitUploadForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Invite'))


def generate_users(file_name, request):
    csv_file = open(file_name)
    file_data = csv_file.read()
    io_string = io.StringIO(file_data)
    users = []
    for row in csv.reader(io_string, delimiter=',', quotechar='"'):
        print(row)
        if len(row) == 3:
            print("---- creating user")
            user = AvUser(
                first_name=row[0].strip(),
                last_name=row[1].strip(),
                email=row[2].strip(),
                firm=request.user.firm,
            )
            users.append(user)
            print(vars(user))
            existing = get_object_or_None(AvUser, email=user.email)
            print(user.email)
            if existing is not None:
                print("uh oh")
                setattr(user, 'existing', True)
    return users


class ClientImportView(ReadyRequiredMixin, FormView):
    form_class = UploadFileForm
    template_name = 'av_clients/import.html'
    success_url = reverse_lazy('preview')

    def form_valid(self, form):
        csv_file = self.request.FILES['file']
        decoded_file = csv_file.read().decode('utf-8')

        temp = NamedTemporaryFile(delete=False)
        temp.write(bytes(decoded_file, 'UTF-8'))

        temp.seek(0)
        print(temp.read())
        print(temp.name)

        self.request.session['import_file'] = temp.name

        return super(ClientImportView, self).form_valid(form)


class ClientImportPreView(ReadyRequiredMixin, FormView):
    form_class = CommitUploadForm
    template_name = 'av_clients/import.html'
    success_url = reverse_lazy('import')

    def form_valid(self, form):
        print("upload time")
        file_name = self.request.session['import_file']

        if file_name is None:
            messages.error(self.request, 'Import failed.')
            return super(ClientImportPreView, self).form_valid(form)

        print(file_name)
        print(type(file_name))

        users = generate_users(file_name, self.request)
        invite_count = 0
        for user in users:
            existing = get_object_or_None(AvUser, email=user.email)
            if existing is None:
                # user.send_invitation_code()
                # user.save()
                invite_count += 1
                print('invited: ' + user.email)
            else:
                print('skipped: ' + user.email)

        os.remove(file_name)
        self.request.session['import_file'] = None

        messages.success(self.request, 'Invitations have been sent to {} users.'.format(invite_count))
        return super(ClientImportPreView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ClientImportPreView, self).get_context_data(**kwargs)
        file_name = self.request.session['import_file']

        if file_name is None:
            context['form'] = None
            messages.error(self.request, 'Nothing to preview.')
            return context

        context['name'] = file_name
        context['users'] = generate_users(file_name, self.request)

        return context
