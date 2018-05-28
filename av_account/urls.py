from django.conf.urls import url
from django.contrib.auth.views import logout, PasswordResetDoneView, PasswordResetView, PasswordResetConfirmView, \
    PasswordResetCompleteView, PasswordChangeView

from av_account.forms import AccountPasswordResetForm, AccountSetPasswordForm, AccountLoginForm, \
    AccountPasswordChangeForm
from .views import *

urlpatterns = [

    # cpa registration flow
    url(
        regex=r'^register/$',
        view=RegistrationView.as_view(),
        name='register',
    ),
    url(
        regex=r'^questions/$',
        view=SecurityQuestionsView.as_view(),
        name='questions',
    ),
    url(
        regex=r'^phone/$',
        view=PhoneNumberView.as_view(),
        name='phone',
    ),
    url(
        regex=r'^verification/$',
        view=VerificationView.as_view(),
        name='verification',
    ),
    url(
        regex=r'^firm/$',
        view=FirmView.as_view(),
        name='firm',
    ),
    url(
        regex=r'^finished/$',
        view=TemplateView.as_view(template_name='cpa_created.html'),
        name='cpa_created',
    ),
    url(
        regex=r'^confirmation/(?P<code>[\w{}.-]{16})/$',
        view=EmailVerificationView.as_view(),
        name='confirmation',
    ),

    # new user invitations
    url(
        regex=r'^invitation/(?P<code>[\w{}.-]{16})/$',
        view=InvitationView.as_view(),
        name='invitation',
    ),
    url(
        regex=r'^done/$',
        view=TemplateView.as_view(template_name='client_created.html'),
        name='client_created',
    ),

    # account maintenance
    url(
        regex=r'^new-device/$',
        view=TrustView.as_view(),
        name='trust',
    ),
    url(
        regex=r'^new-email/$',
        view=NewEmailView.as_view(),
        name='email_verify',
    ),
    url(
        regex=r'^edit/$',
        view=EditView.as_view(),
        name='edit',
    ),
    url(
        regex=r'^logins/$',
        view=LoginsView.as_view(),
        name='logins',
    ),
    url(
        regex=r'^devices/$',
        view=DevicesView.as_view(),
        name='devices',
    ),
    url(
        regex=r'^banking-info/$',
        view=BankingView.as_view(),
        name='banking',
    ),
    url(
        regex=r'^disabled/$',
        view=NotReadyView.as_view(),
        name='disabled',
    ),

    url(r'^login/$', LoginView.as_view(template_name='login.html', form_class=AccountLoginForm), name='login'),
    url(r'^logout/$', logout, name='logout'),

    url(r'^password_change/$', PasswordChangeView.as_view(template_name='password_change.html', form_class=AccountPasswordChangeForm, success_url=reverse_lazy('edit')), name='password_change'),

    url(r'^password_reset/$', PasswordResetView.as_view(template_name='password_reset.html', form_class=AccountPasswordResetForm), name='password_reset'),
    url(r'^password_reset/done/$', PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),

    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', PasswordResetConfirmView.as_view(template_name='password_new.html', form_class=AccountSetPasswordForm), name='password_reset_confirm'),
    url(r'^reset/done/$', PasswordResetCompleteView.as_view(template_name='password_new_complete.html'), name='password_reset_complete'),
]
