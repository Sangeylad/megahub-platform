# backend/task_monitoring/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('task_core', '0001_initial'),
        ('brands_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkerHealth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('worker_name', models.CharField(max_length=100, unique=True)),
                ('queue_name', models.CharField(max_length=50)),
                ('is_online', models.BooleanField(default=True)),
                ('active_tasks', models.PositiveIntegerField(default=0)),
                ('processed_tasks', models.PositiveIntegerField(default=0)),
                ('failed_tasks', models.PositiveIntegerField(default=0)),
                ('cpu_percent', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('memory_percent', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('load_average', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('last_heartbeat', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'task_worker_health',
                'indexes': [models.Index(fields=['is_online', 'queue_name'], name='task_worker_is_onli_4ba05a_idx'), models.Index(fields=['last_heartbeat'], name='task_worker_last_he_112f1a_idx')],
            },
        ),
        migrations.CreateModel(
            name='TaskMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('execution_time_ms', models.PositiveIntegerField(blank=True, null=True)),
                ('memory_usage_mb', models.PositiveIntegerField(blank=True, null=True)),
                ('cpu_usage_percent', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('network_bytes_sent', models.PositiveIntegerField(default=0)),
                ('network_bytes_received', models.PositiveIntegerField(default=0)),
                ('disk_io_bytes', models.PositiveIntegerField(default=0)),
                ('api_calls_count', models.PositiveIntegerField(default=0)),
                ('tokens_used', models.PositiveIntegerField(default=0)),
                ('cost_usd', models.DecimalField(decimal_places=4, default=0, max_digits=10)),
                ('error_count', models.PositiveIntegerField(default=0)),
                ('warning_count', models.PositiveIntegerField(default=0)),
                ('retry_count', models.PositiveIntegerField(default=0)),
                ('worker_name', models.CharField(blank=True, max_length=100)),
                ('queue_wait_time_ms', models.PositiveIntegerField(blank=True, null=True)),
                ('base_task', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='task_core.basetask')),
            ],
            options={
                'db_table': 'task_metrics',
                'indexes': [models.Index(fields=['execution_time_ms'], name='task_metric_executi_11bad8_idx'), models.Index(fields=['memory_usage_mb'], name='task_metric_memory__9c6a0c_idx'), models.Index(fields=['cost_usd'], name='task_metric_cost_us_b3fb24_idx'), models.Index(fields=['base_task', 'created_at'], name='task_metric_base_ta_64a6c7_idx')],
            },
        ),
        migrations.CreateModel(
            name='AlertRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('metric_field', models.CharField(choices=[('execution_time_ms', "Temps d'exécution (ms)"), ('memory_usage_mb', 'Mémoire (MB)'), ('error_count', "Nombre d'erreurs"), ('cost_usd', 'Coût USD'), ('queue_wait_time_ms', "Temps d'attente queue (ms)")], max_length=50)),
                ('condition', models.CharField(choices=[('gt', 'Supérieur à'), ('gte', 'Supérieur ou égal à'), ('lt', 'Inférieur à'), ('lte', 'Inférieur ou égal à'), ('eq', 'Égal à')], max_length=10)),
                ('threshold_value', models.DecimalField(decimal_places=4, max_digits=15)),
                ('is_active', models.BooleanField(default=True)),
                ('task_types', models.JSONField(default=list, help_text='Types de tâches concernées')),
                ('notification_emails', models.JSONField(default=list)),
                ('webhook_url', models.URLField(blank=True)),
                ('cooldown_minutes', models.PositiveIntegerField(default=60)),
                ('last_triggered_at', models.DateTimeField(blank=True, null=True)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_set', to='brands_core.brand')),
            ],
            options={
                'db_table': 'task_alert_rule',
                'indexes': [models.Index(fields=['is_active', 'metric_field'], name='task_alert__is_acti_5170f8_idx'), models.Index(fields=['brand', 'is_active'], name='task_alert__brand_i_76720f_idx')],
            },
        ),
    ]
