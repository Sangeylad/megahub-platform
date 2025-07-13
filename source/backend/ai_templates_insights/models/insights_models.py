# backend/ai_templates_insights/models/insights_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class TemplateRecommendation(TimestampedMixin):
    """Recommandations personnalisées par brand/user"""
    brand = models.ForeignKey('brands_core.Brand', on_delete=models.CASCADE, related_name='template_recommendations')
    user = models.ForeignKey('users_core.CustomUser', on_delete=models.CASCADE, null=True, blank=True)
    recommended_template = models.ForeignKey('ai_templates_core.BaseTemplate', on_delete=models.CASCADE)
    recommendation_type = models.CharField(max_length=30, choices=[
        ('trending', 'Tendance'),
        ('personalized', 'Personnalisé'),
        ('similar_brands', 'Marques similaires'),
        ('performance_based', 'Performance'),
        ('new_release', 'Nouveauté')
    ])
    confidence_score = models.FloatField(help_text="Score de confiance 0-1")
    reasoning = models.TextField(help_text="Explication de la recommandation")
    priority = models.PositiveIntegerField(default=50, help_text="Priorité 1-100")
    is_active = models.BooleanField(default=True)
    clicked = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'template_recommendation'
        ordering = ['-priority', '-confidence_score', '-created_at']
        indexes = [
            models.Index(fields=['brand', 'is_active', 'priority']),
            models.Index(fields=['user', 'recommendation_type'])
        ]
    
    def __str__(self):
        target = self.user.username if self.user else f"Brand {self.brand.name}"
        return f"Rec: {self.recommended_template.name} → {target}"

class TemplateInsight(TimestampedMixin):
    """Insights automatiques détectés par IA"""
    template = models.ForeignKey('ai_templates_core.BaseTemplate', on_delete=models.CASCADE, related_name='insights')
    insight_type = models.CharField(max_length=30, choices=[
        ('underused', 'Sous-utilisé'),
        ('performance_drop', 'Baisse performance'),
        ('quality_issue', 'Problème qualité'),
        ('trending_up', 'En hausse'),
        ('optimization_needed', 'Optimisation requise')
    ])
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
        ('critical', 'Critique')
    ])
    data_source = models.JSONField(default=dict, help_text="Données ayant généré l'insight")
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    auto_generated = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'template_insight'
        ordering = ['-severity', '-created_at']
        indexes = [
            models.Index(fields=['template', 'is_resolved']),
            models.Index(fields=['insight_type', 'severity'])
        ]
    
    def __str__(self):
        return f"{self.severity.upper()}: {self.title}"

class OptimizationSuggestion(TimestampedMixin):
    """Suggestions d'amélioration basées sur data"""
    template = models.ForeignKey('ai_templates_core.BaseTemplate', on_delete=models.CASCADE, related_name='optimization_suggestions')
    suggestion_type = models.CharField(max_length=30, choices=[
        ('content_improvement', 'Amélioration contenu'),
        ('variable_optimization', 'Optimisation variables'),
        ('performance_boost', 'Boost performance'),
        ('user_experience', 'Expérience utilisateur'),
        ('seo_enhancement', 'Amélioration SEO')
    ])
    title = models.CharField(max_length=200)
    description = models.TextField()
    implementation_difficulty = models.CharField(max_length=20, choices=[
        ('easy', 'Facile'),
        ('medium', 'Moyen'),
        ('hard', 'Difficile')
    ])
    estimated_impact = models.CharField(max_length=20, choices=[
        ('low', 'Faible'),
        ('medium', 'Moyen'),
        ('high', 'Élevé')
    ])
    supporting_data = models.JSONField(default=dict, help_text="Données justifiant la suggestion")
    is_implemented = models.BooleanField(default=False)
    implemented_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'optimization_suggestion'
        ordering = ['-estimated_impact', '-created_at']
        indexes = [
            models.Index(fields=['template', 'is_implemented']),
            models.Index(fields=['suggestion_type', 'estimated_impact'])
        ]
    
    def __str__(self):
        return f"{self.title} ({self.estimated_impact} impact)"

class TrendAnalysis(TimestampedMixin):
    """Analyse des tendances d'usage et performance"""
    analysis_type = models.CharField(max_length=30, choices=[
        ('usage_trends', 'Tendances usage'),
        ('performance_trends', 'Tendances performance'),
        ('popularity_shifts', 'Évolution popularité'),
        ('category_analysis', 'Analyse catégories'),
        ('seasonal_patterns', 'Patterns saisonniers')
    ])
    scope = models.CharField(max_length=20, choices=[
        ('global', 'Global'),
        ('brand', 'Par brand'),
        ('category', 'Par catégorie'),
        ('template_type', 'Par type')
    ])
    scope_id = models.PositiveIntegerField(null=True, blank=True, help_text="ID de l'entité analysée")
    period_start = models.DateField()
    period_end = models.DateField()
    trend_direction = models.CharField(max_length=20, choices=[
        ('increasing', 'Croissante'),
        ('decreasing', 'Décroissante'),
        ('stable', 'Stable'),
        ('volatile', 'Volatile')
    ])
    trend_strength = models.FloatField(help_text="Force de la tendance 0-1")
    key_findings = models.JSONField(default=dict, help_text="Principales découvertes")
    visualization_data = models.JSONField(default=dict, help_text="Données pour graphiques")
    
    class Meta:
        db_table = 'trend_analysis'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['analysis_type', 'scope']),
            models.Index(fields=['period_start', 'period_end'])
        ]
    
    def __str__(self):
        return f"{self.analysis_type} ({self.scope}) - {self.trend_direction}"
