# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('booking', '0007_bookingform_integrate_with_crm'),
        ('quizzes', '0004_quiz_integrate_with_crm'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeadStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Название статуса')),
                ('code', models.CharField(choices=[('new', 'Новый'), ('in_progress', 'В процессе работы'), ('cancelled', 'Отмена'), ('converted', 'Превращен в клиента')], default='new', max_length=20, verbose_name='Код статуса')),
                ('color', models.CharField(default='#007bff', help_text='Цвет для отображения в интерфейсе', max_length=7, verbose_name='Цвет (HEX)')),
                ('order', models.IntegerField(default=0, verbose_name='Порядок')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
            ],
            options={
                'verbose_name': 'Статус лида',
                'verbose_name_plural': 'Статусы лидов',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, verbose_name='Имя (зашифровано)')),
                ('phone', models.TextField(blank=True, verbose_name='Телефон (зашифровано)')),
                ('email', models.TextField(blank=True, verbose_name='Email (зашифровано)')),
                ('additional_data', models.TextField(blank=True, verbose_name='Дополнительные данные (JSON, зашифрован)')),
                ('source', models.CharField(blank=True, help_text='Источник лида (форма записи, анкета и т.д.)', max_length=100, verbose_name='Источник')),
                ('notes', models.TextField(blank=True, help_text='Внутренние заметки по лиду', verbose_name='Заметки')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлен')),
                ('converted_at', models.DateTimeField(blank=True, null=True, verbose_name='Превращен в клиента')),
                ('booking_submission', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='leads', to='booking.bookingsubmission', verbose_name='Отправка формы записи')),
                ('quiz_submission', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='leads', to='quizzes.quizsubmission', verbose_name='Отправка анкеты')),
                ('status', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='leads', to='crm.leadstatus', verbose_name='Статус')),
            ],
            options={
                'verbose_name': 'Лид',
                'verbose_name_plural': 'Лиды',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, verbose_name='Имя (зашифровано)')),
                ('phone', models.TextField(blank=True, verbose_name='Телефон (зашифровано)')),
                ('email', models.TextField(blank=True, verbose_name='Email (зашифровано)')),
                ('additional_data_json', models.JSONField(blank=True, default=dict, verbose_name='Дополнительные данные')),
                ('notes', models.TextField(blank=True, help_text='Внутренние заметки по клиенту', verbose_name='Заметки')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлен')),
                ('source_lead', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='client', to='crm.lead', verbose_name='Исходный лид')),
            ],
            options={
                'verbose_name': 'Клиент',
                'verbose_name_plural': 'Клиенты',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ClientFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='crm/client_files/%Y/%m/%d/', verbose_name='Файл')),
                ('name', models.CharField(blank=True, help_text='Название для отображения (если не указано, используется имя файла)', max_length=200, verbose_name='Название файла')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Загружен')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='crm.client', verbose_name='Клиент')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user', verbose_name='Загружен пользователем')),
            ],
            options={
                'verbose_name': 'Файл клиента',
                'verbose_name_plural': 'Файлы клиентов',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(fields=['-created_at'], name='crm_lead_created_idx'),
        ),
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(fields=['status'], name='crm_lead_status_idx'),
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['-created_at'], name='crm_client_created_idx'),
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['is_active'], name='crm_client_is_acti_idx'),
        ),
    ]

