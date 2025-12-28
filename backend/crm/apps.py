from django.apps import AppConfig


class CrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm'
    
    def ready(self):
        # Импортируем сигналы только если приложение полностью загружено
        # и миграции применены
        try:
            import crm.signals  # noqa
        except Exception as e:
            # Игнорируем ошибки при загрузке сигналов (например, при применении миграций)
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f'Не удалось загрузить сигналы CRM: {e}')