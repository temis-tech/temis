from django.db import models
from django.utils import timezone


class TelegramBotSettings(models.Model):
    """Настройки Telegram бота"""
    token = models.CharField('Токен бота', max_length=200, 
                            default='8576779956:AAEmqm1yQmtO06aiXdcdUfi-H4ZKqecbZBo',
                            help_text='Токен бота от @BotFather')
    is_active = models.BooleanField('Активен', default=True,
                                   help_text='Включить/выключить бота')
    
    # Настройки уведомлений
    notify_on_quiz = models.BooleanField('Уведомлять при прохождении анкеты', default=True)
    notify_on_booking = models.BooleanField('Уведомлять при новой записи', default=True)
    notify_on_banner_start = models.BooleanField('Уведомлять при начале отображения баннера', default=True)
    notify_on_banner_end = models.BooleanField('Уведомлять при завершении отображения баннера', default=True)
    
    webhook_url = models.CharField('URL webhook', max_length=500, blank=True,
                                  help_text='URL для webhook (заполняется автоматически)')
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Настройки Telegram бота'
        verbose_name_plural = 'Настройки Telegram бота'

    def __str__(self):
        return 'Настройки Telegram бота'
    
    def save(self, *args, **kwargs):
        # Разрешаем только одну запись
        self.pk = 1
        super().save(*args, **kwargs)


class TelegramUser(models.Model):
    """Пользователь Telegram бота"""
    telegram_id = models.BigIntegerField('Telegram ID', unique=True,
                                         help_text='ID пользователя в Telegram')
    username = models.CharField('Username', max_length=100, blank=True,
                               help_text='Username пользователя в Telegram')
    first_name = models.CharField('Имя', max_length=200, blank=True)
    last_name = models.CharField('Фамилия', max_length=200, blank=True)
    is_admin = models.BooleanField('Админ', default=False,
                                  help_text='Получает уведомления от бота')
    is_active = models.BooleanField('Активен', default=True,
                                   help_text='Активен ли пользователь')
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Пользователь Telegram'
        verbose_name_plural = 'Пользователи Telegram'
        ordering = ['-created_at']

    def __str__(self):
        name = self.first_name or self.username or f'User {self.telegram_id}'
        admin_status = ' (Админ)' if self.is_admin else ''
        return f'{name}{admin_status}'
    
    def get_full_name(self):
        """Возвращает полное имя пользователя"""
        parts = [self.first_name, self.last_name]
        return ' '.join(filter(None, parts)) or self.username or f'User {self.telegram_id}'
