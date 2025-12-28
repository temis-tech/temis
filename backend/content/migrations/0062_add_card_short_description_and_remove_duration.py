# Generated manually

from django.db import migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0061_add_logo_mobile_scale_to_header_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='card_short_description',
            field=ckeditor.fields.RichTextField(blank=True, help_text='Краткое описание для отображения в карточках услуг (стиль "minimal"). Поддерживает форматирование текста.', verbose_name='Краткое описание для карточки'),
        ),
        migrations.RemoveField(
            model_name='service',
            name='duration',
        ),
    ]

