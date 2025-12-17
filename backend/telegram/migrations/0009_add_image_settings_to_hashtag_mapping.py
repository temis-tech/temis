# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram', '0008_add_preview_settings_to_hashtag_mapping'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramhashtagmapping',
            name='image_position',
            field=models.CharField(
                choices=[
                    ('top', 'Сверху'),
                    ('bottom', 'Снизу'),
                    ('left', 'Слева'),
                    ('right', 'Справа'),
                    ('none', 'Не отображать'),
                ],
                default='top',
                help_text='Где отображать изображение на странице элемента: сверху, снизу, слева, справа или не отображать',
                max_length=10,
                verbose_name='Позиция изображения на странице'
            ),
        ),
        migrations.AddField(
            model_name='telegramhashtagmapping',
            name='image_target_width',
            field=models.IntegerField(
                blank=True,
                help_text='Ширина, к которой будет приведено изображение. Изображение будет вписано в этот размер с сохранением пропорций, центрировано. Если не указано, используется размер по умолчанию.',
                null=True,
                verbose_name='Целевая ширина изображения (px)'
            ),
        ),
        migrations.AddField(
            model_name='telegramhashtagmapping',
            name='image_target_height',
            field=models.IntegerField(
                blank=True,
                help_text='Высота, к которой будет приведено изображение. Изображение будет вписано в этот размер с сохранением пропорций, центрировано. Если не указано, используется размер по умолчанию.',
                null=True,
                verbose_name='Целевая высота изображения (px)'
            ),
        ),
    ]
