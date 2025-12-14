# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0039_add_faq_page_type'),
    ]

    operations = [
        # Создаем модель ServiceBranch
        migrations.CreateModel(
            name='ServiceBranch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(blank=True, decimal_places=2, help_text='Если не указана, используется базовая цена из услуги', max_digits=10, null=True, verbose_name='Цена в этом филиале')),
                ('price_with_abonement', models.DecimalField(blank=True, decimal_places=2, help_text='Если не указана, используется базовая цена по абонементу из услуги', max_digits=10, null=True, verbose_name='Цена по абонементу')),
                ('is_available', models.BooleanField(default=True, help_text='Можно временно отключить услугу в конкретном филиале', verbose_name='Доступна в этом филиале')),
                ('order', models.IntegerField(default=0, help_text='Порядок отображения услуги в списке услуг филиала', verbose_name='Порядок отображения')),
                ('crm_item_id', models.CharField(blank=True, help_text='ID услуги/айтема в системе МойКласс для синхронизации данных', max_length=100, null=True, verbose_name='ID айтема в CRM МойКласс')),
                ('crm_item_data', models.JSONField(blank=True, help_text='Дополнительные данные из CRM (цены абонементов, условия и т.д.)', null=True, verbose_name='Данные из CRM')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создана')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлена')),
                ('branch', models.ForeignKey(blank=True, help_text='Если филиал удален, связь сохраняется для истории', null=True, on_delete=django.db.models.deletion.SET_NULL, to='content.branch', verbose_name='Филиал')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_branches', to='content.service', verbose_name='Услуга')),
            ],
            options={
                'verbose_name': 'Услуга в филиале',
                'verbose_name_plural': 'Услуги в филиалах',
                'ordering': ['order', 'branch__order', 'service__order'],
                'unique_together': {('service', 'branch')},
            },
        ),
        # Создаем индексы для ServiceBranch
        migrations.AddIndex(
            model_name='servicebranch',
            index=models.Index(fields=['service', 'branch'], name='content_ser_service_8a1f2d_idx'),
        ),
        migrations.AddIndex(
            model_name='servicebranch',
            index=models.Index(fields=['is_available', 'branch'], name='content_ser_is_avail_8b2f3e_idx'),
        ),
        # Создаем модель ServiceBranchPriceHistory
        migrations.CreateModel(
            name='ServiceBranchPriceHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('price_with_abonement', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Цена по абонементу')),
                ('changed_at', models.DateTimeField(auto_now_add=True, verbose_name='Изменено')),
                ('notes', models.TextField(blank=True, help_text='Причина изменения цены или дополнительная информация', verbose_name='Примечание')),
                ('changed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Изменено пользователем')),
                ('service_branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_history', to='content.servicebranch', verbose_name='Услуга в филиале')),
            ],
            options={
                'verbose_name': 'История изменения цены',
                'verbose_name_plural': 'История изменений цен',
                'ordering': ['-changed_at'],
            },
        ),
        # Создаем индекс для ServiceBranchPriceHistory
        migrations.AddIndex(
            model_name='servicebranchpricehistory',
            index=models.Index(fields=['service_branch', '-changed_at'], name='content_ser_service_9c3f4d_idx'),
        ),
    ]
