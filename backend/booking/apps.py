from django.apps import AppConfig


class BookingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'booking'
    verbose_name = 'Запись на услуги'  # Группировка в админке
    
    def ready(self):
        """Подключаем сигналы при запуске приложения"""
        import booking.signals  # noqa