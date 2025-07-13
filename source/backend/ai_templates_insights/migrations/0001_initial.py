# backend/ai_templates_insights/migrations/0001_initial.py

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OptimizationSuggestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('suggestion_type', models.CharField(choices=[('content_improvement', 'Amélioration contenu'), ('variable_optimization', 'Optimisation variables'), ('performance_boost', 'Boost performance'), ('user_experience', 'Expérience utilisateur'), ('seo_enhancement', 'Amélioration SEO')], max_length=30)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('implementation_difficulty', models.CharField(choices=[('easy', 'Facile'), ('medium', 'Moyen'), ('hard', 'Difficile')], max_length=20)),
                ('estimated_impact', models.CharField(choices=[('low', 'Faible'), ('medium', 'Moyen'), ('high', 'Élevé')], max_length=20)),
                ('supporting_data', models.JSONField(default=dict, help_text='Données justifiant la suggestion')),
                ('is_implemented', models.BooleanField(default=False)),
                ('implemented_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'optimization_suggestion',
                'ordering': ['-estimated_impact', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TemplateInsight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('insight_type', models.CharField(choices=[('underused', 'Sous-utilisé'), ('performance_drop', 'Baisse performance'), ('quality_issue', 'Problème qualité'), ('trending_up', 'En hausse'), ('optimization_needed', 'Optimisation requise')], max_length=30)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('severity', models.CharField(choices=[('low', 'Faible'), ('medium', 'Moyenne'), ('high', 'Élevée'), ('critical', 'Critique')], max_length=20)),
                ('data_source', models.JSONField(default=dict, help_text="Données ayant généré l'insight")),
                ('is_resolved', models.BooleanField(default=False)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('auto_generated', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'template_insight',
                'ordering': ['-severity', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TemplateRecommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('recommendation_type', models.CharField(choices=[('trending', 'Tendance'), ('personalized', 'Personnalisé'), ('similar_brands', 'Marques similaires'), ('performance_based', 'Performance'), ('new_release', 'Nouveauté')], max_length=30)),
                ('confidence_score', models.FloatField(help_text='Score de confiance 0-1')),
                ('reasoning', models.TextField(help_text='Explication de la recommandation')),
                ('priority', models.PositiveIntegerField(default=50, help_text='Priorité 1-100')),
                ('is_active', models.BooleanField(default=True)),
                ('clicked', models.BooleanField(default=False)),
                ('clicked_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'template_recommendation',
                'ordering': ['-priority', '-confidence_score', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TrendAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('analysis_type', models.CharField(choices=[('usage_trends', 'Tendances usage'), ('performance_trends', 'Tendances performance'), ('popularity_shifts', 'Évolution popularité'), ('category_analysis', 'Analyse catégories'), ('seasonal_patterns', 'Patterns saisonniers')], max_length=30)),
                ('scope', models.CharField(choices=[('global', 'Global'), ('brand', 'Par brand'), ('category', 'Par catégorie'), ('template_type', 'Par type')], max_length=20)),
                ('scope_id', models.PositiveIntegerField(blank=True, help_text="ID de l'entité analysée", null=True)),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
                ('trend_direction', models.CharField(choices=[('increasing', 'Croissante'), ('decreasing', 'Décroissante'), ('stable', 'Stable'), ('volatile', 'Volatile')], max_length=20)),
                ('trend_strength', models.FloatField(help_text='Force de la tendance 0-1')),
                ('key_findings', models.JSONField(default=dict, help_text='Principales découvertes')),
                ('visualization_data', models.JSONField(default=dict, help_text='Données pour graphiques')),
            ],
            options={
                'db_table': 'trend_analysis',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['analysis_type', 'scope'], name='trend_analy_analysi_0a602a_idx'), models.Index(fields=['period_start', 'period_end'], name='trend_analy_period__14d58b_idx')],
            },
        ),
    ]
