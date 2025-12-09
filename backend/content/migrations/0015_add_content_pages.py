# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0015_herosettings_button_booking_form_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название страницы')),
                ('slug', models.SlugField(blank=True, help_text='Автоматически генерируется из названия, если не указан', unique=True, verbose_name='URL')),
                ('page_type', models.CharField(choices=[('catalog', 'Каталог'), ('gallery', 'Галерея'), ('home', 'Главная')], default='catalog', max_length=20, verbose_name='Тип страницы')),
                ('description', models.TextField(blank=True, help_text='Краткое описание страницы (для SEO)', verbose_name='Описание')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна')),
                ('order', models.IntegerField(default=0, verbose_name='Порядок')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создана')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлена')),
            ],
            options={
                'verbose_name': 'Страница контента',
                'verbose_name_plural': 'Страницы контента',
                'ordering': ['order', 'title'],
            },
        ),
        migrations.CreateModel(
            name='CatalogItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('image', models.ImageField(blank=True, null=True, upload_to='catalog/', verbose_name='Изображение')),
                ('order', models.IntegerField(default=0, verbose_name='Порядок')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('button_type', models.CharField(choices=[('booking', 'Запись'), ('quiz', 'Анкета'), ('external', 'Внешняя ссылка'), ('none', 'Без кнопки')], default='none', max_length=20, verbose_name='Тип кнопки')),
                ('button_text', models.CharField(blank=True, default='Записаться', max_length=100, verbose_name='Текст кнопки')),
                ('booking_form_id', models.IntegerField(blank=True, help_text='Если тип кнопки - "Запись"', null=True, verbose_name='ID формы записи')),
                ('quiz_slug', models.CharField(blank=True, help_text='Если тип кнопки - "Анкета"', max_length=200, verbose_name='Slug анкеты')),
                ('external_url', models.URLField(blank=True, help_text='Если тип кнопки - "Внешняя ссылка"', verbose_name='Внешняя ссылка')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлен')),
                ('page', models.ForeignKey(limit_choices_to={'page_type': 'catalog'}, on_delete=django.db.models.deletion.CASCADE, related_name='catalog_items', to='content.contentpage', verbose_name='Страница')),
            ],
            options={
                'verbose_name': 'Элемент каталога',
                'verbose_name_plural': 'Элементы каталога',
                'ordering': ['order', 'title'],
            },
        ),
        migrations.CreateModel(
            name='GalleryImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='gallery/', verbose_name='Изображение')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('order', models.IntegerField(default=0, verbose_name='Порядок')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создана')),
                ('page', models.ForeignKey(limit_choices_to={'page_type': 'gallery'}, on_delete=django.db.models.deletion.CASCADE, related_name='gallery_images', to='content.contentpage', verbose_name='Страница')),
            ],
            options={
                'verbose_name': 'Изображение галереи',
                'verbose_name_plural': 'Изображения галереи',
                'ordering': ['order', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='HomePageBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, help_text='Если не указан, будет использован заголовок страницы', max_length=200, verbose_name='Заголовок блока')),
                ('order', models.IntegerField(default=0, verbose_name='Порядок')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('content_page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='content.contentpage', verbose_name='Страница для отображения')),
                ('page', models.ForeignKey(limit_choices_to={'page_type': 'home'}, on_delete=django.db.models.deletion.CASCADE, related_name='home_blocks', to='content.contentpage', verbose_name='Главная страница')),
            ],
            options={
                'verbose_name': 'Блок главной страницы',
                'verbose_name_plural': 'Блоки главной страницы',
                'ordering': ['order', 'created_at'],
            },
        ),
        migrations.AddField(
            model_name='menuitem',
            name='content_page',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='menu_items', to='content.contentpage', verbose_name='Страница контента'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='url',
            field=models.CharField(blank=True, help_text='Заполните, если используете внешнюю ссылку или кастомный URL', max_length=200, verbose_name='URL'),
        ),
    ]

