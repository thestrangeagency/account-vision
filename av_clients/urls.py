from django.conf.urls import url

from av_clients.views import ClientListView, ClientInviteView

urlpatterns = [
    url(
        regex=r'^$',
        view=ClientListView.as_view(),
        name='clients',
    ),
    url(
        regex=r'^invite$',
        view=ClientInviteView.as_view(),
        name='invite',
    ),
    url(
        regex=r'^import$',
        view=ClientListView.as_view(),
        name='import',
    ),
]