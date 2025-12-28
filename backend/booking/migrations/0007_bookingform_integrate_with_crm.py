# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0005_alter_bookingform_default_quiz_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingform',
            name='integrate_with_crm',
            field=models.BooleanField(default=False, help_text='При отправке формы автоматически создавать лид в CRM', verbose_name='Интегрировать с CRM'),
        ),
    ]

