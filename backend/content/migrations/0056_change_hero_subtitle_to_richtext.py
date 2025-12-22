# Generated manually

from django.db import migrations
try:
    import ckeditor.fields
except ImportError:
    # Fallback если ckeditor не установлен (не должно произойти, но на всякий случай)
    from django.db import models
    ckeditor = None


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0055_add_height_to_hero'),
    ]

    operations = [
        migrations.AlterField(
            model_name='herosettings',
            name='subtitle',
            field=ckeditor.fields.RichTextField(blank=True, help_text='Подзаголовок с поддержкой форматирования текста', verbose_name='Подзаголовок') if ckeditor else migrations.TextField(blank=True, help_text='Подзаголовок с поддержкой форматирования текста', verbose_name='Подзаголовок'),
        ),
    ]

