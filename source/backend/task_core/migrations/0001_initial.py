# backend/task_core/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('brands_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskQueue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('concurrency', models.PositiveIntegerField(default=2)),
                ('max_memory_mb', models.PositiveIntegerField(default=512)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'task_queue',
            },
        ),
        migrations.CreateModel(
            name='TaskType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('default_priority', models.CharField(default='normal', max_length=20)),
                ('timeout_seconds', models.PositiveIntegerField(default=3600)),
                ('max_retries', models.PositiveIntegerField(default=3)),
                ('default_queue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task_core.taskqueue')),
            ],
            options={
                'db_table': 'task_type',
            },
        ),
        migrations.CreateModel(
            name='BaseTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('task_id', models.CharField(db_index=True, max_length=255, unique=True)),
                ('celery_task_id', models.CharField(blank=True, max_length=255, null=True)),
                ('task_type', models.CharField(db_index=True, max_length=100)),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('processing', 'En cours'), ('completed', 'Terminé'), ('failed', 'Échoué'), ('cancelled', 'Annulé'), ('retry', 'En attente de retry')], default='pending', max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Basse'), ('normal', 'Normale'), ('high', 'Haute'), ('critical', 'Critique')], default='normal', max_length=20)),
                ('queue_name', models.CharField(default='normal', max_length=50)),
                ('description', models.TextField(blank=True)),
                ('context_data', models.JSONField(blank=True, default=dict)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_set', to='brands_core.brand')),
            ],
            options={
                'db_table': 'task_base',
                'ordering': ['-created_at'],
            },
        ),
    ]
