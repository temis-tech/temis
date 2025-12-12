# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0037_add_gallery_settings_to_content_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='galleryimage',
            name='content_type',
            field=models.CharField(choices=[('image', 'Изображение'), ('video', 'Видео')], default='image', help_text='Выберите тип контента: изображение или видео', max_length=10, verbose_name='Тип контента'),
        ),
        migrations.AlterField(
            model_name='galleryimage',
            name='image',
            field=models.ImageField(blank=True, help_text='Загрузите изображение (если тип контента - "Изображение")', null=True, upload_to='gallery/', verbose_name='Изображение'),
        ),
        migrations.AddField(
            model_name='galleryimage',
            name='video_file',
            field=models.FileField(blank=True, help_text='Загрузите видео файл (если тип контента - "Видео" и хотите загрузить локально)', null=True, upload_to='gallery/videos/', verbose_name='Видео файл'),
        ),
        migrations.AddField(
            model_name='galleryimage',
            name='video_url',
            field=models.URLField(blank=True, help_text='Ссылка на видео с YouTube, Rutube, Vimeo или другого видеохостинга (если тип контента - "Видео")', null=True, verbose_name='URL видео'),
        ),
        migrations.AlterModelOptions(
            name='galleryimage',
            options={'ordering': ['order', 'created_at'], 'verbose_name': 'Элемент галереи', 'verbose_name_plural': 'Элементы галереи'},
        ),
    ]
