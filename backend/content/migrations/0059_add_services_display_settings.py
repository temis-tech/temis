# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0058_alter_default_values'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentpage',
            name='services_card_style',
            field=models.CharField(choices=[('standard', 'Стандартная карточка'), ('compact', 'Компактная карточка'), ('detailed', 'Подробная карточка'), ('minimal', 'Минималистичная карточка')], default='standard', help_text='Выберите стиль отображения карточек услуг', max_length=20, verbose_name='Стиль карточки услуги'),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='services_show_title',
            field=models.BooleanField(default=True, help_text='Отображать заголовок над блоком услуг', verbose_name='Показывать заголовок блока услуг'),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='services_title',
            field=models.CharField(blank=True, default='Наши услуги', help_text='Заголовок, который будет отображаться над блоком услуг. Если не указан, используется "Наши услуги"', max_length=200, verbose_name='Заголовок блока услуг'),
        ),
    ]

