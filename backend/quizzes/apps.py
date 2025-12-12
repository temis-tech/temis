from django.apps import AppConfig


class QuizzesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quizzes'
    
    def ready(self):
        """Подключаем сигналы при запуске приложения"""
        import quizzes.signals  # noqa
    verbose_name = 'Анкеты'  # Группировка в админке
