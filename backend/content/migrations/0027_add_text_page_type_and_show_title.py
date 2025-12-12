# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0026_add_width_to_catalog_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentpage',
            name='show_title',
            field=models.BooleanField(
                default=True,
                help_text='Если отключено, заголовок страницы не будет отображаться на сайте',
                verbose_name='Показывать заголовок на странице',
            ),
        ),
        migrations.AlterField(
            model_name='contentpage',
            name='page_type',
            field=models.CharField(
                choices=[
                    ('catalog', 'Каталог'),
                    ('gallery', 'Галерея'),
                    ('home', 'Главная'),
                    ('text', 'Описание'),
                ],
                default='catalog',
                max_length=20,
                verbose_name='Тип страницы',
            ),
        ),
    ]
