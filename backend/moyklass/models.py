from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class MoyKlassSettings(models.Model):
    """Настройки интеграции с MoyKlass CRM"""
    
    # API настройки
    api_key = models.CharField(
        'API ключ',
        max_length=200,
        help_text='API ключ из раздела "Настройки - API" в MoyKlass'
    )
    access_token = models.CharField(
        'Токен доступа',
        max_length=500,
        blank=True,
        help_text='Автоматически обновляется при работе'
    )
    token_expires_at = models.DateTimeField(
        'Токен действителен до',
        null=True,
        blank=True,
        help_text='Автоматически обновляется'
    )
    
    # Настройки синхронизации
    is_active = models.BooleanField('Интеграция активна', default=True)
    auto_sync_enabled = models.BooleanField(
        'Автоматическая синхронизация',
        default=False,
        help_text='Автоматически синхронизировать данные с MoyKlass'
    )
    sync_interval_minutes = models.IntegerField(
        'Интервал синхронизации (минуты)',
        default=60,
        validators=[MinValueValidator(5), MaxValueValidator(1440)],
        help_text='Как часто синхронизировать данные (минимум 5 минут)'
    )
    last_sync_at = models.DateTimeField(
        'Последняя синхронизация',
        null=True,
        blank=True
    )
    
    # Настройки синхронизации данных
    sync_students = models.BooleanField('Синхронизировать учеников', default=True)
    sync_payments = models.BooleanField('Синхронизировать платежи', default=True)
    sync_bookings = models.BooleanField('Синхронизировать записи', default=True)
    sync_groups = models.BooleanField('Синхронизировать группы', default=False)
    sync_lessons = models.BooleanField('Синхронизировать занятия', default=False)
    
    # Настройки вебхуков
    webhook_enabled = models.BooleanField(
        'Включить вебхуки',
        default=False,
        help_text='Получать уведомления от MoyKlass о событиях'
    )
    webhook_url = models.URLField(
        'URL для вебхуков',
        blank=True,
        help_text='URL для получения вебхуков от MoyKlass'
    )
    
    # Логирование
    log_requests = models.BooleanField(
        'Логировать запросы',
        default=True,
        help_text='Сохранять логи всех запросов к API'
    )
    
    # Настройки тегов
    website_tag_name = models.CharField(
        'Название тега для лидов с сайта',
        max_length=200,
        default='Пришел с сайта',
        help_text='Тег, который будет автоматически присваиваться лидам, созданным с сайта. Можно выбрать из списка тегов MoyKlass или ввести свой.'
    )
    website_tag_id = models.IntegerField(
        'ID тега для лидов с сайта',
        null=True,
        blank=True,
        help_text='ID тега в MoyKlass (заполняется автоматически при выборе тега)'
    )
    
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    
    class Meta:
        verbose_name = 'Настройки MoyKlass'
        verbose_name_plural = 'Настройки MoyKlass'
    
    def __str__(self):
        return f'MoyKlass интеграция ({self.api_key[:10]}...)' if self.api_key else 'MoyKlass интеграция'
    
    def save(self, *args, **kwargs):
        # Разрешаем только одну запись настроек
        self.pk = 1
        super().save(*args, **kwargs)
    
    def is_token_valid(self):
        """Проверяет, действителен ли токен"""
        if not self.access_token or not self.token_expires_at:
            return False
        return timezone.now() < self.token_expires_at


class MoyKlassSyncLog(models.Model):
    """Лог синхронизации с MoyKlass"""
    
    SYNC_TYPES = [
        ('students', 'Ученики'),
        ('payments', 'Платежи'),
        ('bookings', 'Записи'),
        ('groups', 'Группы'),
        ('lessons', 'Занятия'),
        ('full', 'Полная синхронизация'),
    ]
    
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('error', 'Ошибка'),
        ('partial', 'Частично'),
    ]
    
    sync_type = models.CharField('Тип синхронизации', max_length=20, choices=SYNC_TYPES)
    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES)
    records_processed = models.IntegerField('Обработано записей', default=0)
    records_created = models.IntegerField('Создано записей', default=0)
    records_updated = models.IntegerField('Обновлено записей', default=0)
    records_errors = models.IntegerField('Ошибок', default=0)
    error_message = models.TextField('Сообщение об ошибке', blank=True)
    started_at = models.DateTimeField('Начало', auto_now_add=True)
    finished_at = models.DateTimeField('Окончание', null=True, blank=True)
    duration_seconds = models.FloatField('Длительность (сек)', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Лог синхронизации'
        verbose_name_plural = 'Логи синхронизации'
        ordering = ['-started_at']
    
    def __str__(self):
        return f'{self.get_sync_type_display()} - {self.get_status_display()} ({self.started_at})'


class MoyKlassRequestLog(models.Model):
    """Лог запросов к API MoyKlass"""
    
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH'),
    ]
    
    method = models.CharField('Метод', max_length=10, choices=METHOD_CHOICES)
    endpoint = models.CharField('Endpoint', max_length=500)
    request_data = models.TextField('Данные запроса', blank=True)
    response_status = models.IntegerField('Статус ответа', null=True, blank=True)
    response_data = models.TextField('Данные ответа', blank=True)
    error_message = models.TextField('Ошибка', blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    duration_ms = models.FloatField('Длительность (мс)', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Лог запроса'
        verbose_name_plural = 'Логи запросов'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['endpoint']),
        ]
    
    def __str__(self):
        return f'{self.method} {self.endpoint} - {self.response_status or "Error"} ({self.created_at})'


class MoyKlassIntegration(models.Model):
    """Настройка интеграции для конкретной анкеты или формы записи"""
    
    SOURCE_TYPE_CHOICES = [
        ('booking_form', 'Форма записи'),
        ('quiz', 'Анкета'),
    ]
    
    source_type = models.CharField(
        'Тип источника',
        max_length=20,
        choices=SOURCE_TYPE_CHOICES
    )
    booking_form = models.ForeignKey(
        'booking.BookingForm',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Форма записи',
        related_name='moyklass_integrations'
    )
    quiz = models.ForeignKey(
        'quizzes.Quiz',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Анкета',
        related_name='moyklass_integrations'
    )
    is_active = models.BooleanField('Активна', default=True)
    order = models.IntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    
    class Meta:
        verbose_name = 'Интеграция с MoyKlass'
        verbose_name_plural = 'Интеграции с MoyKlass'
        ordering = ['order', 'id']
    
    def __str__(self):
        if self.booking_form:
            return f'Форма записи: {self.booking_form.title}'
        elif self.quiz:
            return f'Анкета: {self.quiz.title}'
        return f'Интеграция #{self.id}'
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.source_type == 'booking_form' and not self.booking_form:
            raise ValidationError('Для типа "Форма записи" необходимо выбрать форму')
        if self.source_type == 'quiz' and not self.quiz:
            raise ValidationError('Для типа "Анкета" необходимо выбрать анкету')
        if self.source_type == 'booking_form' and self.quiz:
            raise ValidationError('Нельзя указывать анкету для формы записи')
        if self.source_type == 'quiz' and self.booking_form:
            raise ValidationError('Нельзя указывать форму записи для анкеты')
    
    def get_source_fields(self):
        """Возвращает список полей источника (формы или анкеты)"""
        if self.booking_form:
            return self.booking_form.fields.all()
        elif self.quiz:
            return self.quiz.questions.all()
        return []


class MoyKlassFieldMapping(models.Model):
    """Маппинг полей формы/анкеты на поля MoyKlass"""
    
    MOYKLASS_FIELD_CHOICES = [
        ('name', 'Имя'),
        ('phone', 'Телефон'),
        ('email', 'Email'),
        ('comment', 'Комментарий'),
        ('birthday', 'Дата рождения'),
        ('address', 'Адрес'),
        ('city', 'Город'),
        ('country', 'Страна'),
        ('note', 'Заметка'),
    ]
    
    integration = models.ForeignKey(
        MoyKlassIntegration,
        on_delete=models.CASCADE,
        related_name='field_mappings',
        verbose_name='Интеграция'
    )
    moyklass_field = models.CharField(
        'Поле в MoyKlass',
        max_length=50,
        choices=MOYKLASS_FIELD_CHOICES
    )
    source_field_name = models.CharField(
        'Имя поля в источнике',
        max_length=100,
        help_text='Имя поля (name) из формы записи или ID вопроса из анкеты'
    )
    source_field_label = models.CharField(
        'Название поля в источнике',
        max_length=200,
        blank=True,
        help_text='Для отображения в админке'
    )
    is_required = models.BooleanField(
        'Обязательное',
        default=False,
        help_text='Если поле не заполнено, лид не будет создан'
    )
    default_value = models.CharField(
        'Значение по умолчанию',
        max_length=500,
        blank=True,
        help_text='Используется, если поле не заполнено'
    )
    order = models.IntegerField('Порядок', default=0)
    
    class Meta:
        verbose_name = 'Маппинг поля'
        verbose_name_plural = 'Маппинги полей'
        ordering = ['order', 'id']
        unique_together = [['integration', 'moyklass_field']]
    
    def save(self, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        # Автоматически заполняем source_field_label, если он пустой
        if not self.source_field_label and self.integration:
            logger.debug(f'MoyKlassFieldMapping.save: определение label для поля {self.source_field_name}, интеграция {self.integration.id}')
            if self.integration.source_type == 'booking_form' and self.integration.booking_form:
                try:
                    field = self.integration.booking_form.fields.get(name=self.source_field_name)
                    self.source_field_label = field.label
                    logger.debug(f'MoyKlassFieldMapping.save: найден label "{field.label}" для поля {self.source_field_name}')
                except Exception as e:
                    logger.warning(f'MoyKlassFieldMapping.save: не удалось найти поле {self.source_field_name} в форме {self.integration.booking_form.id}: {e}')
                    pass
            elif self.integration.source_type == 'quiz' and self.integration.quiz:
                if self.source_field_name == 'user_name':
                    self.source_field_label = 'Имя пользователя'
                elif self.source_field_name == 'user_phone':
                    self.source_field_label = 'Телефон пользователя'
                elif self.source_field_name == 'user_email':
                    self.source_field_label = 'Email пользователя'
                elif self.source_field_name.startswith('question_'):
                    try:
                        question_id = int(self.source_field_name.replace('question_', ''))
                        question = self.integration.quiz.questions.get(id=question_id)
                        self.source_field_label = question.text[:100]
                    except:
                        pass
        super().save(*args, **kwargs)
    
    def __str__(self):
        source_name = self.source_field_label or self.source_field_name
        return f'{self.get_moyklass_field_display()} ← {source_name}'
