from av_account.models import AvUser
from av_contact.models import Contact
from django.contrib import admin


class ContactAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'subject', 'is_user')

    def is_user(self, contact):
        return AvUser.objects.filter(email=contact.email).count() > 0
    
    is_user.boolean = True

    
admin.site.register(Contact, ContactAdmin)
