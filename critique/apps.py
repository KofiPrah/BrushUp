from django.apps import AppConfig


class CritiqueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'critique'
    
    def ready(self):
        """
        Import signals when Django starts to ensure they're registered properly.
        This will connect all signal handlers defined in the signals.py file.
        """
        import critique.signals  # noqa
