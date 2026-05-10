from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id',          models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title',       models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, default='')),
                ('priority',    models.CharField(choices=[('high','🔴 High'),('medium','🟡 Medium'),('low','🟢 Low')], default='medium', max_length=10)),
                ('status',      models.CharField(choices=[('pending','⏳ Pending'),('in_progress','🔄 In Progress'),('completed','✅ Completed')], default='pending', max_length=20)),
                ('created_at',  models.DateTimeField(auto_now_add=True)),
                ('updated_at',  models.DateTimeField(auto_now=True)),
                ('user',        models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='auth.user')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['user', 'status'], name='tasks_task_user_id_status_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['user', 'priority'], name='tasks_task_user_id_priority_idx'),
        ),
    ]
