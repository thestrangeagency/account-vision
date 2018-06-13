from django.apps import AppConfig


class UploadsAppConfig(AppConfig):
    name = 'av_uploads'
    
    def ready(self):
        from actstream import registry
        registry.register(self.get_model('S3File'))
        import av_uploads.signals
