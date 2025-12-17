# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegrambotsettings',
            name='sync_channel_enabled',
            field=models.BooleanField(default=False, help_text='Автоматически создавать элементы каталога из постов в Telegram канале', verbose_name='Включить синхронизацию с каналом'),
        ),
        migrations.AddField(
            model_name='telegrambotsettings',
            name='channel_username',
            field=models.CharField(blank=True, help_text='Username канала (например, @channel_name) или ID канала (например, -1001234567890). Бот должен быть администратором канала.', max_length=200, verbose_name='Username канала'),
        ),
        migrations.AddField(
            model_name='telegrambotsettings',
            name='channel_id',
            field=models.CharField(blank=True, help_text='ID канала (заполняется автоматически при первой синхронизации)', max_length=100, verbose_name='ID канала'),
        ),
    ]
