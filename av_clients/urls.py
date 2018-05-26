from django.conf.urls import url

from av_clients.views import ClientListView, ClientInviteView, ClientImportView, ClientImportPreView, ClientDetailView

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