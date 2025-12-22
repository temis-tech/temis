# Generated manually

from django.db import migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0055_add_height_to_hero'),
    ]

    operations = [
        migrations.AlterField(
            model_name='herosettings',
            name='subtitle',
            field=ckeditor.fields.RichTextField(blank=True, help_text='Подзаголовок с поддержкой форматирования текста', verbose_name='Подзаголовок'),
        ),
    ]

