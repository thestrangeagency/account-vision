# based on https://github.com/azavea/django-amazon-ses
"""Boto3 email backend class for Amazon SES."""
import boto3

from botocore.exceptions import ClientError

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address
from django.dispatch import Signal

pre_send = Signal(providing_args=['message'])
post_send = Signal(providing_args=['message', 'message_id'])


class EmailBackend(BaseEmailBackend):
    """An email backend for use with Amazon SES.

    Attributes:
        conn: A client connection for Amazon SES.
    """
    def __init__(self, fail_silently=False, **kwargs):
        """Creates a client for the Amazon SES API.

        Args:
            fail_silently: Flag that determines whether Amazon SES
                client errors should throw an exception.

        """
        super(EmailBackend, self).__init__(fail_silently=fail_silently)

        self.conn = boto3.client(
            'ses',
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_SES_REGION,
        )

    def send_messages(self, email_messages):
        """Sends one or more EmailMessage objects and returns the
        number of email messages sent.

        Args:
            email_messages: A list of Django EmailMessage objects.
        Returns:
            An integer count of the messages sent.
        Raises:
            ClientError: An interaction with the Amazon SES HTTP API
                failed.
        """
        if not email_messages:
            return

        sent_message_count = 0

        for email_message in email_messages:
            if self._send(email_message):
                sent_message_count += 1
        return sent_message_count

    def _send(self, email_message):
        """Sends an individual message via the Amazon SES HTTP API.

        Args:
            email_message: A single Django EmailMessage object.
        Returns:
            True if the EmailMessage was sent successfully, otherwise False.
        Raises:
            ClientError: An interaction with the Amazon SES HTTP API
                failed.
        """
        pre_send.send(self.__class__, message=email_message)

        if not email_message.recipients():
            return False

        from_email = sanitize_address(email_message.from_email,
                                      email_message.encoding)
        recipients = [sanitize_address(addr, email_message.encoding)
                      for addr in email_message.recipients()]
        message = email_message.message().as_bytes(linesep='\r\n')

        try:
            result = self.conn.send_raw_email(
                Source=from_email,
                Destinations=recipients,
                RawMessage={
                    'Data': message
                }
            )
            message_id = result['MessageId']
            post_send.send(
                self.__class__,
                message=email_message,
                message_id=message_id
            )
        except ClientError:
            if not self.fail_silently:
                raise
            return False
        return True
