# backend/ai_templates_analytics/migrations/0001_initial.py

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TemplateFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rating', models.PositiveIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('comment', models.TextField(blank=True)),
                ('feedback_type', models.CharField(choices=[('quality', 'Qualité'), ('ease_of_use', "Facilité d'usage"), ('relevance', 'Pertinence'), ('bug_report', 'Bug'), ('suggestion', 'Suggestion')], max_length=20)),
                ('is_public', models.BooleanField(default=False, help_text='Commentaire visible publiquement')),
                ('admin_response', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'template_feedback',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TemplatePerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('generation_time', models.FloatField(help_text='Temps de génération (secondes)')),
                ('tokens_used', models.PositiveIntegerField(default=0)),
                ('output_quality_score', models.FloatField(blank=True, help_text='Score qualité 0-10', null=True)),
                ('variables_used', models.JSONField(default=dict, help_text='Variables utilisées pour cette génération')),
                ('was_successful', models.BooleanField(default=True)),
                ('error_message', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'template_performance',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TemplatePopularity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ranking_period', models.CharField(choices=[('daily', 'Quotidien'), ('weekly', 'Hebdomadaire'), ('monthly', 'Mensuel'), ('yearly', 'Annuel')], max_length=20)),
                ('rank_position', models.PositiveIntegerField()),
                ('usage_count', models.PositiveIntegerField()),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
            ],
            options={
                'db_table': 'template_popularity',
                'ordering': ['ranking_period', 'rank_position'],
            },
        ),
        migrations.CreateModel(
            name='TemplateUsageMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('total_uses', models.PositiveIntegerField(default=0)),
                ('successful_generations', models.PositiveIntegerField(default=0)),
                ('failed_generations', models.PositiveIntegerField(default=0)),
                ('unique_users', models.PositiveIntegerField(default=0)),
                ('last_used_at', models.DateTimeField(blank=True, null=True)),
                ('avg_generation_time', models.FloatField(default=0.0, help_text='Temps moyen de génération (secondes)')),
                ('popularity_score', models.FloatField(default=0.0, help_text='Score de popularité calculé')),
            ],
            options={
                'db_table': 'template_usage_metrics',
            },
        ),
    ]
