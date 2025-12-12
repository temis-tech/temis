# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0034_add_card_description_to_catalog_item'),
    ]

    operations = [
        # Добавляем поля для размера видео
        migrations.AddField(
            model_name='catalogitem',
            name='video_width',
            field=models.IntegerField(blank=True, default=800, help_text='Ширина видео-фрейма в пикселях. По умолчанию: 800px', null=True, verbose_name='Ширина видео (px)'),
        ),
        migrations.AddField(
            model_name='catalogitem',
            name='video_height',
            field=models.IntegerField(blank=True, default=450, help_text='Высота видео-фрейма в пикселях. По умолчанию: 450px (соответствует соотношению 16:9 для ширины 800px)', null=True, verbose_name='Высота видео (px)'),
        ),
        # Убираем ограничение page_type для catalog_items
        # Примечание: limit_choices_to не является частью схемы БД, это только ограничение для админки
        # Поэтому мы просто обновляем help_text, чтобы указать, что ограничение снято
        migrations.AlterField(
            model_name='catalogitem',
            name='page',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='catalog_items', to='content.contentpage', verbose_name='Страница'),
        ),
        # Убираем ограничение page_type для gallery_images
        migrations.AlterField(
            model_name='galleryimage',
            name='page',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='gallery_images', to='content.contentpage', verbose_name='Страница'),
        ),
    ]
