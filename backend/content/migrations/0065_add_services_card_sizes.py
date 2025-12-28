# Generated manually

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0064_remove_short_description_from_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentpage',
            name='services_card_standard_width',
            field=models.IntegerField(default=300, help_text='Ширина карточки в пикселях (от 200 до 600px)', validators=[django.core.validators.MinValueValidator(200), django.core.validators.MaxValueValidator(600)], verbose_name='Ширина стандартной карточки (px)'),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='services_card_standard_height',
            field=models.IntegerField(default=450, help_text='Высота карточки в пикселях (от 300 до 800px)', validators=[django.core.validators.MinValueValidator(300), django.core.validators.MaxValueValidator(800)], verbose_name='Высота стандартной карточки (px)'),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='services_card_compact_width',
            field=models.IntegerField(default=280, help_text='Ширина карточки в пикселях (от 200 до 500px)', validators=[django.core.validators.MinValueValidator(200), django.core.validators.MaxValueValidator(500)], verbose_name='Ширина компактной карточки (px)'),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='services_card_compact_height',
            field=models.IntegerField(default=380, help_text='Высота карточки в пикселях (от 250 до 600px)', validators=[django.core.validators.MinValueValidator(250), django.core.validators.MaxValueValidator(600)], verbose_name='Высота компактной карточки (px)'),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='services_card_detailed_width',
            field=models.IntegerField(default=350, help_text='Ширина карточки в пикселях (от 300 до 700px)', validators=[django.core.validators.MinValueValidator(300), django.core.validators.MaxValueValidator(700)], verbose_name='Ширина подробной карточки (px)'),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='services_card_detailed_height',
            field=models.IntegerField(default=550, help_text='Высота карточки в пикселях (от 400 до 900px)', validators=[django.core.validators.MinValueValidator(400), django.core.validators.MaxValueValidator(900)], verbose_name='Высота подробной карточки (px)'),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='services_card_minimal_width',
            field=models.IntegerField(default=100, help_text='Ширина карточки в пикселях (100% ширины контейнера, значение игнорируется)', validators=[django.core.validators.MinValueValidator(100), django.core.validators.MaxValueValidator(100)], verbose_name='Ширина минималистичной карточки (px)'),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='services_card_minimal_height',
            field=models.IntegerField(default=120, help_text='Высота карточки в пикселях (от 100 до 200px)', validators=[django.core.validators.MinValueValidator(100), django.core.validators.MaxValueValidator(200)], verbose_name='Высота минималистичной карточки (px)'),
        ),
    ]

