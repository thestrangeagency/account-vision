from django.apps import AppConfig


class AccountAppConfig(AppConfig):
    name = 'av_account'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('AvUser'))
        registry.register(self.get_model('Address'))
        registry.register(self.get_model('Bank'))
        import av_account.signals
