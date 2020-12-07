from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.db import models
from django.urls import reverse_lazy
from django.utils.html import format_html

from .models import Address, Firm
from .models import AvUser
from .models import Bank
from .models import SecurityQuestion


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = AvUser
        fields = ('email', 'password1', 'password2')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = AvUser
        fields = ('email', 'password', 'is_active', 'is_staff')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class AddressInline(admin.StackedInline):
    model = Address


class BankInline(admin.TabularInline):
    model = Bank


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    inlines = (AddressInline, BankInline,)

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'is_staff', 'is_cpa', 'is_email_verified', 'trial_days_left')
    list_filter = ('is_staff', 'is_cpa', 'is_email_verified', 'groups__name')

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
         ),
    )
    formfield_overrides = {
        models.PositiveIntegerField: {'widget': forms.NumberInput},
    }
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()
    readonly_fields = ('email', 'confirmation_link', 'invitation_link')

    def confirmation_link(self, obj):
        url = reverse_lazy('confirmation', args=[obj.email_verification_code])
        return format_html("<a href='{url}'>{url}</a>", url=url)

    def invitation_link(self, obj):
        url = reverse_lazy('invitation', args=[obj.email_verification_code])
        return format_html("<a href='{url}'>{url}</a>", url=url)

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            fieldsets = (
                (None, {'fields': ('email', 'password', 'firm', 'confirmation_link', 'invitation_link', 'verification_code')}),
                ('Personal info', {'fields': ('first_name', 'last_name', 'middle_name', 'phone', 'ssn', 'dob')}),
                ('Permissions', {'fields': ('is_staff', 'groups')}),
            )
        else:
            fieldsets = (
                (None, {'fields': ('email', 'password')}),
                ('Personal info', {'fields': ('first_name', 'last_name', 'middle_name', 'phone', 'ssn', 'dob', 'date_created')}),
            )
        return fieldsets


class FirmAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'is_paid', 'trial_end', 'trial_days_left', 'cpa_count', 'client_count')


admin.site.register(AvUser, UserAdmin)
admin.site.register(SecurityQuestion)
admin.site.register(Firm, FirmAdmin)
