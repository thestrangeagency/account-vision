from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from av_returns.models import *
from av_uploads import utils
from av_uploads.models import S3File
from av_utils.utils import CPAViewMixin, ExcludeDateMixin


class DependentsInline(CPAViewMixin, admin.StackedInline):
    model = Dependent


class SpouseInline(CPAViewMixin, admin.TabularInline):
    model = Spouse


class CommonExpenseInline(CPAViewMixin, admin.StackedInline):
    model = CommonExpenses


class ExpenseInline(CPAViewMixin, admin.TabularInline):
    model = Expense


class UploadsInline(CPAViewMixin, admin.TabularInline):
    model = S3File
    fields = ('id', 'name', 'type', 'size', 'description', 'link')
    verbose_name = "Upload"
    verbose_name_plural = "Uploads"

    def get_readonly_fields(self, request, obj=None):
        fields = super(UploadsInline, self).get_readonly_fields(request, obj)
        if len(fields) == 0:
            return ['link', ]
        else:
            return fields + ['link', ]

    def link(self, file):
        return format_html('<a download="{}" href="{}">{}</a>'.format(file.name, utils.get_s3_url(file), file.name))


class ReturnAdmin(ExcludeDateMixin, admin.ModelAdmin):
    inlines = (SpouseInline, DependentsInline, CommonExpenseInline, ExpenseInline, UploadsInline)

    list_display = ('__str__', 'year', 'return_status')
    list_filter = ('return_status', ('cpa', admin.RelatedOnlyFieldListFilter))
    actions = []

    # i.e. make return_status and cpa editable
    readonly_fields = ('user', 'user_link', 'year', 'is_dependent', 'filing_status', 'county')

    def get_actions(self, request):
        actions = super(ReturnAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def user_link(self, tax_return):
        user = tax_return.user
        url = reverse('admin:%s_%s_change' % (user._meta.app_label, user._meta.model_name), args=[user.id])
        return format_html('<a href="{}">View user info</a>'.format(url))


admin.site.register(Return, ReturnAdmin)
