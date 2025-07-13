# backend/task_persistence/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('task_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersistentJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('job_data', models.JSONField(default=dict, help_text='Configuration du job')),
                ('current_step', models.CharField(default='init', max_length=100)),
                ('total_steps', models.PositiveIntegerField(default=1)),
                ('completed_steps', models.PositiveIntegerField(default=0)),
                ('can_resume', models.BooleanField(default=True)),
                ('resume_from_step', models.CharField(blank=True, max_length=100)),
                ('last_checkpoint_at', models.DateTimeField(blank=True, null=True)),
                ('progress_percentage', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('estimated_remaining_minutes', models.PositiveIntegerField(blank=True, null=True)),
                ('base_task', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='persistent_job', to='task_core.basetask')),
            ],
            options={
                'db_table': 'task_persistent_job',
            },
        ),
        migrations.CreateModel(
            name='JobState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pages_status', models.JSONField(default=dict, help_text='Statut par page')),
                ('error_log', models.JSONField(default=list, help_text='Log des erreurs')),
                ('warnings', models.JSONField(default=list, help_text='Avertissements')),
                ('retry_count', models.PositiveIntegerField(default=0)),
                ('max_retries', models.PositiveIntegerField(default=3)),
                ('last_error_message', models.TextField(blank=True)),
                ('persistent_job', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='job_state', to='task_persistence.persistentjob')),
            ],
            options={
                'db_table': 'task_job_state',
            },
        ),
        migrations.CreateModel(
            name='JobCheckpoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('step_name', models.CharField(max_length=100)),
                ('checkpoint_data', models.JSONField(default=dict)),
                ('is_recovery_point', models.BooleanField(default=True)),
                ('persistent_job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checkpoints', to='task_persistence.persistentjob')),
            ],
            options={
                'db_table': 'task_job_checkpoint',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='persistentjob',
            index=models.Index(fields=['can_resume', 'current_step'], name='task_persis_can_res_8272d2_idx'),
        ),
        migrations.AddIndex(
            model_name='persistentjob',
            index=models.Index(fields=['base_task', 'last_checkpoint_at'], name='task_persis_base_ta_7004e9_idx'),
        ),
        migrations.AddIndex(
            model_name='jobcheckpoint',
            index=models.Index(fields=['persistent_job', 'step_name'], name='task_job_ch_persist_484bd9_idx'),
        ),
        migrations.AddIndex(
            model_name='jobcheckpoint',
            index=models.Index(fields=['is_recovery_point', 'created_at'], name='task_job_ch_is_reco_9e3bf4_idx'),
        ),
    ]
