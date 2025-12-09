from django.db import migrations


def set_default_token(apps, schema_editor):
    """Устанавливает дефолтный токен при миграции"""
    TelegramBotSettings = apps.get_model('telegram', 'TelegramBotSettings')
    # Создаем настройки с дефолтным токеном, если их еще нет
    # Используем update_or_create для безопасности
    TelegramBotSettings.objects.update_or_create(
        id=1,  # Принудительно устанавливаем id=1
        defaults={
            'token': '8576779956:AAEmqm1yQmtO06aiXdcdUfi-H4ZKqecbZBo',
            'is_active': False,  # По умолчанию неактивен, нужно включить вручную
            'notify_on_quiz': True,
            'notify_on_booking': True,
            'notify_on_banner_start': True,
            'notify_on_banner_end': True,
        }
    )


def reverse_set_default_token(apps, schema_editor):
    """Обратная миграция - удаляем настройки"""
    TelegramBotSettings = apps.get_model('telegram', 'TelegramBotSettings')
    TelegramBotSettings.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('telegram', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(set_default_token, reverse_set_default_token),
    ]

