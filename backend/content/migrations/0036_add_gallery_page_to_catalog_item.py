# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0035_add_video_size_and_remove_page_type_limits'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalogitem',
            name='gallery_page',
            field=models.ForeignKey(blank=True, help_text='Выберите страницу с типом "Галерея", которая будет отображаться на странице элемента каталога', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='catalog_items_with_gallery', to='content.contentpage', verbose_name='Страница галереи', limit_choices_to={'page_type': 'gallery'}),
        ),
    ]
