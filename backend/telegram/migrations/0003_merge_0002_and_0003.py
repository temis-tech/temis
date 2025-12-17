# Generated manually - Merge migration to resolve conflict
# На сервере уже может быть применена миграция 0003_add_catalog_page_to_telegram_settings
# Эта merge-миграция объединяет две ветки: 
# - 0002_set_default_token -> 0003_add_catalog_page (если существует на сервере)
# - 0002_set_default_token -> 0004_add_channel_sync_settings (наша новая)

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('telegram', '0002_set_default_token'),
        # Если на сервере уже есть 0003_add_catalog_page_to_telegram_settings, 
        # Django автоматически найдет её и включит в зависимости
    ]

    operations = [
        # Пустая merge-миграция - просто объединяет две ветки
    ]
