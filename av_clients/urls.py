from django.conf.urls import url

from av_clients.views import *

urlpatterns = [
    url(
        regex=r'^$',
        view=ClientListView.as_view(),
        name='clients',
    ),
    url(
        regex=r'^(?P<username>[\w.@+-]+)/$',
        view=ClientDetailView.as_view(),
        name='client-detail',
    ),
    url(
        regex=r'^(?P<username>[\w.@+-]+)/delete/$',
        view=ClientDeleteView.as_view(),
        name='client-delete',
    ),
    url(
        regex=r'^(?P<username>[\w.@+-]+)/activity/$',
        view=ClientActivityView.as_view(),
        name='client-activity',
    ),
    url(
        regex=r'^(?P<username>[\w.@+-]+)/(?P<year>[0-9]{4})/$',
        view=ClientDetailReturnView.as_view(),
        name='client-detail-return',
    ),

    url(
        regex=r'^(?P<username>[\w.@+-]+)/(?P<year>[0-9]{4})/spouse/$',
        view=ClientDetailReturnView.as_view(template_name='av_clients/spouse.html'),
        name='client-detail-return-spouse',
    ),
    url(
        regex=r'^(?P<username>[\w.@+-]+)/(?P<year>[0-9]{4})/dependents/$',
        view=ClientDetailReturnView.as_view(template_name='av_clients/dependents.html'),
        name='client-detail-return-dependents',
    ),
    url(
        regex=r'^(?P<username>[\w.@+-]+)/(?P<year>[0-9]{4})/uploads/$',
        view=ClientDetailUploadsView.as_view(),
        name='client-detail-return-uploads',
    ),
    url(
        regex=r'^(?P<username>[\w.@+-]+)/(?P<year>[0-9]{4})/expenses/$',
        view=ClientDetailExpensesView.as_view(),
        name='client-detail-return-expenses',
    ),
    url(
        regex=r'^(?P<username>[\w.@+-]+)/(?P<year>[0-9]{4})/returns/$',
        view=ClientDetailReturnView.as_view(template_name='av_clients/downloads.html'),
        name='client-detail-return-returns',
    ),

    url(
        regex=r'^invite$',
        view=ClientInviteView.as_view(),
        name='invite',
    ),
    url(
        regex=r'^import$',
        view=ClientImportView.as_view(),
        name='import',
    ),
    url(
        regex=r'^preview$',
        view=ClientImportPreView.as_view(),
        name='preview',
    ),
]