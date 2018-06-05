from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', ReturnsView.as_view(), name='returns'),
    url(r'^new$', NewReturnView.as_view(), name='new'),

    url(r'^(?P<year>[0-9]{4})/$', ReturnsDetailView.as_view(), name='return'),

    url(r'^(?P<year>[0-9]{4})/e-file$', EFileView.as_view(), name='efile'),
    
    url(r'^(?P<year>[0-9]{4})/expenses/$', ReactView.as_view(template_name='av_returns/expenses.html'), name='expenses'),
    url(r'^(?P<year>[0-9]{4})/uploads/$', ReactView.as_view(template_name='av_returns/uploads.html'), name='uploads'),
    url(r'^(?P<year>[0-9]{4})/spouse/$', SpouseView.as_view(), name='spouse'),
    url(r'^(?P<year>[0-9]{4})/dependents/$', DependentsView.as_view(), name='dependents'),
    url(r'^(?P<year>[0-9]{4})/tax-return/$', DownloadsView.as_view(), name='downloads'),

]
