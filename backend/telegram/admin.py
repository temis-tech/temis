from django.contrib import admin
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
import json
from config.constants import get_api_domain, get_protocol, TELEGRAM_WEBHOOK_PATH
from .models import TelegramBotSettings, TelegramUser, TelegramHashtagMapping
try:
    from .models import TelegramSyncLog
    TELEGRAM_SYNC_LOG_AVAILABLE = True
except ImportError:
    TELEGRAM_SYNC_LOG_AVAILABLE = False
    TelegramSyncLog = None
from .bot import set_webhook, delete_webhook, get_bot_settings


@admin.register(TelegramBotSettings)
class TelegramBotSettingsAdmin(admin.ModelAdmin):
    """Админка для настроек Telegram бота"""
    
    def has_add_permission(self, request):
        # Разрешаем только одну запись
        return not TelegramBotSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление
        return False
    
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Обработка кнопок установки/удаления webhook"""
        if request.method == 'POST' and '_setup_webhook' in request.POST:
            # Установка webhook
            obj = self.get_object(request, object_id)
            if obj:
                api_domain = get_api_domain()
                # Telegram требует HTTPS для webhook
                protocol = 'https'
                webhook_url = f'{protocol}://{api_domain}{TELEGRAM_WEBHOOK_PATH}'
                
                if not obj.token:
                    messages.error(request, 'Укажите токен бота перед установкой webhook')
                elif not obj.is_active:
                    messages.warning(request, 'Бот неактивен. Webhook будет установлен, но уведомления не будут отправляться.')
                    if set_webhook(webhook_url):
                        messages.success(request, f'Webhook успешно установлен: {webhook_url}')
                    else:
                        messages.error(request, 'Ошибка установки webhook. Проверьте токен и доступность URL.')
                else:
                    if set_webhook(webhook_url):
                        messages.success(request, f'Webhook успешно установлен: {webhook_url}')
                    else:
                        messages.error(request, 'Ошибка установки webhook. Проверьте токен и доступность URL.')
            else:
                messages.error(request, 'Настройки бота не найдены. Создайте их сначала.')
            
            return redirect(request.path)
        
        elif request.method == 'POST' and '_delete_webhook' in request.POST:
            # Удаление webhook
            obj = self.get_object(request, object_id)
            if obj:
                if delete_webhook():
                    messages.success(request, 'Webhook успешно удален')
                else:
                    messages.error(request, 'Ошибка удаления webhook')
            else:
                messages.error(request, 'Настройки бота не найдены.')
            
            return redirect(request.path)
        
        return super().changeform_view(request, object_id, form_url, extra_context)
    
    def response_change(self, request, obj):
        """Добавляем кнопки в форму"""
        if '_setup_webhook' in request.POST or '_delete_webhook' in request.POST:
            # Уже обработано в changeform_view
            return redirect(request.path)
        return super().response_change(request, obj)
    
    def get_readonly_fields(self, request, obj=None):
        """Делаем webhook_url и webhook_actions только для чтения"""
        readonly = list(super().get_readonly_fields(request, obj))
        readonly.extend(['webhook_url', 'webhook_actions', 'channel_id'])
        return readonly
    
    def webhook_actions(self, obj):
        """Отображает кнопки для управления webhook"""
        if not obj:
            return ''
        
        api_domain = get_api_domain()
        # Telegram требует HTTPS для webhook
        protocol = 'https'
        webhook_url = f'{protocol}://{api_domain}{TELEGRAM_WEBHOOK_PATH}'
        
        buttons = []
        
        if obj.webhook_url:
            buttons.append(
                format_html(
                    '<input type="submit" name="_delete_webhook" value="Удалить webhook" '
                    'class="button" style="background-color: #ba2121; color: white; margin-left: 10px;" '
                    'onclick="return confirm(\'Вы уверены, что хотите удалить webhook?\');">'
                )
            )
            buttons.append(
                format_html(
                    '<input type="submit" name="_setup_webhook" value="Обновить webhook" '
                    'class="button" style="margin-left: 10px;">'
                )
            )
        else:
            buttons.append(
                format_html(
                    '<input type="submit" name="_setup_webhook" value="Установить webhook" '
                    'class="button" style="background-color: #417690; color: white;">'
                )
            )
        
        buttons.append(
            format_html(
                '<p style="margin-top: 10px; color: #666;">'
                'URL: <code>{}</code>'
                '</p>',
                webhook_url
            )
        )
        
        return format_html(''.join(buttons))
    
    webhook_actions.short_description = 'Управление webhook'
    
    fieldsets = (
        ('Основные настройки', {
            'fields': ('token', 'is_active'),
            'description': 'После настройки токена и активации бота, установите webhook кнопкой ниже'
        }),
        ('Webhook', {
            'fields': ('webhook_actions',),
            'classes': ('wide',),
        }),
        ('Настройки уведомлений', {
            'fields': (
                'notify_on_quiz',
                'notify_on_booking',
                'notify_on_banner_start',
                'notify_on_banner_end',
            ),
            'description': 'Выберите, какие события должны отправлять уведомления'
        }),
        ('Синхронизация с каналом', {
            'fields': (
                'sync_channel_enabled',
                'channel_username',
                'channel_id',
                'catalog_page',
            ),
            'description': 'Настройки для автоматического создания элементов каталога из постов в Telegram канале. '
                         'Бот должен быть администратором канала. Укажите username канала (например, @channel_name) '
                         'или ID канала. ID канала будет заполнен автоматически при первой синхронизации. '
                         'Обязательно укажите страницу каталога, в которую будут создаваться элементы.'
        }),
        ('Техническая информация', {
            'fields': ('webhook_url',),
            'classes': ('collapse',),
            'description': 'URL webhook устанавливается автоматически при нажатии кнопки "Установить webhook"'
        }),
    )


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    """Админка для пользователей Telegram"""
    list_display = ('telegram_id', 'get_full_name', 'username', 'is_admin', 'is_active', 'created_at')
    list_filter = ('is_admin', 'is_active', 'created_at')
    search_fields = ('telegram_id', 'username', 'first_name', 'last_name')
    list_editable = ('is_admin', 'is_active')
    
    fieldsets = (
        ('Информация о пользователе', {
            'fields': ('telegram_id', 'username', 'first_name', 'last_name'),
            'description': 'При создании пользователя вручную заполните все поля. При редактировании существующего пользователя эти поля только для чтения.'
        }),
        ('Настройки', {
            'fields': ('is_admin', 'is_active')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Делаем поля только для чтения при редактировании, но редактируемыми при создании"""
        readonly = ['created_at', 'updated_at']
        # При редактировании существующего пользователя делаем информационные поля readonly
        if obj:  # obj существует - значит редактируем
            readonly.extend(['telegram_id', 'username', 'first_name', 'last_name'])
        # При создании нового пользователя (obj=None) все поля редактируемые
        return readonly
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Имя'


@admin.register(TelegramHashtagMapping)
class TelegramHashtagMappingAdmin(admin.ModelAdmin):
    """Админка для настроек хештегов"""
    list_display = ('hashtag', 'catalog_page', 'width', 'button_type', 'has_own_page', 'is_active', 'order')
    list_filter = ('is_active', 'button_type', 'width', 'catalog_page')
    search_fields = ('hashtag', 'catalog_page__title')
    list_editable = ('is_active', 'order')
    ordering = ('hashtag',)
    
    fieldsets = (
        ('Основные настройки', {
            'fields': ('hashtag', 'catalog_page', 'is_active', 'order'),
            'description': 'Хештег указывается без символа # (например, "новости" вместо "#новости"). '
                         'Элементы каталога будут создаваться в указанную страницу каталога.'
        }),
        ('Настройки элемента каталога', {
            'fields': (
                'width',
                'has_own_page',
            ),
            'description': 'Настройки внешнего вида элемента каталога'
        }),
        ('Настройки текста', {
            'fields': (
                'preview_separator',
                'preview_length',
            ),
            'description': 'Настройки разделения текста на превью (для карточки) и полный текст (для страницы). '
                         'Если указан разделитель, текст до разделителя пойдет в карточку, после - в полный текст. '
                         'Если разделитель не указан, будет использовано автоматическое обрезание по длине превью.'
        }),
        ('Настройки изображения на странице', {
            'fields': (
                'image_position',
                'image_target_width',
                'image_target_height',
            ),
            'description': 'Настройки отображения изображения на странице элемента. '
                         'Позиция определяет, где будет отображаться изображение (сверху, снизу, слева, справа или не отображать). '
                         'Целевые размеры определяют, к какому размеру будет приведено изображение с сохранением пропорций и центрированием.'
        }),
        ('Настройки кнопки', {
            'fields': (
                'button_type',
                'button_text',
                'button_booking_form',
                'button_quiz',
                'button_external_url',
            ),
            'description': 'Настройки кнопки для элемента каталога. '
                         'В зависимости от типа кнопки заполните соответствующее поле: '
                         'форма записи для "Запись", анкета для "Анкета", внешняя ссылка для "Внешняя ссылка".'
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        return ['created_at', 'updated_at']


if TELEGRAM_SYNC_LOG_AVAILABLE and TelegramSyncLog:
    @admin.register(TelegramSyncLog)
    class TelegramSyncLogAdmin(admin.ModelAdmin):
        """Админка для логов синхронизации Telegram"""
    list_display = ('created_at', 'event_type', 'status_badge', 'chat_username', 'hashtags', 'catalog_item_title', 'message_preview')
    list_filter = ('event_type', 'status', 'created_at', 'chat_id')
    search_fields = ('message', 'error_details', 'catalog_item_title', 'hashtags', 'chat_username')
    readonly_fields = ('created_at', 'raw_data_preview', 'catalog_item_link')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('event_type', 'status', 'created_at')
        }),
        ('Информация о Telegram посте', {
            'fields': ('message_id', 'chat_id', 'chat_username', 'hashtags')
        }),
        ('Информация об элементе каталога', {
            'fields': ('catalog_item_link', 'catalog_item_title')
        }),
        ('Детали события', {
            'fields': ('message', 'error_details')
        }),
        ('Отладочная информация', {
            'fields': ('raw_data_preview',),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Отображает статус с цветным бейджем"""
        color = obj.get_status_color()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'status'
    
    def message_preview(self, obj):
        """Показывает превью сообщения"""
        if obj.message:
            preview = obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
            return format_html('<span title="{}">{}</span>', obj.message, preview)
        return '-'
    message_preview.short_description = 'Сообщение'
    
    def raw_data_preview(self, obj):
        """Показывает превью исходных данных"""
        if obj.raw_data:
            formatted = json.dumps(obj.raw_data, indent=2, ensure_ascii=False)
            return format_html('<pre style="max-height: 400px; overflow: auto; background: #f5f5f5; padding: 10px; border-radius: 4px;">{}</pre>', formatted)
        return '-'
    raw_data_preview.short_description = 'Исходные данные'
    
    def catalog_item_link(self, obj):
        """Ссылка на элемент каталога"""
        if obj.catalog_item:
            url = reverse('admin:content_catalogitem_change', args=[obj.catalog_item.pk])
            return format_html('<a href="{}">{}</a>', url, obj.catalog_item.title)
        return '-'
    catalog_item_link.short_description = 'Элемент каталога'
    
    def has_add_permission(self, request):
        """Запрещаем создание логов вручную"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Запрещаем редактирование логов"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Разрешаем удаление логов"""
        return True
else:
    # Модель TelegramSyncLog еще не доступна (миграция не применена)
    TelegramSyncLogAdmin = None
    
