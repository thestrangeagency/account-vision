from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from av_account.utils import ReadyRequiredMixin
from av_returns.forms import MyInfoForm, SpouseForm, DependentsFormSet, AddressForm, DependentsFormSetHelper, \
    EFileForm, FrozenDependentsFormSet, FrozenDependentsFormSetHelper
from av_returns.utils import FreezableFormView
from av_uploads.models import S3File
from av_uploads.utils import get_s3_url
from .models import Return, Dependent


class ReturnsView(ReadyRequiredMixin, ListView):
    model = Return

    def get_queryset(self):
        return Return.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(ReturnsView, self).get_context_data(**kwargs)
        tz_info = self.request.user.date_created.tzinfo
        age = datetime.now(tz_info) - self.request.user.date_created
        age_hours = age.total_seconds() / 3600
        if age_hours < 24:
            context['new_user'] = True
        return context


class ReturnForm(ModelForm):

    class Meta:
        model = Return
        fields = ('year', 'filing_status', 'is_dependent', 'county')


class NewReturnView(ReadyRequiredMixin, FormView):
    form_class = ReturnForm
    template_name = 'av_returns/new.html'
    success_url = reverse_lazy('returns')

    def form_valid(self, form):
        tax_return = form.save(commit=False)
        tax_return.user = self.request.user
        tax_return.save()
        return super(NewReturnView, self).form_valid(form)


class ReturnsDetailView(ReadyRequiredMixin, DetailView):
    model = Return

    def get_object(self):
        return get_object_or_404(Return, year=self.kwargs['year'], user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(ReturnsDetailView, self).get_context_data(**kwargs)
        year = self.kwargs['year']
        # even though we have object.year, we need this for breadcrumbs
        context['year'] = year
        # check for downloads
        context['downloads'] = S3File.objects.filter(target_user=self.request.user, tax_return__year=year).count()
        # calculate status bar
        if self.object.return_status == Return.DRAFT:
            status = 1
        elif self.object.return_status == Return.REVIEW:
            status = 2
        elif self.object.return_status == Return.COMPLETE or self.object.return_status == Return.READY:
            status = 3
        elif self.object.return_status == Return.FILED:
            status = 4
        context['status'] = status
        return context

    def post(self, request, *args, **kwargs):
        tax_return = self.get_object()
        tax_return.return_status = Return.REVIEW
        tax_return.save()
        return self.get(request)


class PersonalInfoView(ReadyRequiredMixin, TemplateView):
    template_name = 'returns/info.html'

    def get_context_data(self, **kwargs):
        context = super(PersonalInfoView, self).get_context_data(**kwargs)
        tax_return = Return.objects.get(user=self.request.user, year=self.kwargs['year'])
        try:
            context['spouse'] = tax_return.spouse
        except ObjectDoesNotExist:
            pass
        context['dependents'] = tax_return.dependent_set
        return context


class ReactView(ReadyRequiredMixin, TemplateView):

    def get_context_data(self, **kwargs):
        context = super(ReactView, self).get_context_data(**kwargs)
        context['year'] = self.kwargs['year']
        context['frozen'] = Return.objects.get(user=self.request.user, year=self.kwargs['year']).is_frozen()
        if context['frozen']:
            context['explanation'] = FreezableFormView.get_html()
        return context


class DownloadsView(ReadyRequiredMixin, TemplateView):
    template_name = 'returns/downloads.html'

    def get_context_data(self, **kwargs):
        context = super(DownloadsView, self).get_context_data(**kwargs)
        year = self.kwargs['year']
        files = S3File.objects.filter(target_user=self.request.user, tax_return__year=year)
        for file in files:
            file.url = get_s3_url(file)
        context['downloads'] = files
        context['year'] = year
        return context


class MyInfoView(ReadyRequiredMixin, FreezableFormView):
    template_name = 'returns/info_my.html'
    form_class = MyInfoForm

    def get_form_kwargs(self):
        kwargs = super(MyInfoView, self).get_form_kwargs()
        kwargs.update({
            'instance': self.request.user,
        })
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(MyInfoView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(MyInfoView, self).get_context_data(**kwargs)
        context['year'] = self.kwargs['year']
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('info_my', args={self.kwargs['year']})


class AddressView(ReadyRequiredMixin, FreezableFormView):
    template_name = 'returns/info_address.html'
    form_class = AddressForm

    def get_form_kwargs(self):
        kwargs = super(AddressView, self).get_form_kwargs()
        kwargs.update({
            'instance': self.request.user.address,
        })
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(AddressView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(AddressView, self).get_context_data(**kwargs)
        context['year'] = self.kwargs['year']
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('info_address', args={self.kwargs['year']})


class SpouseView(ReadyRequiredMixin, FreezableFormView):
    template_name = 'returns/info_spouse.html'
    form_class = SpouseForm

    def get_form_kwargs(self):
        tax_return = Return.objects.get(user=self.request.user, year=self.kwargs['year'])
        spouse = tax_return.spouse
        kwargs = super(SpouseView, self).get_form_kwargs()
        kwargs.update({
            'instance': spouse,
        })
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(SpouseView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(SpouseView, self).get_context_data(**kwargs)
        context['year'] = self.kwargs['year']
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('info_spouse', args={self.kwargs['year']})


class DependentsView(ReadyRequiredMixin, TemplateView):
    template_name = 'returns/info_dependents.html'

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
        return reverse_lazy('info_dependents', args={self.kwargs['year']})


class EFileView(FormView):
    template_name = 'returns/efile.html'
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