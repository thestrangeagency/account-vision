from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.flatpages import views
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views.generic import TemplateView
from django_agent_trust import trust_agent
from rest_framework import routers

from av_account.api import UserViewSet
from av_contact.views import ContactView
from av_core import settings
from av_core.views import HomeView, ClientHomeView, CpaHomeView
from av_returns.api import ExpenseViewSet, CommonExpenseViewSet, ReturnViewSet
from av_uploads.views import UploadParamsView, UploadSignatureView, UploadCompleteView, FileViewSet, CpaFileViewSet, \
    DownloadsViewSet


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


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'returns', ReturnViewSet)
router.register(r'returns/(?P<year>[0-9]{4})/files', FileViewSet)
router.register(r'returns/(?P<year>[0-9]{4})/(?P<target>\d+)/files', CpaFileViewSet)
router.register(r'returns/(?P<year>[0-9]{4})/downloads', DownloadsViewSet, base_name='download')
router.register(r'returns/(?P<year>[0-9]{4})/expenses/custom', ExpenseViewSet)
router.register(r'returns/(?P<year>[0-9]{4})/expenses/common', CommonExpenseViewSet)


urlpatterns = [

    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^dashboard/$', CpaHomeView.as_view(), name='cpa-home'),
    url(r'^home/$', ClientHomeView.as_view(), name='client-home'),

    url(r'^account/', include('av_account.urls')),
    url(r'^profile/', include('av_profile.urls')),
    url(r'^clients/', include('av_clients.urls')),
    url(r'^years/', include('av_returns.urls')),
    url(r'^uploads/', include('av_uploads.urls')),
    url(r'^messages/', include('av_messages.urls')),
    url(r'^firm/', include('av_team.urls')),
    url(r'^payment/', include('av_payment.urls')),

    url(r'^terms/$', TemplateView.as_view(template_name='terms.html'), name='legal'),
    url(r'^privacy/$', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    url(r'^contact/$', ContactView.as_view(), name='contact'),

    url(r'^api/', include('rest_framework.urls', namespace='api')),
    url(r'^api/', include(router.urls)),

    url(r'^api/uploads/params$', UploadParamsView.as_view(), name='upload_params'),
    url(r'^api/uploads/signature$', UploadSignatureView.as_view(), name='upload_signature'),
    url(r'^api/uploads/complete', UploadCompleteView.as_view(), name='upload_complete'),

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
