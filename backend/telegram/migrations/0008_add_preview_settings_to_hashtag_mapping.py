# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram', '0007_add_hashtag_mapping'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramhashtagmapping',
            name='preview_separator',
            field=models.CharField(blank=True, default='', help_text='Символ или текст для разделения превью и полного текста (например, "---" или "<!--more-->"). Если указан, текст до разделителя пойдет в карточку, после - в полный текст. Если не указан, будет использовано автоматическое обрезание.', max_length=10, verbose_name='Разделитель текста'),
        ),
        migrations.AddField(
            model_name='telegramhashtagmapping',
            name='preview_length',
            field=models.IntegerField(blank=True, default=200, help_text='Максимальная длина текста для карточки превью. Используется только если не указан разделитель. По умолчанию: 200 символов.', null=True, verbose_name='Длина превью (символов)'),
        ),
    ]
