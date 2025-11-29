# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0015_add_content_pages'),
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Например: "Основное меню", "Меню версия 2"', max_length=100, unique=True, verbose_name='Название меню')),
                ('description', models.CharField(blank=True, help_text='Краткое описание для чего это меню', max_length=200, verbose_name='Описание')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активно')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
            ],
            options={
                'verbose_name': 'Меню',
                'verbose_name_plural': 'Меню',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='menuitem',
            name='menu',
            field=models.ForeignKey(blank=True, help_text='Выберите меню, к которому относится этот пункт', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='content.menu', verbose_name='Меню'),
        ),
        migrations.AddField(
            model_name='headersettings',
            name='menu',
            field=models.ForeignKey(blank=True, help_text='Выберите меню, которое будет отображаться в шапке. Если не выбрано, будет использоваться меню по умолчанию.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='header_settings', to='content.menu', verbose_name='Меню для отображения'),
        ),
        migrations.AddField(
            model_name='footersettings',
            name='menu',
            field=models.ForeignKey(blank=True, help_text='Выберите меню, которое будет отображаться в футере. Если не выбрано, будет использоваться меню по умолчанию.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='footer_settings', to='content.menu', verbose_name='Меню для отображения'),
        ),
        migrations.AlterModelOptions(
            name='menuitem',
            options={'ordering': ['order', 'title'], 'verbose_name': 'Пункт меню', 'verbose_name_plural': 'Пункты меню'},
        ),
    ]

