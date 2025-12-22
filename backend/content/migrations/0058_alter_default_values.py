# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0057_add_description_to_site_settings'),
    ]

    operations = [
        # Изменяем default значения полей
        # Это безопасно, так как изменяет только значения по умолчанию для новых записей
        # Существующие записи не затрагиваются
        migrations.AlterField(
            model_name='headersettings',
            name='logo_text',
            field=models.CharField(default='Temis', max_length=100, verbose_name='Текст логотипа'),
        ),
        migrations.AlterField(
            model_name='herosettings',
            name='button_text',
            field=models.CharField(default='Записаться', max_length=100, verbose_name='Текст кнопки'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='site_name',
            field=models.CharField(default='Temis', help_text='Название сайта, отображаемое в шапке и других местах', max_length=200, verbose_name='Название сайта'),
        ),
    ]

