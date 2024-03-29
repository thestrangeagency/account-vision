import csv

import io
import os
from actstream import action
from actstream.actions import follow
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView, DetailView, DeleteView
from django.views.generic.base import View, ContextMixin, logger
from tempfile import NamedTemporaryFile

from av_account.models import AvUser
from av_account.utils import CPARequiredMixin, StripeMixin, UserViewMixin
from av_core.views import AbstractTableView
from av_returns.models import Return, Expense
from av_uploads.models import S3File
from av_utils.utils import get_object_or_None


def order_by_lower(sort, desc):
    """
    creates ordering function
    note that postgres cannot handle ORDER BY LOWER("av_account_avuser"."date_created") or LOWER("av_account_avuser"."is_verified")
    :param sort: sort field choice
    :param desc: descending?
    :return: ordering function
    """
    if sort == 'reg':
        order = 'is_verified' if desc == 'no' else '-is_verified'

    field = {
        'last': 'last_name',
        'first': 'first_name',
        'email': 'email',
    }.get(sort)

    if field:
        order = Lower(field) if desc == 'no' else Lower(field).desc()
    else:
        order = 'date_created'

    return order


class ClientListView(CPARequiredMixin, ListView):
    model = AvUser
    template_name = 'av_clients/list.html'

    def get_queryset(self):
        sort = self.request.GET.get('sort')
        desc = self.request.GET.get('desc')
        return AvUser.objects.filter(firm=self.request.user.firm, is_cpa=False).order_by(order_by_lower(sort, desc))

    def get_context_data(self, **kwargs):
        context = super(ClientListView, self).get_context_data(**kwargs)
        context['sort'] = self.request.GET.get('sort')
        context['desc'] = self.request.GET.get('desc')
        return context


class AbstractClientView(CPARequiredMixin, ContextMixin, View):
    template_name = 'av_clients/return.html'

    def get_user(self):
        return get_object_or_404(AvUser, email=self.kwargs['username'], firm=self.request.user.firm)

    def get_context_data(self, **kwargs):
        context = super(AbstractClientView, self).get_context_data(**kwargs)
        context['client'] = self.get_user()
        return context


class AbstractClientReturnView(AbstractClientView):
    def get_year(self):
        return self.kwargs.get('year', None)

    def get_return(self):
        return get_object_or_404(Return, year=self.get_year(), user=self.get_user())

    def get_context_data(self, **kwargs):
        context = super(AbstractClientReturnView, self).get_context_data(**kwargs)
        # even though we have object.year, we need this for breadcrumbs to work
        context['year'] = self.get_year()
        context['return'] = self.get_return()
        return context


class ClientDetailView(AbstractClientView, DetailView):
    model = AvUser
    template_name = 'av_clients/detail.html'

    def get_object(self, queryset=None):
        return self.get_user()


class ClientDeleteView(CPARequiredMixin, UserViewMixin, DeleteView):
    model = AvUser
    success_url = reverse_lazy('clients')

    def delete(self, request, *args, **kwargs):
        user = self.get_user()

        # add to activity stream, but omit target as target will be deleted, removing the action
        verb = 'deleted {} {} ({}).'.format(user.first_name, user.last_name, user.email)
        action.send(self.request.user, verb=verb, target=None)
        logger.info('action: {}, {}'.format(self.request.user, verb))

        messages.success(self.request, verb.capitalize())
        return super(ClientDeleteView, self).delete(request)


class ClientActivityView(AbstractClientView, DetailView):
    model = AvUser
    template_name = 'av_clients/activity.html'

    def get_object(self, queryset=None):
        return self.get_user()


class ClientDetailReturnView(AbstractClientReturnView, DetailView):
    model = AvUser

    def get_object(self, queryset=None):
        return self.get_return()


class ClientDetailUploadsView(AbstractClientReturnView, AbstractTableView):
    template_name = 'av_clients/uploads.html'
    model = S3File
    fields = [
        {
            'name': 'Name',
            'field': 'name',
            'link': 'get_absolute_url',
        },
        {
            'name': 'Size',
            'field': 'size',
        },
        {
            'name': 'Type',
            'field': 'type',
        },
    ]

    def get_queryset(self):
        return S3File.objects.filter(user=self.get_user(), tax_return=self.get_return(), uploaded=True)


class ClientDetailExpensesView(AbstractClientReturnView, AbstractTableView):
    template_name = 'av_clients/expenses.html'
    model = Expense
    fields = [
        {
            'name': 'Type',
            'field': 'type',
        },
        {
            'name': 'Amount',
            'field': 'amount',
        },
        {
            'name': 'Notes',
            'field': 'notes',
        },
    ]

    def get_queryset(self):
        return Expense.objects.filter(tax_return=self.get_return())


class InviteForm(forms.ModelForm):

    class Meta:
        model = AvUser
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super(InviteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Invite'))


class ClientInviteView(CPARequiredMixin, FormView, StripeMixin):
    form_class = InviteForm
    template_name = 'av_clients/invite.html'
    success_url = reverse_lazy('invite')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.firm = self.request.user.firm
        user.send_invitation_code()
        user.save()
        messages.success(self.request, 'Invitation sent to {}.'.format(user.email))
        follow(self.request.user, user, actor_only=False)
        return super(ClientInviteView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ClientInviteView, self).get_context_data(**kwargs)

        plan = self.get_subscription().plan

        context['client_count'] = self.request.user.client_count()
        context['max_client'] = int(plan.metadata.max_client)

        return context


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


class ClientImportView(CPARequiredMixin, FormView, StripeMixin):
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

    def get_context_data(self, **kwargs):
        context = super(ClientImportView, self).get_context_data(**kwargs)

        plan = self.get_subscription().plan

        context['client_count'] = self.request.user.client_count()
        context['max_client'] = int(plan.metadata.max_client)

        return context


class ClientImportPreView(CPARequiredMixin, FormView, StripeMixin):
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
                follow(self.request.user, user, actor_only=False)
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

        # this can be helpful in debugging
        # context['name'] = file_name

        context['users'] = generate_users(file_name, self.request)

        if len(context['users']) == 0:
            context['form'] = None
            messages.error(self.request, 'Nothing to import.')

        plan = self.get_subscription().plan

        context['client_count'] = self.request.user.client_count()
        context['max_client'] = int(plan.metadata.max_client)

        return context
