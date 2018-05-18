from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.flatpages import views
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views.generic import TemplateView
from django_agent_trust import trust_agent

from av_core import settings


@login_required
def login_redirect(request):
    if request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    else:
        return HttpResponseRedirect(reverse('returns'))


def force_trust(request):
    """
    Used only during testing to trust test user agent
    """
    if settings.TESTING:
        trust_agent(request)
        return HttpResponse('ok')
    else:
        return HttpResponseRedirect(reverse('home'))


urlpatterns = [

    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),

    url(r'^account/', include('av_account.urls')),

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
