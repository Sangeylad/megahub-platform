# backend/task_scheduling/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('brands_core', '0001_initial'),
        ('task_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskCalendar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('color', models.CharField(default='#6366f1', max_length=7)),
                ('is_active', models.BooleanField(default=True)),
                ('default_timezone', models.CharField(default='UTC', max_length=50)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_set', to='brands_core.brand')),
            ],
            options={
                'db_table': 'task_calendar',
                'unique_together': {('brand', 'name')},
            },
        ),
        migrations.CreateModel(
            name='PeriodicTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cron_expression', models.CharField(help_text="Expression cron (ex: '0 9 * * 1' pour lundi 9h)", max_length=100)),
                ('timezone', models.CharField(default='UTC', max_length=50)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('next_run_at', models.DateTimeField()),
                ('last_run_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('max_executions', models.PositiveIntegerField(blank=True, null=True)),
                ('executions_count', models.PositiveIntegerField(default=0)),
                ('schedule_config', models.JSONField(default=dict, help_text="Config spécifique à l'exécution")),
                ('base_task', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='periodic_task', to='task_core.basetask')),
            ],
            options={
                'db_table': 'task_periodic_task',
            },
        ),
        migrations.CreateModel(
            name='CronJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('task_type', models.CharField(max_length=100)),
                ('frequency', models.CharField(choices=[('minutely', 'Chaque minute'), ('hourly', 'Toutes les heures'), ('daily', 'Quotidien'), ('weekly', 'Hebdomadaire'), ('monthly', 'Mensuel'), ('custom', 'Expression cron personnalisée')], max_length=20)),
                ('custom_cron', models.CharField(blank=True, max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('task_config', models.JSONField(default=dict, help_text='Configuration pour la tâche')),
                ('last_execution_at', models.DateTimeField(blank=True, null=True)),
                ('total_executions', models.PositiveIntegerField(default=0)),
                ('successful_executions', models.PositiveIntegerField(default=0)),
                ('failed_executions', models.PositiveIntegerField(default=0)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_set', to='brands_core.brand')),
            ],
            options={
                'db_table': 'task_cron_job',
            },
        ),
        migrations.CreateModel(
            name='CalendarTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('custom_cron', models.CharField(blank=True, max_length=100)),
                ('custom_config', models.JSONField(blank=True, default=dict)),
                ('is_active_in_calendar', models.BooleanField(default=True)),
                ('calendar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task_scheduling.taskcalendar')),
                ('periodic_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task_scheduling.periodictask')),
            ],
            options={
                'db_table': 'task_calendar_task',
            },
        ),
        migrations.AddIndex(
            model_name='periodictask',
            index=models.Index(fields=['is_active', 'next_run_at'], name='task_period_is_acti_798fad_idx'),
        ),
        migrations.AddIndex(
            model_name='periodictask',
            index=models.Index(fields=['base_task', 'last_run_at'], name='task_period_base_ta_c37e9c_idx'),
        ),
        migrations.AddIndex(
            model_name='cronjob',
            index=models.Index(fields=['is_active', 'frequency'], name='task_cron_j_is_acti_6e40ce_idx'),
        ),
        migrations.AddIndex(
            model_name='cronjob',
            index=models.Index(fields=['brand', 'task_type'], name='task_cron_j_brand_i_12e105_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='cronjob',
            unique_together={('brand', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='calendartask',
            unique_together={('calendar', 'periodic_task')},
        ),
    ]
