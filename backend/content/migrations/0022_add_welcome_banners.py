from django.db import migrations, models
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_bookingform_default_quiz'),
        ('quizzes', '0001_initial'),
        ('content', '0021_change_catalog_item_button_fields_to_foreignkey'),
    ]

    operations = [
        migrations.CreateModel(
            name='WelcomeBanner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, verbose_name='Заголовок')),
                ('subtitle', ckeditor.fields.RichTextField(blank=True, verbose_name='Описание')),
                ('background_color', models.CharField(default='#FFFFFF', max_length=7, verbose_name='Цвет фона')),
                ('text_color', models.CharField(default='#1C1C1C', max_length=7, verbose_name='Цвет текста')),
                ('content_width', models.CharField(choices=[('narrow', 'Узкая (600px)'), ('medium', 'Средняя (800px)'), ('wide', 'Широкая (1000px)'), ('full', 'На всю ширину (1200px)')], default='full', max_length=10, verbose_name='Ширина контента')),
                ('start_at', models.DateTimeField(blank=True, null=True, verbose_name='Активен с')),
                ('end_at', models.DateTimeField(blank=True, null=True, verbose_name='Активен до')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('order', models.IntegerField(default=0, verbose_name='Порядок')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлен')),
            ],
            options={
                'verbose_name': 'Приветственный баннер',
                'verbose_name_plural': 'Приветственные баннеры',
                'ordering': ['order', '-start_at'],
            },
        ),
        migrations.CreateModel(
            name='WelcomeBannerCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('description', ckeditor.fields.RichTextField(blank=True, verbose_name='Описание')),
                ('image', models.ImageField(blank=True, null=True, upload_to='welcome_banners/', verbose_name='Изображение')),
                ('button_type', models.CharField(choices=[('none', 'Без кнопки'), ('link', 'Ссылка'), ('booking', 'Форма записи'), ('quiz', 'Анкета')], default='none', max_length=20, verbose_name='Тип кнопки')),
                ('button_text', models.CharField(blank=True, max_length=100, verbose_name='Текст кнопки')),
                ('button_url', models.URLField(blank=True, max_length=500, verbose_name='Ссылка')),
                ('order', models.IntegerField(default=0, verbose_name='Порядок')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна')),
                ('banner', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='cards', to='content.welcomebanner', verbose_name='Баннер')),
                ('button_booking_form', models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=models.deletion.SET_NULL, to='booking.bookingform', verbose_name='Форма записи')),
                ('button_quiz', models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=models.deletion.SET_NULL, to='quizzes.quiz', verbose_name='Анкета')),
            ],
            options={
                'verbose_name': 'Карточка приветственного баннера',
                'verbose_name_plural': 'Карточки приветственного баннера',
                'ordering': ['order', 'id'],
            },
        ),
    ]

