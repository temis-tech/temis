# Generated manually

from django.db import migrations, models
import django.db.models.deletion
from ckeditor.fields import RichTextField


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0038_add_video_support_to_gallery_image'),
    ]

    operations = [
        # Добавляем 'faq' в PAGE_TYPES
        migrations.AlterField(
            model_name='contentpage',
            name='page_type',
            field=models.CharField(
                choices=[
                    ('catalog', 'Каталог'),
                    ('gallery', 'Галерея'),
                    ('home', 'Главная'),
                    ('text', 'Описание'),
                    ('faq', 'FAQ (Вопросы-Ответы)'),
                ],
                default='catalog',
                max_length=20,
                verbose_name='Тип страницы'
            ),
        ),
        # Добавляем настройки FAQ в ContentPage
        migrations.AddField(
            model_name='contentpage',
            name='faq_icon',
            field=models.ImageField(
                blank=True,
                help_text='Маленькая пиктограммка для вопроса (только для типа "FAQ")',
                null=True,
                upload_to='faq/',
                verbose_name='Иконка вопроса'
            ),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='faq_icon_position',
            field=models.CharField(
                choices=[('left', 'Слева'), ('right', 'Справа')],
                default='left',
                help_text='Расположение иконки относительно вопроса (только для типа "FAQ")',
                max_length=10,
                verbose_name='Позиция иконки'
            ),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='faq_background_color',
            field=models.CharField(
                blank=True,
                default='#FFFFFF',
                help_text='Цвет фона секции FAQ в формате HEX (например, #FFFFFF) (только для типа "FAQ")',
                max_length=7,
                verbose_name='Цвет фона'
            ),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='faq_background_image',
            field=models.ImageField(
                blank=True,
                help_text='Фоновое изображение для секции FAQ (только для типа "FAQ")',
                null=True,
                upload_to='faq/',
                verbose_name='Фоновое изображение'
            ),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='faq_animation',
            field=models.CharField(
                choices=[
                    ('slide', 'Слайд'),
                    ('fade', 'Плавное появление'),
                    ('none', 'Без анимации'),
                ],
                default='slide',
                help_text='Тип анимации при раскрытии вопроса (только для типа "FAQ")',
                max_length=20,
                verbose_name='Анимация разворачивания'
            ),
        ),
        # Создаем модель FAQItem
        migrations.CreateModel(
            name='FAQItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=500, verbose_name='Вопрос')),
                ('answer', RichTextField(help_text='Ответ на вопрос с поддержкой форматирования', verbose_name='Ответ')),
                ('order', models.IntegerField(default=0, verbose_name='Порядок')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлен')),
                ('page', models.ForeignKey(
                    limit_choices_to={'page_type': 'faq'},
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='faq_items',
                    to='content.contentpage',
                    verbose_name='Страница FAQ'
                )),
            ],
            options={
                'verbose_name': 'Элемент FAQ',
                'verbose_name_plural': 'Элементы FAQ',
                'ordering': ['order', 'created_at'],
            },
        ),
    ]
