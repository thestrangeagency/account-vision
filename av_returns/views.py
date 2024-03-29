import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.views.generic.list import ListView

from av_account.utils import ClientRequiredMixin
from av_returns.forms import SpouseForm, DependentsFormSet, DependentsFormSetHelper, \
    EFileForm, FrozenDependentsFormSet, FrozenDependentsFormSetHelper, NewReturnForm, EditReturnForm
from av_returns.utils import FreezableFormView
from av_uploads.models import S3File
from av_utils.utils import SimpleFormMixin
from .models import Return, Dependent


class ReturnsView(ClientRequiredMixin, ListView):
    model = Return

    def get_queryset(self):
        return Return.objects.filter(user=self.request.user).order_by('-year')

    def get_context_data(self, **kwargs):
        context = super(ReturnsView, self).get_context_data(**kwargs)
        tz_info = self.request.user.date_created.tzinfo
        age = datetime.datetime.now(tz_info) - self.request.user.date_created
        age_hours = age.total_seconds() / 3600
        if age_hours < 24:
            context['new_user'] = True
        return context


class NewReturnView(ClientRequiredMixin, FormView):
    form_class = NewReturnForm
    template_name = 'av_returns/new.html'
    success_url = reverse_lazy('returns')

    def get_form(self, form_class=None):
        # add user to form so it can validate unique user/year constraint
        return NewReturnForm(user=self.request.user,  **self.get_form_kwargs())

    def form_valid(self, form):
        tax_return = form.save(commit=False)
        tax_return.user = self.request.user
        tax_return.save()
        return super(NewReturnView, self).form_valid(form)


class ReturnsDetailView(ClientRequiredMixin, SimpleFormMixin):
    form_class = EditReturnForm
    model = Return
    template_name = 'av_returns/return_detail.html'
    form_message_type = 'tax year'

    def get_success_url(self, **kwargs):
        return reverse_lazy('return', args={self.kwargs['year']})
    
    def get_form_kwargs(self):
        kwargs = super(ReturnsDetailView, self).get_form_kwargs()
        tax_return = Return.objects.get(user=self.request.user, year=self.kwargs['year'])
        try:
            kwargs.update({
                'instance': tax_return,
            })
        except ObjectDoesNotExist:
            pass
        return kwargs

    def get_object(self):
        return get_object_or_404(Return, year=self.kwargs['year'], user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(ReturnsDetailView, self).get_context_data(**kwargs)
        year = self.kwargs['year']
        # even though we have object.year, we need this for breadcrumbs
        context['year'] = year

        # # check for downloads
        # context['downloads'] = S3File.objects.filter(target_user=self.request.user, tax_return__year=year).count()
        # # calculate status bar
        # if self.object.return_status == Return.DRAFT:
        #     status = 1
        # elif self.object.return_status == Return.REVIEW:
        #     status = 2
        # elif self.object.return_status == Return.COMPLETE or self.object.return_status == Return.READY:
        #     status = 3
        # elif self.object.return_status == Return.FILED:
        #     status = 4
        # context['status'] = status

        # switched to form view from detail view, so need this:
        context['object'] = self.get_object()
        return context


class ReactView(ClientRequiredMixin, TemplateView):

    def get_context_data(self, **kwargs):
        context = super(ReactView, self).get_context_data(**kwargs)
        context['year'] = self.kwargs['year']
        context['frozen'] = Return.objects.get(user=self.request.user, year=self.kwargs['year']).is_frozen()
        if context['frozen']:
            context['explanation'] = FreezableFormView.get_html()
        return context


class DownloadsView(ClientRequiredMixin, TemplateView):
    template_name = 'av_returns/downloads.html'

    def get_context_data(self, **kwargs):
        context = super(DownloadsView, self).get_context_data(**kwargs)
        year = self.kwargs['year']
        files = S3File.objects.filter(target_user=self.request.user, tax_return__year=year)
        context['downloads'] = files
        context['year'] = year
        return context


class SpouseView(ClientRequiredMixin, FreezableFormView):
    template_name = 'av_returns/spouse.html'
    form_class = SpouseForm

    def get_form_kwargs(self):
        kwargs = super(SpouseView, self).get_form_kwargs()
        tax_return = Return.objects.get(user=self.request.user, year=self.kwargs['year'])
        try:
            kwargs.update({
                'instance': tax_return.spouse,
            })
        except ObjectDoesNotExist:
            pass
        return kwargs

    def form_valid(self, form):
        spouse = form.save(commit=False)
        spouse.tax_return = Return.objects.get(user=self.request.user, year=self.kwargs['year'])
        form.save()
        return super(SpouseView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(SpouseView, self).get_context_data(**kwargs)
        context['year'] = self.kwargs['year']
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('spouse', args={self.kwargs['year']})


class DependentsView(ClientRequiredMixin, TemplateView):
    template_name = 'av_returns/dependents.html'

    def post(self, request, *args, **kwargs):
        formset = DependentsFormSet(self.request.POST, self.request.FILES)
        if formset.is_valid():
            tax_return = Return.objects.get(user=self.request.user, year=kwargs['year'])
            instances = formset.save(commit=False)
            for instance in instances:
                instance.tax_return = tax_return
                instance.save()
            for deleted in formset.deleted_objects:
                deleted.delete()
            return redirect(self.get_success_url())
        else:
            return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(DependentsView, self).get_context_data(**kwargs)

        tax_return = Return.objects.get(user=self.request.user, year=self.kwargs['year'])

        if tax_return.is_frozen():
            context['helper'] = FrozenDependentsFormSetHelper()
        else:
            context['helper'] = DependentsFormSetHelper()

        if self.request.POST:
            context['formset'] = DependentsFormSet(self.request.POST)
            context['formset'].full_clean()
        else:
            if tax_return.is_frozen():
                context['formset'] = FrozenDependentsFormSet(queryset=Dependent.objects.filter(tax_return=tax_return))
                for form in context['formset'].forms:
                    FreezableFormView.freeze_form(form)
            else:
                context['formset'] = DependentsFormSet(queryset=Dependent.objects.filter(tax_return=tax_return))
            context['year'] = self.kwargs['year']
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('dependents', args={self.kwargs['year']})


class EFileView(ClientRequiredMixin, FormView):
    template_name = 'av_returns/efile.html'
    form_class = EFileForm

    def dispatch(self, request, *args, **kwargs):
        year = self.kwargs['year']
        tax_return = Return.objects.get(user=self.request.user, year=year)
        if tax_return.return_status != tax_return.COMPLETE:
            return redirect('return', year)
        return super(EFileView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        tax_return = Return.objects.get(user=self.request.user, year=self.kwargs['year'])
        tax_return.return_status = tax_return.READY
        tax_return.save()
        return super(EFileView, self).form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse_lazy('return', args={self.kwargs['year']})