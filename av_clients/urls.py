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
        regex=r'^(?P<username>[\w.@+-]+)/(?P<year>[0-9]{4})/$',
        view=ClientDetailReturnView.as_view(),
        name='client-detail-return',
    ),

    url(
        regex=r'^(?P<username>[\w.@+-]+)/(?P<year>[0-9]{4})/spouse/$',
        view=ClientDetailReturnView.as_view(),
        name='client-detail-return-spouse',
    ),
    url(
        regex=r'^(?P<username>[\w.@+-]+)/(?P<year>[0-9]{4})/dependents/$',
        view=ClientDetailReturnView.as_view(),
        name='client-detail-return-dependents',
    ),
    url(
        regex=r'^(?P<username>[\w.@+-]+)/(?P<year>[0-9]{4})/uploads/$',
        view=ClientDetailUploadsView.as_view(),
        name='client-detail-return-uploads',
    ),
    url(
        regex=r'^(?P<username>[\w.@+-]+)/(?P<year>[0-9]{4})/expenses/$',
        view=ClientDetailReturnView.as_view(),
        name='client-detail-return-expenses',
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