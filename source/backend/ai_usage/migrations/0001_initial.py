# backend/ai_usage/migrations/0001_initial.py

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AIJobUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('input_tokens', models.IntegerField(default=0)),
                ('output_tokens', models.IntegerField(default=0)),
                ('total_tokens', models.IntegerField(default=0)),
                ('cost_input', models.DecimalField(decimal_places=6, default=0, max_digits=10)),
                ('cost_output', models.DecimalField(decimal_places=6, default=0, max_digits=10)),
                ('total_cost', models.DecimalField(decimal_places=6, default=0, max_digits=10)),
                ('execution_time_seconds', models.IntegerField(default=0)),
                ('memory_usage_mb', models.IntegerField(default=0)),
                ('provider_name', models.CharField(max_length=50)),
                ('model_name', models.CharField(max_length=100)),
                ('success_rate', models.FloatField(default=1.0)),
                ('error_count', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'ai_job_usage',
            },
        ),
        migrations.CreateModel(
            name='AIUsageAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('provider_name', models.CharField(max_length=50)),
                ('alert_type', models.CharField(choices=[('quota_warning', 'Quota Warning 80%'), ('quota_exceeded', 'Quota Exceeded'), ('cost_warning', 'Cost Warning'), ('high_failure_rate', 'High Failure Rate'), ('unusual_usage', 'Unusual Usage Pattern')], max_length=30)),
                ('threshold_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('current_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('message', models.TextField()),
                ('is_resolved', models.BooleanField(default=False)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('email_sent', models.BooleanField(default=False)),
                ('email_sent_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'ai_usage_alert',
                'ordering': ['-created_at'],
            },
        ),
    ]
