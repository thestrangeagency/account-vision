from django.conf.urls import url
from .views import *

urlpatterns = [
    url(
        regex=r'^terms/$',
        view=TermsView.as_view(),
        name='terms',
    ),
    url(
        regex=r'^checkout/$',
        view=CheckoutView.as_view(),
        name='checkout',
    ),
    url(
        regex=r'^ready/$',
        view=TemplateView.as_view(template_name='av_payment/ready.html'),
        name='ready',
    ),
    url(
        regex=r'^error/$',
        view=TemplateView.as_view(template_name='av_payment/error.html'),
        name='error',
    ),
]
