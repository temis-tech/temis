# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0031_add_card_image_to_catalog_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalogitem',
            name='video_url',
            field=models.URLField(blank=True, null=True, verbose_name='URL видео', help_text='Ссылка на видео с YouTube, Rutube или другого видеохостинга. Видео будет отображаться на странице элемента с кнопками управления.'),
        ),
    ]
