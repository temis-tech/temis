# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0066_make_services_card_sizes_nullable'),
        ('telegram', '0009_add_image_settings_to_hashtag_mapping'),
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramSyncLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('webhook_received', 'Webhook получен'), ('channel_post', 'Пост из канала'), ('edited_channel_post', 'Пост отредактирован'), ('catalog_item_created', 'Элемент каталога создан'), ('catalog_item_updated', 'Элемент каталога обновлен'), ('catalog_item_deactivated', 'Элемент каталога деактивирован'), ('error', 'Ошибка'), ('warning', 'Предупреждение'), ('info', 'Информация')], max_length=50, verbose_name='Тип события')),
                ('status', models.CharField(choices=[('success', 'Успешно'), ('error', 'Ошибка'), ('warning', 'Предупреждение'), ('skipped', 'Пропущено')], default='success', max_length=20, verbose_name='Статус')),
                ('message_id', models.BigIntegerField(blank=True, null=True, verbose_name='ID сообщения Telegram')),
                ('chat_id', models.CharField(blank=True, max_length=100, verbose_name='ID канала')),
                ('chat_username', models.CharField(blank=True, max_length=200, verbose_name='Username канала')),
                ('hashtags', models.CharField(blank=True, help_text='Хештеги из поста (через запятую)', max_length=500, verbose_name='Хештеги')),
                ('catalog_item_title', models.CharField(blank=True, max_length=500, verbose_name='Название элемента')),
                ('message', models.TextField(blank=True, help_text='Детальное описание события', verbose_name='Сообщение')),
                ('error_details', models.TextField(blank=True, help_text='Детали ошибки, если произошла', verbose_name='Детали ошибки')),
                ('raw_data', models.JSONField(blank=True, help_text='Исходные данные из Telegram (для отладки)', null=True, verbose_name='Исходные данные')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('catalog_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='telegram_sync_logs', to='content.catalogitem', verbose_name='Элемент каталога')),
            ],
            options={
                'verbose_name': 'Лог синхронизации Telegram',
                'verbose_name_plural': 'Логи синхронизации Telegram',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='telegramsynclog',
            index=models.Index(fields=['created_at'], name='telegram_te_created_idx'),
        ),
        migrations.AddIndex(
            model_name='telegramsynclog',
            index=models.Index(fields=['event_type', 'status'], name='telegram_te_event_t_idx'),
        ),
        migrations.AddIndex(
            model_name='telegramsynclog',
            index=models.Index(fields=['message_id'], name='telegram_te_message_idx'),
        ),
        migrations.AddIndex(
            model_name='telegramsynclog',
            index=models.Index(fields=['chat_id'], name='telegram_te_chat_id_idx'),
        ),
    ]

