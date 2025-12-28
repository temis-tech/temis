# Generated manually

from django.db import migrations


def create_initial_statuses(apps, schema_editor):
    """Создать начальные статусы лидов"""
    LeadStatus = apps.get_model('crm', 'LeadStatus')
    
    statuses = [
        {'name': 'Новый', 'code': 'new', 'color': '#28a745', 'order': 0},
        {'name': 'В процессе работы', 'code': 'in_progress', 'color': '#ffc107', 'order': 1},
        {'name': 'Отмена', 'code': 'cancelled', 'color': '#dc3545', 'order': 2},
        {'name': 'Превращен в клиента', 'code': 'converted', 'color': '#17a2b8', 'order': 3},
    ]
    
    for status_data in statuses:
        LeadStatus.objects.get_or_create(
            code=status_data['code'],
            defaults=status_data
        )


def reverse_create_initial_statuses(apps, schema_editor):
    """Удалить начальные статусы"""
    LeadStatus = apps.get_model('crm', 'LeadStatus')
    LeadStatus.objects.filter(code__in=['new', 'in_progress', 'cancelled', 'converted']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_statuses, reverse_create_initial_statuses),
    ]

