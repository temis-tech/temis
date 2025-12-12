# Generated manually

from django.db import migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0033_add_video_url_to_catalog_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalogitem',
            name='card_description',
            field=ckeditor.fields.RichTextField(blank=True, help_text='Краткое описание, которое будет отображаться в карточке элемента в списке каталога. Поддерживает форматирование текста.', verbose_name='Описание для карточки (превью)'),
        ),
        migrations.AlterField(
            model_name='catalogitem',
            name='description',
            field=ckeditor.fields.RichTextField(blank=True, help_text='Полное описание, которое будет отображаться на странице элемента (если включен режим "Может быть открыт как страница").', verbose_name='Описание для страницы'),
        ),
    ]
