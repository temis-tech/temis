# Generated manually - Merge migration to resolve conflict
# 
# Эта merge-миграция объединяет две возможные ветки:
# 1. Если на сервере есть 0003_add_catalog_page_to_telegram_settings:
#    - 0002_set_default_token -> 0003_add_catalog_page_to_telegram_settings
#    - 0002_set_default_token -> 0003_merge -> 0004_add_channel_sync_settings
# 2. Если на сервере нет 0003_add_catalog_page_to_telegram_settings:
#    - 0002_set_default_token -> 0003_merge -> 0004_add_channel_sync_settings
#
# Django автоматически обнаружит конфликт и создаст правильные зависимости

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('telegram', '0004_add_channel_sync_settings'),
        # Если на сервере есть 0003_add_catalog_page_to_telegram_settings,
        # Django автоматически добавит её в зависимости при обнаружении конфликта
    ]

    operations = [
        # Пустая merge-миграция - просто объединяет две ветки
    ]
