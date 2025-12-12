# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0036_add_gallery_page_to_catalog_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentpage',
            name='gallery_display_type',
            field=models.CharField(choices=[('grid', 'Плитка (сетка)'), ('carousel', 'Карусель'), ('masonry', 'Кирпичная кладка')], default='grid', help_text='Выберите способ отображения изображений галереи (только для типа "Галерея")', max_length=20, verbose_name='Вид отображения галереи'),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='gallery_enable_fullscreen',
            field=models.BooleanField(default=True, help_text='Если включено, при клике на изображение оно откроется в полноэкранном режиме с возможностью перелистывания (только для типа "Галерея")', verbose_name='Открывать изображения на весь экран'),
        ),
    ]
