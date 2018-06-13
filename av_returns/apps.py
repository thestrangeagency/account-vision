from django.apps import AppConfig


class ReturnsAppConfig(AppConfig):
    name = 'av_returns'
    
    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Return'))
        registry.register(self.get_model('Spouse'))
        registry.register(self.get_model('Dependent'))
        registry.register(self.get_model('Expense'))
        import av_returns.signals
