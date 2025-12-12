from django.contrib import admin
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from config.constants import get_api_domain, get_protocol, TELEGRAM_WEBHOOK_PATH
from .models import TelegramBotSettings, TelegramUser
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
        readonly.extend(['webhook_url', 'webhook_actions'])
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
