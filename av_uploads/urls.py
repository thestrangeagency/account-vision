from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^get/(?P<id>\d+)/$', UploadUrlView.as_view(), name='upload-url'),
]