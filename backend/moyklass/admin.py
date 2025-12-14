from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    MoyKlassSettings, MoyKlassSyncLog, MoyKlassRequestLog,
    MoyKlassIntegration, MoyKlassFieldMapping
)


class MoyKlassSettingsForm(forms.ModelForm):
    """Форма для настроек с выбором тега из API"""
    
    tag_choice = forms.ChoiceField(
        label='Выбрать тег из MoyKlass',
        required=False,
        choices=[],
        help_text='Выберите тег из списка доступных в MoyKlass или введите свой в поле "Название тега"'
    )
    
    class Meta:
        model = MoyKlassSettings
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Загружаем теги из API, если есть настройки
        tag_choices = [('', '--- Введите свой тег ---')]
        
        if self.instance and self.instance.pk and self.instance.is_active:
            try:
                from .client import MoyKlassClient, MoyKlassAPIError
                import logging
                logger = logging.getLogger(__name__)
                
                client = MoyKlassClient(self.instance)
                tags = client.get_tags()
                
                logger.info(f'Получено тегов из API: {len(tags)}')
                
                if tags:
                    for tag in tags:
                        if isinstance(tag, dict):
                            tag_id = tag.get('id')
                            tag_name = tag.get('name') or tag.get('title') or tag.get('label', '')
                            if tag_id and tag_name:
                                tag_choices.append((str(tag_id), f'{tag_name} (ID: {tag_id})'))
                    if len(tag_choices) == 1:
                        # Если теги не загрузились, добавляем сообщение
                        tag_choices.append(('', '⚠️ Теги не найдены. Проверьте подключение к API.'))
                else:
                    tag_choices.append(('', '⚠️ Список тегов пуст. Возможно, в MoyKlass нет тегов или endpoint недоступен.'))
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Ошибка загрузки тегов: {str(e)}', exc_info=True)
                tag_choices.append(('', f'⚠️ Ошибка загрузки тегов: {str(e)}'))
        
        self.fields['tag_choice'].choices = tag_choices
        
        # Если есть сохраненный ID тега, выбираем его
        if self.instance and self.instance.website_tag_id:
            self.fields['tag_choice'].initial = str(self.instance.website_tag_id)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Если выбран тег из списка, обновляем название и ID
        tag_choice = self.cleaned_data.get('tag_choice')
        if tag_choice:
            try:
                from .client import MoyKlassClient
                client = MoyKlassClient(instance)
                tags = client.get_tags()
                
                for tag in tags:
                    if isinstance(tag, dict) and str(tag.get('id')) == tag_choice:
                        instance.website_tag_id = tag.get('id')
                        instance.website_tag_name = tag.get('name') or tag.get('title', '')
                        break
            except Exception:
                pass
        
        if commit:
            instance.save()
        return instance


@admin.register(MoyKlassSettings)
class MoyKlassSettingsAdmin(admin.ModelAdmin):
    """Админка для настроек интеграции MoyKlass"""
    
    form = MoyKlassSettingsForm
    
    def has_add_permission(self, request):
        # Разрешаем только одну запись
        return not MoyKlassSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    list_display = ['api_key_preview', 'is_active', 'auto_sync_enabled', 'token_status', 'last_sync_display']
    readonly_fields = [
        'access_token', 'token_expires_at', 'last_sync_at',
        'created_at', 'updated_at', 'token_status_display', 'website_tag_id'
    ]
    
    fieldsets = (
        ('API Настройки', {
            'fields': ('api_key', 'is_active'),
            'description': 'Введите API ключ из раздела "Настройки - API" в MoyKlass CRM'
        }),
        ('Токен доступа', {
            'fields': ('access_token', 'token_expires_at', 'token_status_display'),
            'description': 'Токен автоматически обновляется при работе с API'
        }),
        ('Автоматическая синхронизация', {
            'fields': (
                'auto_sync_enabled',
                'sync_interval_minutes',
                'last_sync_at'
            ),
            'description': 'Настройки автоматической синхронизации данных'
        }),
        ('Типы синхронизации', {
            'fields': (
                'sync_students',
                'sync_payments',
                'sync_bookings',
                'sync_groups',
                'sync_lessons'
            ),
            'description': 'Выберите, какие данные синхронизировать с MoyKlass'
        }),
        ('Вебхуки', {
            'fields': ('webhook_enabled', 'webhook_url'),
            'description': 'Настройки для получения уведомлений от MoyKlass'
        }),
        ('Логирование', {
            'fields': ('log_requests',)
        }),
        ('Теги для лидов', {
            'fields': ('tag_choice', 'website_tag_name', 'website_tag_id'),
            'description': 'Настройка тега, который будет автоматически присваиваться лидам, созданным с сайта. Выберите тег из списка или введите свой.'
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def api_key_preview(self, obj):
        if obj.api_key:
            return format_html(
                '<code>{}</code>',
                obj.api_key[:20] + '...' if len(obj.api_key) > 20 else obj.api_key
            )
        return 'Не настроено'
    api_key_preview.short_description = 'API ключ'
    
    def token_status(self, obj):
        if obj.is_token_valid():
            expires_in = obj.token_expires_at - timezone.now()
            hours = int(expires_in.total_seconds() / 3600)
            minutes = int((expires_in.total_seconds() % 3600) / 60)
            return format_html(
                '<span style="color: green;">✓ Действителен</span><br>'
                '<small>Истекает через {}ч {}м</small>',
                hours, minutes
            )
        elif obj.access_token:
            return format_html('<span style="color: red;">✗ Истек</span>')
        return format_html('<span style="color: orange;">Не получен</span>')
    token_status.short_description = 'Статус токена'
    
    def token_status_display(self, obj):
        return self.token_status(obj)
    token_status_display.short_description = 'Статус токена'
    
    def last_sync_display(self, obj):
        if obj.last_sync_at:
            time_ago = timezone.now() - obj.last_sync_at
            if time_ago.total_seconds() < 60:
                return f'{int(time_ago.total_seconds())} сек назад'
            elif time_ago.total_seconds() < 3600:
                return f'{int(time_ago.total_seconds() / 60)} мин назад'
            else:
                return f'{int(time_ago.total_seconds() / 3600)} ч назад'
        return 'Никогда'
    last_sync_display.short_description = 'Последняя синхронизация'
    
    actions = ['test_connection', 'refresh_token_action', 'reload_tags']
    
    def test_connection(self, request, queryset):
        """Тестирует подключение к API"""
        from .client import MoyKlassClient, MoyKlassAPIError
        
        for settings in queryset:
            try:
                client = MoyKlassClient(settings)
                company_info = client.get_company_info()
                self.message_user(
                    request,
                    f'✓ Подключение успешно! Компания: {company_info.get("name", "Неизвестно")}',
                    level='SUCCESS'
                )
            except MoyKlassAPIError as e:
                self.message_user(request, f'✗ Ошибка: {str(e)}', level='ERROR')
    test_connection.short_description = 'Тестировать подключение к API'
    
    def refresh_token_action(self, request, queryset):
        """Обновляет токен доступа"""
        from .client import MoyKlassClient, MoyKlassAPIError
        
        for settings in queryset:
            try:
                client = MoyKlassClient(settings)
                client._refresh_token()
                self.message_user(request, '✓ Токен успешно обновлен', level='SUCCESS')
            except MoyKlassAPIError as e:
                self.message_user(request, f'✗ Ошибка: {str(e)}', level='ERROR')
    refresh_token_action.short_description = 'Обновить токен доступа'
    
    def reload_tags(self, request, queryset):
        """Перезагружает список тегов из API"""
        from .client import MoyKlassClient, MoyKlassAPIError
        
        for settings in queryset:
            try:
                client = MoyKlassClient(settings)
                tags = client.get_tags()
                
                if tags:
                    tags_list = []
                    for tag in tags:
                        if isinstance(tag, dict):
                            tag_id = tag.get('id')
                            tag_name = tag.get('name') or tag.get('title') or tag.get('label', '')
                            if tag_id and tag_name:
                                tags_list.append(f'{tag_name} (ID: {tag_id})')
                    
                    if tags_list:
                        self.message_user(
                            request,
                            f'✓ Загружено тегов: {len(tags_list)}\n' + '\n'.join(tags_list[:10]),
                            level='SUCCESS'
                        )
                    else:
                        self.message_user(
                            request,
                            '⚠️ Теги получены, но не удалось их распарсить',
                            level='WARNING'
                        )
                else:
                    self.message_user(
                        request,
                        '⚠️ Список тегов пуст. Возможно, в MoyKlass нет тегов или endpoint недоступен.',
                        level='WARNING'
                    )
            except MoyKlassAPIError as e:
                self.message_user(request, f'✗ Ошибка API: {str(e)}', level='ERROR')
            except Exception as e:
                self.message_user(request, f'✗ Ошибка: {str(e)}', level='ERROR')
    reload_tags.short_description = 'Перезагрузить список тегов из MoyKlass'


@admin.register(MoyKlassSyncLog)
class MoyKlassSyncLogAdmin(admin.ModelAdmin):
    """Админка для логов синхронизации"""
    
    list_display = [
        'sync_type', 'status', 'records_processed', 'records_created',
        'records_updated', 'records_errors', 'duration_display', 'started_at'
    ]
    list_filter = ['sync_type', 'status', 'started_at']
    readonly_fields = [
        'sync_type', 'status', 'records_processed', 'records_created',
        'records_updated', 'records_errors', 'error_message',
        'started_at', 'finished_at', 'duration_seconds'
    ]
    search_fields = ['error_message']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('sync_type', 'status', 'started_at', 'finished_at', 'duration_seconds')
        }),
        ('Результаты', {
            'fields': (
                'records_processed',
                'records_created',
                'records_updated',
                'records_errors'
            )
        }),
        ('Ошибки', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        if obj.duration_seconds:
            if obj.duration_seconds < 1:
                return f'{int(obj.duration_seconds * 1000)} мс'
            return f'{obj.duration_seconds:.2f} сек'
        return '-'
    duration_display.short_description = 'Длительность'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(MoyKlassRequestLog)
class MoyKlassRequestLogAdmin(admin.ModelAdmin):
    """Админка для логов запросов к API"""
    
    list_display = [
        'method', 'endpoint_short', 'response_status_display', 'duration_display', 'created_at'
    ]
    list_filter = ['method', 'response_status', 'created_at']
    readonly_fields = [
        'method', 'endpoint', 'request_data', 'response_status',
        'response_data', 'error_message', 'created_at', 'duration_ms'
    ]
    search_fields = ['endpoint', 'error_message']
    actions = ['retry_request']
    
    fieldsets = (
        ('Запрос', {
            'fields': ('method', 'endpoint', 'request_data', 'created_at', 'duration_ms'),
            'description': 'Данные запроса к API MoyKlass'
        }),
        ('Ответ', {
            'fields': ('response_status', 'response_data'),
            'description': 'Полный ответ от API MoyKlass. Если статус 400+, здесь будет детальная информация об ошибке.'
        }),
        ('Ошибка', {
            'fields': ('error_message',),
            'description': 'Сообщение об ошибке, если запрос завершился с ошибкой',
            'classes': ('collapse',)
        }),
    )
    
    def response_status_display(self, obj):
        if obj.response_status:
            if obj.response_status >= 400:
                return format_html(
                    '<span style="color: red; font-weight: bold;">{} (Ошибка)</span>',
                    obj.response_status
                )
            elif obj.response_status >= 300:
                return format_html(
                    '<span style="color: orange;">{} (Перенаправление)</span>',
                    obj.response_status
                )
            else:
                return format_html(
                    '<span style="color: green;">{} (Успешно)</span>',
                    obj.response_status
                )
        return '-'
    response_status_display.short_description = 'Статус'
    
    def endpoint_short(self, obj):
        if len(obj.endpoint) > 50:
            return obj.endpoint[:50] + '...'
        return obj.endpoint
    endpoint_short.short_description = 'Endpoint'
    
    def duration_display(self, obj):
        if obj.duration_ms:
            if obj.duration_ms < 1000:
                return f'{int(obj.duration_ms)} мс'
            return f'{obj.duration_ms / 1000:.2f} сек'
        return '-'
    duration_display.short_description = 'Длительность'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        # Показываем только последние 1000 записей для производительности
        # Используем order_by для правильной сортировки
        qs = super().get_queryset(request).order_by('-created_at')
        # Ограничиваем через фильтр по дате, если записей много
        # Но для простоты просто возвращаем queryset - Django admin сам сделает пагинацию
        return qs
    
    def retry_request(self, request, queryset):
        """Повторяет запрос для выбранных логов"""
        from .client import MoyKlassClient, MoyKlassAPIError
        from .models import MoyKlassSettings
        import json
        
        settings = MoyKlassSettings.objects.first()
        if not settings or not settings.is_active:
            self.message_user(request, 'Интеграция MoyKlass неактивна', level='ERROR')
            return
        
        success_count = 0
        error_count = 0
        
        for log in queryset:
            try:
                client = MoyKlassClient(settings)
                
                # Парсим данные запроса
                try:
                    request_data = json.loads(log.request_data) if log.request_data else {}
                except:
                    request_data = {}
                
                # Повторяем запрос
                result = client._make_request(
                    log.method,
                    log.endpoint,
                    data=request_data if log.method in ['POST', 'PUT', 'PATCH'] else None,
                    params=request_data if log.method == 'GET' else None
                )
                
                success_count += 1
                self.message_user(
                    request,
                    f'✓ Запрос {log.method} {log.endpoint} успешно повторен',
                    level='SUCCESS'
                )
            except MoyKlassAPIError as e:
                error_count += 1
                self.message_user(
                    request,
                    f'✗ Ошибка при повторении запроса {log.method} {log.endpoint}: {str(e)}',
                    level='ERROR'
                )
            except Exception as e:
                error_count += 1
                self.message_user(
                    request,
                    f'✗ Неожиданная ошибка при повторении запроса {log.method} {log.endpoint}: {str(e)}',
                    level='ERROR'
                )
        
        if success_count > 0:
            self.message_user(
                request,
                f'Успешно повторено запросов: {success_count}',
                level='SUCCESS'
            )
        if error_count > 0:
            self.message_user(
                request,
                f'Ошибок при повторении: {error_count}',
                level='WARNING'
            )
    
    retry_request.short_description = 'Повторить выбранные запросы'


class MoyKlassFieldMappingForm(forms.ModelForm):
    """Кастомная форма для маппинга полей с динамическим выбором полей источника"""
    
    class Meta:
        model = MoyKlassFieldMapping
        fields = '__all__'
        widgets = {
            'source_field_name': forms.Select(attrs={'class': 'source-field-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        import logging
        logger = logging.getLogger(__name__)
        
        # Получаем integration из instance или из initial
        integration = None
        
        # Сначала пробуем получить из instance
        if self.instance and self.instance.pk:
            integration = self.instance.integration
            logger.debug(f'MoyKlassFieldMappingForm.__init__: integration из instance.pk: {integration}')
        elif self.instance and hasattr(self.instance, 'integration_id') and self.instance.integration_id:
            from .models import MoyKlassIntegration
            try:
                integration = MoyKlassIntegration.objects.get(id=self.instance.integration_id)
                logger.debug(f'MoyKlassFieldMappingForm.__init__: integration из integration_id: {integration}')
            except MoyKlassIntegration.DoesNotExist:
                logger.warning(f'MoyKlassFieldMappingForm.__init__: integration с id={self.instance.integration_id} не найден')
        elif self.instance and hasattr(self.instance, 'integration') and self.instance.integration:
            # Для новых inline форм integration может быть установлен через form.instance.integration
            integration = self.instance.integration
            logger.debug(f'MoyKlassFieldMappingForm.__init__: integration из instance.integration: {integration}')
        
        # Если не нашли, пробуем из initial
        if not integration:
            if 'initial' in kwargs and 'integration' in kwargs['initial']:
                integration_id = kwargs['initial']['integration']
                from .models import MoyKlassIntegration
                try:
                    integration = MoyKlassIntegration.objects.get(id=integration_id)
                    logger.debug(f'MoyKlassFieldMappingForm.__init__: integration из initial: {integration}')
                except (MoyKlassIntegration.DoesNotExist, ValueError, TypeError) as e:
                    logger.warning(f'MoyKlassFieldMappingForm.__init__: ошибка получения integration из initial: {e}')
        
        if not integration:
            logger.warning(f'MoyKlassFieldMappingForm.__init__: integration не найден. instance.pk={self.instance.pk if self.instance else None}, hasattr integration={hasattr(self.instance, "integration") if self.instance else False}')
        
        # Если integration есть, заполняем choices для source_field_name
        if integration:
            choices = [('', '---------')]
            
            if integration.source_type == 'booking_form' and integration.booking_form:
                # Поля формы записи
                form_fields = integration.booking_form.fields.all().order_by('order', 'id')
                logger.debug(f'MoyKlassFieldMappingForm: форма {integration.booking_form.id}, полей найдено: {form_fields.count()}')
                if form_fields.exists():
                    for field in form_fields:
                        choices.append((
                            field.name,
                            f'{field.label} ({field.name}) - {field.get_field_type_display()}'
                        ))
                    logger.debug(f'MoyKlassFieldMappingForm: добавлено {len(choices)-1} полей в choices')
                else:
                    choices.append(('', 'В форме нет полей. Добавьте поля в форму записи.'))
                    logger.warning(f'MoyKlassFieldMappingForm: в форме {integration.booking_form.id} нет полей')
            elif integration.source_type == 'quiz' and integration.quiz:
                # Поля анкеты
                choices.append(('user_name', 'Имя пользователя (user_name)'))
                choices.append(('user_phone', 'Телефон пользователя (user_phone)'))
                choices.append(('user_email', 'Email пользователя (user_email)'))
                
                # Вопросы анкеты
                for question in integration.quiz.questions.all().order_by('order', 'id'):
                    choices.append((
                        f'question_{question.id}',
                        f'{question.text[:50]}... (question_{question.id})'
                    ))
            
            # Устанавливаем choices и делаем поле Select
            self.fields['source_field_name'].widget = forms.Select(choices=choices, attrs={'class': 'source-field-select'})
            self.fields['source_field_name'].widget.attrs['data-integration-id'] = integration.id if integration else ''
        else:
            # Если integration нет, показываем пустой список
            self.fields['source_field_name'].widget = forms.Select(
                choices=[('', 'Сначала выберите форму/анкету')],
                attrs={'class': 'source-field-select', 'disabled': True}
            )


class MoyKlassFieldMappingInline(admin.TabularInline):
    """Inline для маппинга полей"""
    model = MoyKlassFieldMapping
    form = MoyKlassFieldMappingForm
    extra = 1
    fields = ['moyklass_field', 'source_field_name', 'is_required', 'default_value', 'order']
    # Убираем source_field_label - он будет заполняться автоматически
    ordering = ['order', 'id']
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        
        # Обновляем choices для полей source_field_name
        if obj:
            original_init = formset.__init__
            
            def custom_init(self, *args, **kwargs):
                original_init(self, *args, **kwargs)
                
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f'MoyKlassFieldMappingInline.get_formset: обновление choices для интеграции {obj.id}, тип: {obj.source_type}')
                
                # Обновляем choices для каждого поля в каждой форме
                for idx, form in enumerate(self.forms):
                    if 'source_field_name' in form.fields:
                        choices = [('', '---------')]
                        
                        if obj.source_type == 'booking_form' and obj.booking_form:
                            form_fields = obj.booking_form.fields.all().order_by('order', 'id')
                            logger.debug(f'Форма {idx}: форма записи {obj.booking_form.id}, полей: {form_fields.count()}')
                            if form_fields.exists():
                                for field in form_fields:
                                    choices.append((
                                        field.name,
                                        f'{field.label} ({field.name}) - {field.get_field_type_display()}'
                                    ))
                                logger.debug(f'Форма {idx}: добавлено {len(choices)-1} полей')
                            else:
                                choices.append(('', 'В форме нет полей. Добавьте поля в форму записи.'))
                                logger.warning(f'Форма {idx}: в форме {obj.booking_form.id} нет полей')
                        elif obj.source_type == 'quiz' and obj.quiz:
                            choices.append(('user_name', 'Имя пользователя (user_name)'))
                            choices.append(('user_phone', 'Телефон пользователя (user_phone)'))
                            choices.append(('user_email', 'Email пользователя (user_email)'))
                            
                            for question in obj.quiz.questions.all().order_by('order', 'id'):
                                choices.append((
                                    f'question_{question.id}',
                                    f'{question.text[:50]}... (question_{question.id})'
                                ))
                        
                        # Обновляем choices виджета
                        widget = form.fields['source_field_name'].widget
                        widget.choices = choices
                        # Обновляем атрибуты виджета
                        if hasattr(widget, 'attrs'):
                            widget.attrs.update({
                                'class': 'source-field-select',
                                'data-integration-id': str(obj.id)
                            })
                        else:
                            widget.attrs = {
                                'class': 'source-field-select',
                                'data-integration-id': str(obj.id)
                            }
                        logger.debug(f'Форма {idx}: обновлены choices для source_field_name, всего опций: {len(choices)}')
                        
                        # Устанавливаем integration для новых форм
                        if not form.instance.pk and hasattr(form, 'instance'):
                            form.instance.integration = obj
                            # Также устанавливаем в initial для формы
                            if not hasattr(form, 'initial') or form.initial is None:
                                form.initial = {}
                            form.initial['integration'] = obj.id
                            logger.debug(f'Форма {idx}: установлена интеграция {obj.id} для нового маппинга')
            
            formset.__init__ = custom_init
        
        return formset


@admin.register(MoyKlassIntegration)
class MoyKlassIntegrationAdmin(admin.ModelAdmin):
    """Админка для интеграций с формами записи и анкетами"""
    
    list_display = ['source_type', 'source_display', 'is_active', 'mappings_count', 'order']
    list_filter = ['source_type', 'is_active', 'created_at']
    list_editable = ['is_active', 'order']
    search_fields = ['booking_form__title', 'quiz__title']
    inlines = [MoyKlassFieldMappingInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('source_type', 'booking_form', 'quiz', 'is_active', 'order')
        }),
        ('Системная информация', {
            'fields': ('form_fields_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['form_fields_display', 'created_at', 'updated_at']
    
    class Media:
        js = ('admin/js/moyklass_integration.js',)
    
    def source_display(self, obj):
        if obj.booking_form:
            return format_html('<strong>{}</strong>', obj.booking_form.title)
        elif obj.quiz:
            return format_html('<strong>{}</strong>', obj.quiz.title)
        return '-'
    source_display.short_description = 'Источник'
    
    def mappings_count(self, obj):
        count = obj.field_mappings.count()
        if count > 0:
            return format_html('<span style="color: green;">{} полей</span>', count)
        return format_html('<span style="color: orange;">Нет полей</span>')
    mappings_count.short_description = 'Маппинги'
    
    def form_fields_display(self, obj):
        """Отображает список полей формы записи или вопросов анкеты"""
        if not obj:
            return '-'
        
        fields_list = []
        
        if obj.source_type == 'booking_form' and obj.booking_form:
            form_fields = obj.booking_form.fields.all().order_by('order', 'id')
            if form_fields.exists():
                fields_list.append(format_html('<h4 style="margin-top: 0;">Поля формы записи "{}":</h4>', obj.booking_form.title))
                fields_list.append('<ul style="margin: 0; padding-left: 20px;">')
                for field in form_fields:
                    field_type = field.get_field_type_display()
                    required = ' (обязательное)' if field.is_required else ''
                    fields_list.append(format_html(
                        '<li><strong>{}</strong> ({}) - {}{}</li>',
                        field.label,
                        field.name,
                        field_type,
                        required
                    ))
                fields_list.append('</ul>')
            else:
                fields_list.append(format_html(
                    '<p style="color: orange; margin: 0;">В форме "{}" нет полей. Добавьте поля в форме записи.</p>',
                    obj.booking_form.title
                ))
        elif obj.source_type == 'quiz' and obj.quiz:
            questions = obj.quiz.questions.all().order_by('order', 'id')
            if questions.exists():
                fields_list.append(format_html('<h4 style="margin-top: 0;">Вопросы анкеты "{}":</h4>', obj.quiz.title))
                fields_list.append('<ul style="margin: 0; padding-left: 20px;">')
                # Базовые поля пользователя
                fields_list.append('<li><strong>Имя пользователя</strong> (user_name) - Текст</li>')
                fields_list.append('<li><strong>Телефон пользователя</strong> (user_phone) - Телефон</li>')
                fields_list.append('<li><strong>Email пользователя</strong> (user_email) - Email</li>')
                # Вопросы анкеты
                for question in questions:
                    question_type = question.get_question_type_display()
                    fields_list.append(format_html(
                        '<li><strong>{}</strong> (question_{}) - {}</li>',
                        question.text[:50] + ('...' if len(question.text) > 50 else ''),
                        question.id,
                        question_type
                    ))
                fields_list.append('</ul>')
            else:
                fields_list.append(format_html(
                    '<p style="color: orange; margin: 0;">В анкете "{}" нет вопросов.</p>',
                    obj.quiz.title
                ))
        else:
            fields_list.append('<p style="color: gray; margin: 0;">Выберите форму записи или анкету для отображения полей.</p>')
        
        return format_html(''.join(fields_list))
    form_fields_display.short_description = 'Доступные поля для маппинга'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Динамически скрываем поля в зависимости от source_type
        if obj:
            if obj.source_type == 'booking_form':
                form.base_fields['quiz'].widget = admin.widgets.AdminTextInputWidget()
                form.base_fields['quiz'].widget.attrs['style'] = 'display:none'
            elif obj.source_type == 'quiz':
                form.base_fields['booking_form'].widget = admin.widgets.AdminTextInputWidget()
                form.base_fields['booking_form'].widget.attrs['style'] = 'display:none'
        return form
    
    class Media:
        js = (
            'admin/js/jquery.init.js',  # Убеждаемся, что jQuery загружен
            'admin/js/moyklass_integration.js',
        )
    
