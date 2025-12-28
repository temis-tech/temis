# Generated manually

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0065_add_services_card_sizes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentpage',
            name='services_card_standard_width',
            field=models.IntegerField(blank=True, default=300, help_text='Ширина карточки в пикселях (от 200 до 600px). Если не указано, используется 300px.', null=True, validators=[django.core.validators.MinValueValidator(200), django.core.validators.MaxValueValidator(600)], verbose_name='Ширина стандартной карточки (px)'),
        ),
        migrations.AlterField(
            model_name='contentpage',
            name='services_card_standard_height',
            field=models.IntegerField(blank=True, default=450, help_text='Высота карточки в пикселях (от 300 до 800px). Если не указано, используется 450px.', null=True, validators=[django.core.validators.MinValueValidator(300), django.core.validators.MaxValueValidator(800)], verbose_name='Высота стандартной карточки (px)'),
        ),
        migrations.AlterField(
            model_name='contentpage',
            name='services_card_compact_width',
            field=models.IntegerField(blank=True, default=280, help_text='Ширина карточки в пикселях (от 200 до 500px). Если не указано, используется 280px.', null=True, validators=[django.core.validators.MinValueValidator(200), django.core.validators.MaxValueValidator(500)], verbose_name='Ширина компактной карточки (px)'),
        ),
        migrations.AlterField(
            model_name='contentpage',
            name='services_card_compact_height',
            field=models.IntegerField(blank=True, default=380, help_text='Высота карточки в пикселях (от 250 до 600px). Если не указано, используется 380px.', null=True, validators=[django.core.validators.MinValueValidator(250), django.core.validators.MaxValueValidator(600)], verbose_name='Высота компактной карточки (px)'),
        ),
        migrations.AlterField(
            model_name='contentpage',
            name='services_card_detailed_width',
            field=models.IntegerField(blank=True, default=350, help_text='Ширина карточки в пикселях (от 300 до 700px). Если не указано, используется 350px.', null=True, validators=[django.core.validators.MinValueValidator(300), django.core.validators.MaxValueValidator(700)], verbose_name='Ширина подробной карточки (px)'),
        ),
        migrations.AlterField(
            model_name='contentpage',
            name='services_card_detailed_height',
            field=models.IntegerField(blank=True, default=550, help_text='Высота карточки в пикселях (от 400 до 900px). Если не указано, используется 550px.', null=True, validators=[django.core.validators.MinValueValidator(400), django.core.validators.MaxValueValidator(900)], verbose_name='Высота подробной карточки (px)'),
        ),
        migrations.AlterField(
            model_name='contentpage',
            name='services_card_minimal_width',
            field=models.IntegerField(blank=True, default=100, help_text='Ширина карточки в пикселях (100% ширины контейнера, значение игнорируется). Если не указано, используется 100px.', null=True, validators=[django.core.validators.MinValueValidator(100), django.core.validators.MaxValueValidator(100)], verbose_name='Ширина минималистичной карточки (px)'),
        ),
        migrations.AlterField(
            model_name='contentpage',
            name='services_card_minimal_height',
            field=models.IntegerField(blank=True, default=120, help_text='Высота карточки в пикселях (от 100 до 200px). Если не указано, используется 120px.', null=True, validators=[django.core.validators.MinValueValidator(100), django.core.validators.MaxValueValidator(200)], verbose_name='Высота минималистичной карточки (px)'),
        ),
    ]

