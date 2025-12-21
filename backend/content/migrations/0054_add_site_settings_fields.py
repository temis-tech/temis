# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0053_alter_catalogitem_image_align_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='site_name',
            field=models.CharField(default='Радуга слов', help_text='Название сайта, отображаемое в шапке и других местах', max_length=200, verbose_name='Название сайта'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='page_title',
            field=models.CharField(default='Логопедический центр', help_text='Заголовок страницы (title), отображаемый во вкладке браузера', max_length=200, verbose_name='Заголовок страницы'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='favicon',
            field=models.ImageField(blank=True, help_text='Иконка сайта, отображаемая во вкладке браузера (рекомендуемый размер: 32x32 или 16x16 пикселей)', null=True, upload_to='site/', verbose_name='Фавикон'),
        ),
        migrations.AlterModelOptions(
            name='sitesettings',
            options={'verbose_name': 'Настройки сайта', 'verbose_name_plural': 'Настройки сайта'},
        ),
    ]

