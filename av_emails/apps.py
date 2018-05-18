from django.apps import AppConfig


class EmailAppConfig(AppConfig):
    name = 'av_emails'

    def ready(self):
        import av_emails.signals
