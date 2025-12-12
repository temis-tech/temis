# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0028_add_image_settings'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialNetwork',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название соцсети для отображения', max_length=100, verbose_name='Название')),
                ('network_type', models.CharField(choices=[('vk', 'ВКонтакте'), ('telegram', 'Telegram'), ('whatsapp', 'WhatsApp'), ('instagram', 'Instagram'), ('facebook', 'Facebook'), ('youtube', 'YouTube'), ('twitter', 'Twitter'), ('ok', 'Одноклассники'), ('custom', 'Другая')], default='custom', help_text='Выберите тип соцсети или "Другая" для кастомной', max_length=20, verbose_name='Тип соцсети')),
                ('url', models.URLField(help_text='Ссылка на профиль/канал в соцсети', max_length=500, verbose_name='URL')),
                ('icon', models.ImageField(blank=True, help_text='Иконка соцсети (если не указана, будет использована стандартная)', null=True, upload_to='social/', verbose_name='Иконка')),
                ('order', models.IntegerField(default=0, help_text='Порядок отображения в списке', verbose_name='Порядок')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создана')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлена')),
            ],
            options={
                'verbose_name': 'Социальная сеть',
                'verbose_name_plural': 'Социальные сети',
                'ordering': ['order', 'name'],
                'app_label': 'content',
            },
        ),
    ]
