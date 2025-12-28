# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0002_alter_quiz_options_alter_quizsubmission_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='integrate_with_crm',
            field=models.BooleanField(default=False, help_text='При отправке анкеты автоматически создавать лид в CRM', verbose_name='Интегрировать с CRM'),
        ),
    ]

