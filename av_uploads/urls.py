from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', CpaUserView.as_view(), name='cpa-user'),
    url(r'^(?P<id>\d+)/$', CpaReturnView.as_view(), name='cpa-return'),
    url(r'^(?P<id>\d+)/(?P<year>[0-9]{4})/$', CpaUploadsView.as_view(), name='cpa-uploads'),
]