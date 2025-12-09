from django.apps import AppConfig


class TelegramConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram'
    
    def ready(self):
        """Подключаем сигналы при запуске приложения"""
        import telegram.signals  # noqa