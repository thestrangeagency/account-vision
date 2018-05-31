from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', ReturnsView.as_view(), name='returns'),
    url(r'^new$', NewReturnView.as_view(), name='new'),

    url(r'^(?P<year>[0-9]{4})/$', ReturnsDetailView.as_view(), name='return'),

    url(r'^(?P<year>[0-9]{4})/e-file$', EFileView.as_view(), name='efile'),
    url(r'^(?P<year>[0-9]{4})/info/$', PersonalInfoView.as_view(), name='info'),

    url(r'^(?P<year>[0-9]{4})/info/my/$', MyInfoView.as_view(), name='info_my'),
    url(r'^(?P<year>[0-9]{4})/info/address/$', AddressView.as_view(), name='info_address'),
    url(r'^(?P<year>[0-9]{4})/info/spouse/$', SpouseView.as_view(), name='info_spouse'),
    url(r'^(?P<year>[0-9]{4})/info/dependents/$', DependentsView.as_view(), name='info_dependents'),
    url(r'^(?P<year>[0-9]{4})/tax-return/$', DownloadsView.as_view(), name='downloads'),
    
    url(r'^(?P<year>[0-9]{4})/expenses/common$', ReactView.as_view(template_name='av_returns/expenses/common.html'), name='expenses-common'),
    url(r'^(?P<year>[0-9]{4})/expenses/custom$', ReactView.as_view(template_name='av_returns/expenses/custom.html'), name='expenses-custom'),
    url(r'^(?P<year>[0-9]{4})/uploads/$', ReactView.as_view(template_name='av_returns/uploads.html'), name='uploads'),
]
