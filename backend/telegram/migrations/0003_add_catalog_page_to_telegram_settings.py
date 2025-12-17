# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('telegram', '0002_add_channel_sync_settings'),
        ('content', '0049_add_price_is_from_to_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegrambotsettings',
            name='catalog_page',
            field=models.ForeignKey(
                blank=True,
                help_text='Страница каталога, в которую будут создаваться элементы из постов Telegram. Если не указана, элементы не будут создаваться.',
                limit_choices_to={'is_active': True, 'page_type': 'catalog'},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='telegram_sync_sources',
                to='content.contentpage',
                verbose_name='Страница каталога'
            ),
        ),
    ]
