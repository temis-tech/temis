# Generated manually

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0013_add_image_vertical_align_to_hero'),
    ]

    operations = [
        migrations.AddField(
            model_name='headersettings',
            name='logo_height',
            field=models.IntegerField(default=100, help_text='Максимальная высота логотипа в пикселях (от 20 до 200)', validators=[django.core.validators.MinValueValidator(20), django.core.validators.MaxValueValidator(200)], verbose_name='Высота логотипа (px)'),
        ),
        migrations.AddField(
            model_name='headersettings',
            name='header_height',
            field=models.IntegerField(default=140, help_text='Общая высота шапки в пикселях (от 60 до 300). Используется для отступа контента.', validators=[django.core.validators.MinValueValidator(60), django.core.validators.MaxValueValidator(300)], verbose_name='Высота шапки (px)'),
        ),
    ]

