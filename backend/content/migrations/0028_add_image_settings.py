# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0027_add_text_page_type_and_show_title'),
    ]

    operations = [
        # Добавляем настройки изображения для CatalogItem
        migrations.AddField(
            model_name='catalogitem',
            name='image_align',
            field=models.CharField(
                choices=[
                    ('left', 'Слева'),
                    ('right', 'Справа'),
                    ('center', 'По центру'),
                    ('full', 'На всю ширину'),
                ],
                default='center',
                help_text='Как изображение выравнивается относительно текста',
                max_length=10,
                verbose_name='Выравнивание изображения',
            ),
        ),
        migrations.AddField(
            model_name='catalogitem',
            name='image_size',
            field=models.CharField(
                choices=[
                    ('small', 'Маленькое (200px)'),
                    ('medium', 'Среднее (400px)'),
                    ('large', 'Большое (600px)'),
                    ('full', 'На всю ширину'),
                ],
                default='medium',
                help_text='Размер изображения',
                max_length=10,
                verbose_name='Размер изображения',
            ),
        ),
        # Добавляем настройки изображения для Service
        migrations.AddField(
            model_name='service',
            name='image_align',
            field=models.CharField(
                choices=[
                    ('left', 'Слева'),
                    ('right', 'Справа'),
                    ('center', 'По центру'),
                    ('full', 'На всю ширину'),
                ],
                default='center',
                help_text='Как изображение выравнивается относительно текста',
                max_length=10,
                verbose_name='Выравнивание изображения',
            ),
        ),
        migrations.AddField(
            model_name='service',
            name='image_size',
            field=models.CharField(
                choices=[
                    ('small', 'Маленькое (200px)'),
                    ('medium', 'Среднее (400px)'),
                    ('large', 'Большое (600px)'),
                    ('full', 'На всю ширину'),
                ],
                default='medium',
                help_text='Размер изображения',
                max_length=10,
                verbose_name='Размер изображения',
            ),
        ),
        # Добавляем изображение и настройки для ContentPage
        migrations.AddField(
            model_name='contentpage',
            name='image',
            field=models.ImageField(
                blank=True,
                help_text='Главное изображение страницы (используется для типа "Описание")',
                null=True,
                upload_to='content/',
                verbose_name='Изображение',
            ),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='image_align',
            field=models.CharField(
                choices=[
                    ('left', 'Слева'),
                    ('right', 'Справа'),
                    ('center', 'По центру'),
                    ('full', 'На всю ширину'),
                ],
                default='center',
                help_text='Как изображение выравнивается относительно текста (для типа "Описание")',
                max_length=10,
                verbose_name='Выравнивание изображения',
            ),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='image_size',
            field=models.CharField(
                choices=[
                    ('small', 'Маленькое (200px)'),
                    ('medium', 'Среднее (400px)'),
                    ('large', 'Большое (600px)'),
                    ('full', 'На всю ширину'),
                ],
                default='medium',
                help_text='Размер изображения (для типа "Описание")',
                max_length=10,
                verbose_name='Размер изображения',
            ),
        ),
    ]
