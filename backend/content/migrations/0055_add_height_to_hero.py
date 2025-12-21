# Generated manually

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0054_add_site_settings_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='herosettings',
            name='height',
            field=models.IntegerField(blank=True, help_text='Высота Hero секции в пикселях (от 200 до 2000px). Если не указано, используется минимальная высота.', null=True, validators=[django.core.validators.MinValueValidator(200), django.core.validators.MaxValueValidator(2000)], verbose_name='Высота секции (px)'),
        ),
    ]

