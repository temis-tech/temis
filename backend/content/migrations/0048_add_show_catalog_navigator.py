# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0047_add_rich_text_and_price_position_to_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentpage',
            name='show_catalog_navigator',
            field=models.BooleanField(default=False, help_text='Если включено, на странице каталога будет отображаться навигационный список элементов каталога для удобной навигации по статьям', verbose_name='Показывать рубрикатор (навигационный список)'),
        ),
    ]
