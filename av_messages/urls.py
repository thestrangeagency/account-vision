from django.conf.urls import url, include
from .views import *

urlpatterns = [
    url(r'^inbox/$', MessageInboxView.as_view(), name='messages_inbox'),
    url(r'^compose/$', MessageComposeView.as_view(), name='messages_compose'),
    url(r'^reply/(?P<message_id>[\d]+)/$', MessageReplyView.as_view(), name='messages_reply'),
    url(r'^trash/$', MessageTrashView.as_view(), name='messages_trash'),
    
    url(r'^', include('django_messages.urls')),
]