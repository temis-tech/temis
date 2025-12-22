# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0056_change_hero_subtitle_to_richtext'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='description',
            field=models.TextField(blank=True, help_text='Краткое описание сайта для мета-тегов и соцсетей (Open Graph, Twitter Card)', max_length=500, verbose_name='Описание сайта'),
        ),
    ]

