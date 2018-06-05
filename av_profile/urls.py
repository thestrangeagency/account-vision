from django.conf.urls import url

from .views import *

urlpatterns = [
    # profile
    url(
        regex=r'^banking/$',
        view=BankingView.as_view(),
        name='banking',
    ),
]