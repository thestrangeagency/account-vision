from .views import *
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.contrib.flatpages import views

urlpatterns = [

    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),

    url(r'^admin/', admin.site.urls),
    url(r'^login_redirect/$', login_redirect, name='login_redirect'),
    url(r'^force_trust/$', force_trust, name='force_trust'),
    url(r'^(?P<url>.*/)$', views.flatpage),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
