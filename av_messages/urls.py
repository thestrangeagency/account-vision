from django.conf.urls import url, include
from .views import *

urlpatterns = [
    url(r'^compose/$', MessageComposeView.as_view(), name='messages_compose'),
    url(r'^reply/(?P<message_id>[\d]+)/$', MessageReplyView.as_view(), name='messages_reply'),
    
    url(r'^', include('django_messages.urls')),
]