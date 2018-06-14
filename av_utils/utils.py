from actstream import action
from crispy_forms.layout import BaseInput
from django.conf import settings
from django.contrib import messages
from django.db import models
from django.shortcuts import _get_queryset
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView


class TimeStampedModel(models.Model):
    date_created = models.DateTimeField(_('date created'), default=timezone.now)
    date_modified = models.DateTimeField(_('date modified'), auto_now=True)

    class Meta:
        abstract = True


class ReadOnlyMixin:
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields

        return list(
            [field.name for field in self.opts.local_fields if field.name not in self.get_exclude(request)] +
            [field.name for field in self.opts.local_many_to_many]
        )


class ExcludeDateMixin:
    def get_exclude(self, request, obj=None):
        return ('date_created', 'date_modified')


class CPAViewMixin(ExcludeDateMixin, ReadOnlyMixin):
    pass


class FormMessageMixin(FormView):
    form_message_type = 'information'

    def form_valid(self, form):
        # give user update feedback
        messages.success(self.request, 'Your {} has been updated.'.format(self.form_message_type))
        return super(FormMessageMixin, self).form_valid(form)


class FormActivityMixin(FormView):
    def form_valid(self, form):
        # add form update to activity stream
        for field in form.changed_data:
            verb = 'updated {} on'.format(form[field].label.lower())
            action.send(self.request.user, verb=verb, target=form.instance)
        return super(FormActivityMixin, self).form_valid(form)


class SimpleFormMixin(FormMessageMixin, FormActivityMixin):
    def form_valid(self, form):
        form.save()
        return super(SimpleFormMixin, self).form_valid(form)


class FormSubmit(BaseInput):
    """
    Use instead of Crispy submit to add custom styling
    """
    input_type = 'submit'

    def __init__(self, *args, **kwargs):
        self.field_classes = 'btn btn-primary tx-form-btn'
        super(FormSubmit, self).__init__(*args, **kwargs)


# these are from django-annoying which is causing an installation issue both locally and on heroku
# An error occurred while installing django-annoying==0.10.3! Will try again.

def get_object_or_None(klass, *args, **kwargs):
    """
    Uses get() to return an object or None if the object does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), a MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None


def get_config(key, default=None):
    """
    Get settings from django.conf if exists,
    return default value otherwise

    example:

    ADMIN_EMAIL = get_config('ADMIN_EMAIL', 'default@email.com')
    """
    return getattr(settings, key, default)


def get_object_or_this(model, this=None, *args, **kwargs):
    """
    Uses get() to return an object or the value of <this> argument
    if object does not exist.

    If the <this> argument if not provided None would be returned.
    <model> can be either a QuerySet instance or a class.
    """

    return get_object_or_None(model, *args, **kwargs) or this
