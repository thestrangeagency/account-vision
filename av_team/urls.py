from django.conf.urls import url

from av_team.views import *

urlpatterns = [
    url(
        regex=r'^$',
        view=TeamListView.as_view(),
        name='team',
    ),
    url(
        regex=r'^invite$',
        view=TeamInviteView.as_view(),
        name='team-invite',
    ),
]