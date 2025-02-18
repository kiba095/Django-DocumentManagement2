from django.apps import AppConfig


class MediaappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mediaapp'
    #name = 'frontend'
    verbose_name = "Document Management"

    def ready(self):
        import mediaapp.signals