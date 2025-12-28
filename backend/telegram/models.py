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
    
    # Настройки синхронизации с каналом
    sync_channel_enabled = models.BooleanField('Включить синхронизацию с каналом', default=False,
                                              help_text='Автоматически создавать элементы каталога из постов в Telegram канале')
    channel_username = models.CharField('Username канала', max_length=200, blank=True,
                                       help_text='Username канала (например, @channel_name) или ID канала (например, -1001234567890). Бот должен быть администратором канала.')
    channel_id = models.CharField('ID канала', max_length=100, blank=True,
                                 help_text='ID канала (заполняется автоматически при первой синхронизации)')
    catalog_page = models.ForeignKey('content.ContentPage', on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='telegram_sync_sources',
                                     verbose_name='Страница каталога',
                                     help_text='Страница каталога, в которую будут создаваться элементы из постов Telegram. Если не указана, элементы не будут создаваться.',
                                     limit_choices_to={'page_type': 'catalog', 'is_active': True})
    
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


class TelegramHashtagMapping(models.Model):
    """Настройка сопоставления хештега с каталогом и параметрами элемента"""
    # Константы для выбора (дублируем из CatalogItem, чтобы избежать циклических импортов)
    WIDTH_CHOICES = [
        ('narrow', 'Узкая (1/3 ширины)'),
        ('medium', 'Средняя (1/2 ширины)'),
        ('wide', 'Широкая (2/3 ширины)'),
        ('full', 'На всю ширину'),
    ]
    
    BUTTON_TYPES = [
        ('booking', 'Запись'),
        ('quiz', 'Анкета'),
        ('external', 'Внешняя ссылка'),
        ('none', 'Без кнопки'),
    ]
    
    IMAGE_POSITION_CHOICES = [
        ('top', 'Сверху'),
        ('bottom', 'Снизу'),
        ('left', 'Слева'),
        ('right', 'Справа'),
        ('none', 'Не отображать'),
    ]
    
    hashtag = models.CharField('Хештег', max_length=100, unique=True,
                               help_text='Хештег из поста Telegram (например, новости, статья). Без символа #')
    catalog_page = models.ForeignKey('content.ContentPage', on_delete=models.CASCADE,
                                     related_name='hashtag_mappings',
                                     verbose_name='Страница каталога',
                                     help_text='Страница каталога, в которую будут создаваться элементы из постов с этим хештегом',
                                     limit_choices_to={'page_type': 'catalog', 'is_active': True})
    
    # Настройки элемента каталога
    width = models.CharField('Ширина элемента', max_length=10, 
                            choices=WIDTH_CHOICES, 
                            default='medium',
                            help_text='Ширина элемента в сетке каталога')
    
    has_own_page = models.BooleanField('Может быть открыт как страница', default=True,
                                      help_text='Если включено, карточка будет иметь свой URL и может быть открыта как отдельная страница')
    
    button_type = models.CharField('Тип кнопки', max_length=20, 
                                   choices=BUTTON_TYPES, 
                                   default='none',
                                   help_text='Тип кнопки для элемента каталога')
    
    button_text = models.CharField('Текст кнопки', max_length=100, blank=True, default='',
                                  help_text='Текст кнопки (если тип кнопки не "Без кнопки")')
    
    button_booking_form = models.ForeignKey('booking.BookingForm', on_delete=models.SET_NULL, 
                                           null=True, blank=True,
                                           verbose_name='Форма записи',
                                           help_text='Выберите форму записи (если тип кнопки - "Запись")',
                                           limit_choices_to={'is_active': True})
    
    button_quiz = models.ForeignKey('quizzes.Quiz', on_delete=models.SET_NULL, 
                                   null=True, blank=True,
                                   verbose_name='Анкета',
                                   help_text='Выберите анкету (если тип кнопки - "Анкета")',
                                   limit_choices_to={'is_active': True})
    
    button_external_url = models.URLField('Внешняя ссылка', blank=True, null=True,
                                          help_text='Внешняя ссылка (если тип кнопки - "Внешняя ссылка")')
    
    is_active = models.BooleanField('Активен', default=True,
                                    help_text='Если выключено, элементы с этим хештегом не будут создаваться')
    
    order = models.IntegerField('Порядок', default=0,
                                help_text='Порядок сортировки элементов в каталоге (0 - в конец)')
    
    # Настройки разделения текста
    preview_separator = models.CharField('Разделитель текста', max_length=10, blank=True, default='',
                                        help_text='Символ или текст для разделения превью и полного текста (например, "---" или "<!--more-->"). Если указан, текст до разделителя пойдет в карточку, после - в полный текст. Если не указан, будет использовано автоматическое обрезание.')
    preview_length = models.IntegerField('Длина превью (символов)', default=200, null=True, blank=True,
                                        help_text='Максимальная длина текста для карточки превью. Используется только если не указан разделитель. По умолчанию: 200 символов.')
    
    # Настройки изображения на странице элемента
    image_position = models.CharField('Позиция изображения на странице', max_length=10, 
                                     choices=IMAGE_POSITION_CHOICES, 
                                     default='top',
                                     help_text='Где отображать изображение на странице элемента: сверху, снизу, слева, справа или не отображать')
    image_target_width = models.IntegerField('Целевая ширина изображения (px)', null=True, blank=True,
                                             help_text='Ширина, к которой будет приведено изображение. Изображение будет вписано в этот размер с сохранением пропорций, центрировано. Если не указано, используется размер по умолчанию.')
    image_target_height = models.IntegerField('Целевая высота изображения (px)', null=True, blank=True,
                                              help_text='Высота, к которой будет приведено изображение. Изображение будет вписано в этот размер с сохранением пропорций, центрировано. Если не указано, используется размер по умолчанию.')
    
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        verbose_name = 'Настройка хештега'
        verbose_name_plural = 'Настройки хештегов'
        ordering = ['hashtag']
        app_label = 'telegram'
    
    def __str__(self):
        return f'#{self.hashtag} → {self.catalog_page.title}'


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


class TelegramSyncLog(models.Model):
    """Логи синхронизации с Telegram каналом"""
    
    EVENT_TYPE_CHOICES = [
        ('webhook_received', 'Webhook получен'),
        ('channel_post', 'Пост из канала'),
        ('edited_channel_post', 'Пост отредактирован'),
        ('catalog_item_created', 'Элемент каталога создан'),
        ('catalog_item_updated', 'Элемент каталога обновлен'),
        ('catalog_item_deactivated', 'Элемент каталога деактивирован'),
        ('error', 'Ошибка'),
        ('warning', 'Предупреждение'),
        ('info', 'Информация'),
    ]
    
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('error', 'Ошибка'),
        ('warning', 'Предупреждение'),
        ('skipped', 'Пропущено'),
    ]
    
    event_type = models.CharField('Тип события', max_length=50, choices=EVENT_TYPE_CHOICES)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='success')
    
    # Информация о Telegram посте
    message_id = models.BigIntegerField('ID сообщения Telegram', null=True, blank=True)
    chat_id = models.CharField('ID канала', max_length=100, blank=True)
    chat_username = models.CharField('Username канала', max_length=200, blank=True)
    
    # Информация о хештегах
    hashtags = models.CharField('Хештеги', max_length=500, blank=True,
                                help_text='Хештеги из поста (через запятую)')
    
    # Информация о созданном/обновленном элементе
    catalog_item = models.ForeignKey('content.CatalogItem', on_delete=models.SET_NULL, 
                                    null=True, blank=True,
                                    verbose_name='Элемент каталога',
                                    related_name='telegram_sync_logs')
    catalog_item_title = models.CharField('Название элемента', max_length=500, blank=True)
    
    # Детали события
    message = models.TextField('Сообщение', blank=True,
                              help_text='Детальное описание события')
    error_details = models.TextField('Детали ошибки', blank=True,
                                    help_text='Детали ошибки, если произошла')
    
    # Метаданные
    raw_data = models.JSONField('Исходные данные', null=True, blank=True,
                               help_text='Исходные данные из Telegram (для отладки)')
    
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Лог синхронизации Telegram'
        verbose_name_plural = 'Логи синхронизации Telegram'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['event_type', 'status']),
            models.Index(fields=['message_id']),
            models.Index(fields=['chat_id']),
        ]
        app_label = 'telegram'
    
    def __str__(self):
        return f'{self.get_event_type_display()} - {self.get_status_display()} ({self.created_at.strftime("%Y-%m-%d %H:%M:%S")})'
    
    def get_status_color(self):
        """Возвращает цвет для отображения статуса"""
        colors = {
            'success': '#28a745',
            'error': '#dc3545',
            'warning': '#ffc107',
            'skipped': '#6c757d',
        }
        return colors.get(self.status, '#6c757d')
