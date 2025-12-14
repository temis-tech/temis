# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0045_add_faq_columns'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentpage',
            name='display_services',
            field=models.ManyToManyField(
                blank=True,
                help_text='Выберите услуги, которые будут отображаться на этой странице. Услуги будут автоматически фильтроваться по выбранному филиалу, если он указан.',
                related_name='displayed_on_pages',
                to='content.service',
                verbose_name='Услуги для отображения'
            ),
        ),
    ]
