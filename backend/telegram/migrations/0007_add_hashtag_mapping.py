# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('telegram', '0006_add_catalog_page_to_telegram_settings'),
        ('content', '0015_add_content_pages'),  # ContentPage создается в этой миграции
        ('booking', '0001_initial'),  # BookingForm
        ('quizzes', '0001_initial'),  # Quiz
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramHashtagMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hashtag', models.CharField(help_text='Хештег из поста Telegram (например, новости, статья). Без символа #', max_length=100, unique=True, verbose_name='Хештег')),
                ('width', models.CharField(choices=[('narrow', 'Узкая (1/3 ширины)'), ('medium', 'Средняя (1/2 ширины)'), ('wide', 'Широкая (2/3 ширины)'), ('full', 'На всю ширину')], default='medium', help_text='Ширина элемента в сетке каталога', max_length=10, verbose_name='Ширина элемента')),
                ('has_own_page', models.BooleanField(default=True, help_text='Если включено, карточка будет иметь свой URL и может быть открыта как отдельная страница', verbose_name='Может быть открыт как страница')),
                ('button_type', models.CharField(choices=[('booking', 'Запись'), ('quiz', 'Анкета'), ('external', 'Внешняя ссылка'), ('none', 'Без кнопки')], default='none', help_text='Тип кнопки для элемента каталога', max_length=20, verbose_name='Тип кнопки')),
                ('button_text', models.CharField(blank=True, default='', help_text='Текст кнопки (если тип кнопки не "Без кнопки")', max_length=100, verbose_name='Текст кнопки')),
                ('button_external_url', models.URLField(blank=True, help_text='Внешняя ссылка (если тип кнопки - "Внешняя ссылка")', null=True, verbose_name='Внешняя ссылка')),
                ('is_active', models.BooleanField(default=True, help_text='Если выключено, элементы с этим хештегом не будут создаваться', verbose_name='Активен')),
                ('order', models.IntegerField(default=0, help_text='Порядок сортировки элементов в каталоге (0 - в конец)', verbose_name='Порядок')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлен')),
                ('button_booking_form', models.ForeignKey(blank=True, help_text='Выберите форму записи (если тип кнопки - "Запись")', limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='booking.bookingform', verbose_name='Форма записи')),
                ('button_quiz', models.ForeignKey(blank=True, help_text='Выберите анкету (если тип кнопки - "Анкета")', limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='quizzes.quiz', verbose_name='Анкета')),
                ('catalog_page', models.ForeignKey(help_text='Страница каталога, в которую будут создаваться элементы из постов с этим хештегом', limit_choices_to={'is_active': True, 'page_type': 'catalog'}, on_delete=django.db.models.deletion.CASCADE, related_name='hashtag_mappings', to='content.contentpage', verbose_name='Страница каталога')),
            ],
            options={
                'verbose_name': 'Настройка хештега',
                'verbose_name_plural': 'Настройки хештегов',
                'ordering': ['hashtag'],
            },
        ),
    ]
