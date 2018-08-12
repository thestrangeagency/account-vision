from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string

from av_core import settings, logger


def send_new_message_email(message):
    send_email(
        subject='Account Vision: You have a new message',
        recipient=message.recipient.email,
        context={'message': message, 'user': message.recipient},
        template='av_emails/new_message.html',
    )


def send_new_user_email(user):
    send_email(
        subject='Welcome to Account Vision!',
        recipient=user.email,
        context={'user': user},
        template='av_emails/new_user.html',
    )


def send_untrusted_device_email(user, ip):
    send_email(
        subject='Account Vision untrusted device login',
        recipient=user.email,
        context={'user': user, 'ip': ip},
        template='av_emails/untrusted_device.html',
    )


def send_verification_email(user):
    send_email(
        subject='Welcome to Account Vision - email verification',
        recipient=user.email,
        context={'user': user},
        template='av_emails/verification.html',
    )


def send_invitation_email(user):
    send_email(
        subject='Welcome to Account Vision',
        recipient=user.email,
        context={'user': user},
        template='av_emails/invitation.html',
    )


def send_team_invitation_email(user):
    send_email(
        subject='Welcome to Account Vision',
        recipient=user.email,
        context={'user': user},
        template='av_emails/team_invitation.html',
    )
    

def send_return_update_email(tax_return, state_changed=None):
    if tax_return.cpa is not None:
        send_email(
            subject='A return you are managing was updated',
            recipient=tax_return.cpa.email,
            context={'user': tax_return.user, 'return': tax_return, 'state_changed': state_changed},
            template='av_emails/return_update.html',
        )


def send_new_contact_email(contact):
    send_email(
        subject='New contact form message',
        recipient=settings.DEFAULT_CONTACT,
        context={'contact': contact},
        template='av_emails/new_contact.html',
    )


def send_payment_email(user):
    send_email(
        subject='Payment Received',
        recipient=user.email,
        context={'user': user},
        template='av_emails/payment.html',
    )


def send_abandoned_email(user):
    send_email(
        subject='Almost Ready!',
        recipient=user.email,
        context={'user': user},
        template='av_emails/abandoned.html',
    )


def send_return_complete_email(user, year):
    send_email(
        subject='Your Account Vision tax return is ready for review',
        recipient=user.email,
        context={'user': user, 'year': year},
        template='av_emails/complete.html',
    )


def send_new_upload_email(user, year):
    send_email(
        subject='Account Vision New Upload',
        recipient=user.email,
        context={'user': user, 'year': year},
        template='av_emails/new_upload.html',
    )


def send_return_filed_email(user, year):
    send_email(
        subject='Your Account Vision tax return has been E-Filed!',
        recipient=user.email,
        context={'user': user, 'year': year},
        template='av_emails/filed.html',
    )


def send_trial_end_email(user, plan, amount):
    send_email(
        subject='Your Account Vision Trial',
        recipient=user.email,
        context={'user': user, 'plan': plan, 'amount': amount},
        template='av_emails/trial_end.html',
    )


def send_trial_final_email(user, plan, amount):
    send_email(
        subject='Your Account Vision Trial',
        recipient=user.email,
        context={'user': user, 'plan': plan, 'amount': amount},
        template='av_emails/trial_final.html',
    )

# ------------------------------------------------------------------------------------------


def get_url():
    default_protocol = getattr(settings, 'DEFAULT_HTTP_PROTOCOL', 'http')
    current_domain = Site.objects.get_current().domain
    return '%s://%s' % (default_protocol, current_domain)


def send_email(subject="Account Vision", recipient=None, context=None, template='av_emails/base.html'):

    if context is None:
        context = {}

    context['site_url'] = get_url()
    context['recipient'] = recipient
    message = render_to_string(template_name=template, context=context)

    try:
        if not settings.MAIL_OFF:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient, ], html_message=message)
        if not settings.TESTING:
            logger.info('sent from:{} to:{} subject:{}'.format(settings.DEFAULT_FROM_EMAIL, recipient, subject))
    except Exception as e:
        logger.warn('Email send failure')
        logger.warn(e)
        logger.info(message)
