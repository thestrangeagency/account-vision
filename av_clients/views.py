import csv

import io
import os
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView, DetailView
from django.views.generic.base import View, ContextMixin
from tempfile import NamedTemporaryFile

from av_account.models import AvUser
from av_account.utils import CPARequiredMixin
from av_returns.models import Return, Expense
from av_uploads.models import S3File
from av_utils.utils import get_object_or_None


class ClientListView(CPARequiredMixin, ListView):
    model = AvUser
    template_name = 'av_clients/list.html'

    def get_queryset(self):
        return AvUser.objects.filter(firm=self.request.user.firm, is_cpa=False).order_by('-date_created')


class AbstractClientView(CPARequiredMixin, ContextMixin, View):
    template_name = 'av_clients/return.html'
    
    def get_user(self):
        return get_object_or_404(AvUser, email=self.kwargs['username'], firm=self.request.user.firm)
    
    def get_year(self):
        return self.kwargs.get('year', None)

    def get_return(self):
        return get_object_or_404(Return, year=self.get_year(), user=self.get_user())


class AbstractClientReturnView(AbstractClientView):
    def get_context_data(self, **kwargs):
        context = super(AbstractClientReturnView, self).get_context_data(**kwargs)
        # even though we have object.year, we need this for breadcrumbs
        context['year'] = self.get_year()
        # base template expects user in 'object' variable
        context['return'] = self.get_return()
        context['object'] = self.get_user()
        return context


class ClientDetailView(AbstractClientView, DetailView):
    model = AvUser
    template_name = 'av_clients/detail.html'
    
    def get_object(self, queryset=None):
        return self.get_user()


class ClientDetailReturnView(AbstractClientReturnView, DetailView):
    model = AvUser

    def get_object(self, queryset=None):
        return self.get_return()


class ClientDetailUploadsView(AbstractClientReturnView, ListView):
    model = S3File
    
    def get_queryset(self):
        return S3File.objects.filter(user=self.get_user(), tax_return=self.get_return(), uploaded=True)


class ClientDetailExpensesView(AbstractClientReturnView, ListView):
    model = Expense
    
    def get_queryset(self):
        return Expense.objects.filter(tax_return=self.get_return())


class InviteForm(forms.ModelForm):

    class Meta:
        model = AvUser
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super(InviteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Save'))


class ClientInviteView(CPARequiredMixin, FormView):
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
    for row in csv.reader(io_string, delimiter=',', quotechar='"', skipinitialspace=True):
        if len(row) == 3:
            email = row[2].strip()
            try:
                validate_email(email)
                valid_email = True
            except ValidationError:
                valid_email = False

            user = AvUser(
                first_name=row[0].strip(),
                last_name=row[1].strip(),
                email=email,
                firm=request.user.firm,
            )
            
            existing = get_object_or_None(AvUser, email=user.email)
            if existing is not None:
                setattr(user, 'existing', True)

            for u in users:
                if u.email == email:
                    setattr(user, 'duplicate', True)
                    break

            if not valid_email:
                setattr(user, 'malformed', True)

            users.append(user)

    return users


class ClientImportView(CPARequiredMixin, FormView):
    form_class = UploadFileForm
    template_name = 'av_clients/import.html'
    success_url = reverse_lazy('preview')

    def form_valid(self, form):
        csv_file = self.request.FILES['file']
        decoded_file = csv_file.read().decode('utf-8')

        temp = NamedTemporaryFile(delete=False)
        temp.write(bytes(decoded_file, 'UTF-8'))
        temp.seek(0)

        self.request.session['import_file'] = temp.name

        return super(ClientImportView, self).form_valid(form)


class ClientImportPreView(CPARequiredMixin, FormView):
    form_class = CommitUploadForm
    template_name = 'av_clients/import.html'
    success_url = reverse_lazy('import')

    def form_valid(self, form):
        file_name = self.request.session['import_file']

        if file_name is None:
            messages.error(self.request, 'Import failed.')
            return super(ClientImportPreView, self).form_valid(form)

        users = generate_users(file_name, self.request)
        invite_count = 0
        for user in users:
            existing = get_object_or_None(AvUser, email=user.email)
            if existing is None and not getattr(user, 'malformed', False):
                user.send_invitation_code()
                user.save()
                invite_count += 1

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

        if len(context['users']) == 0:
            context['form'] = None
            messages.error(self.request, 'Nothing to import.')

        return context
