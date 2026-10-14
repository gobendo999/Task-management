# Generated for Task composite indexes
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo_app', '0003_task_user'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['user', '-created_at'], name='todo_task_user_created_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['user', 'completed'], name='todo_task_user_completed_idx'),
        ),
    ]
