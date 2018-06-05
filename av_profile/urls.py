from django.conf.urls import url

from .views import *

urlpatterns = [
    # profile
    url(r'^identity/$', MyInfoView.as_view(), name='identity'),
    url(r'^address/$', AddressView.as_view(), name='address'),
    url(r'^banking/$', BankingView.as_view(), name='banking'),
]
