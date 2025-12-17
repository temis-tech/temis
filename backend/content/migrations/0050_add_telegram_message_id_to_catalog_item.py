# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0049_add_price_is_from_to_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalogitem',
            name='telegram_message_id',
            field=models.BigIntegerField(blank=True, help_text='ID сообщения из Telegram канала для связи с постом и обновления при редактировании', null=True, unique=True, verbose_name='ID сообщения Telegram'),
        ),
    ]
