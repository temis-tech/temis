# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_bookingform_default_quiz'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingsubmission',
            name='source_page',
            field=models.CharField(
                blank=True,
                help_text='URL страницы, с которой была отправлена форма',
                max_length=500,
                verbose_name='Страница источника'
            ),
        ),
    ]
