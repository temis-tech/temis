# Generated manually
from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0044_add_menu_item_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentpage',
            name='faq_columns',
            field=models.IntegerField(
                default=1,
                help_text='Количество вопросов в одной строке (1, 2 или 3). Вопросы будут пропорционально распределены по ширине (только для типа "FAQ")',
                validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(3)],
                verbose_name='Количество колонок'
            ),
        ),
    ]
