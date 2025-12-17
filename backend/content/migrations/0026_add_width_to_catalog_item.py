# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0025_fix_catalog_item_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalogitem',
            name='width',
            field=models.CharField(
                choices=[
                    ('narrow', 'Узкая (1/3 ширины)'),
                    ('medium', 'Средняя (1/2 ширины)'),
                    ('wide', 'Широкая (2/3 ширины)'),
                    ('full', 'На всю ширину'),
                ],
                default='medium',
                help_text='Ширина элемента в сетке каталога',
                max_length=10,
                verbose_name='Ширина элемента',
            ),
        ),
    ]

