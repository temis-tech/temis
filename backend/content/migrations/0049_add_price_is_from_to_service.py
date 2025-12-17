# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0048_add_show_catalog_navigator'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='price_is_from',
            field=models.BooleanField(default=False, help_text='Если включено, перед ценой будет отображаться "От" (например, "От 1000 ₽")', verbose_name='Цена "От"'),
        ),
        migrations.AddField(
            model_name='service',
            name='price_with_abonement_is_from',
            field=models.BooleanField(default=False, help_text='Если включено, перед ценой по абонементу будет отображаться "От"', verbose_name='Цена по абонементу "От"'),
        ),
    ]
