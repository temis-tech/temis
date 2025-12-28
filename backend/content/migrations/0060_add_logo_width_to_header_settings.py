# Generated manually

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0059_add_services_display_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='headersettings',
            name='logo_width',
            field=models.IntegerField(default=150, help_text='Максимальная ширина логотипа в пикселях (от 50 до 400). Используется для ограничения размера на мобильных устройствах.', validators=[django.core.validators.MinValueValidator(50), django.core.validators.MaxValueValidator(400)], verbose_name='Ширина логотипа (px)'),
        ),
    ]

