# Generated manually

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0060_add_logo_width_to_header_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='headersettings',
            name='logo_mobile_scale',
            field=models.IntegerField(default=100, help_text='Процент размера логотипа на мобильных устройствах (от 30 до 100). 100% = полный размер, 50% = половина размера.', validators=[django.core.validators.MinValueValidator(30), django.core.validators.MaxValueValidator(100)], verbose_name='Уменьшение логотипа на мобильных (%)'),
        ),
    ]

