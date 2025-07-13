# backend/ai_templates_analytics/models/analytics_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class TemplateUsageMetrics(TimestampedMixin):
    """Métriques d'utilisation des templates"""
    template = models.OneToOneField('ai_templates_core.BaseTemplate', on_delete=models.CASCADE, related_name='usage_metrics')
    total_uses = models.PositiveIntegerField(default=0)
    successful_generations = models.PositiveIntegerField(default=0)
    failed_generations = models.PositiveIntegerField(default=0)
    unique_users = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    avg_generation_time = models.FloatField(default=0.0, help_text="Temps moyen de génération (secondes)")
    popularity_score = models.FloatField(default=0.0, help_text="Score de popularité calculé")
    
    class Meta:
        db_table = 'template_usage_metrics'
    
    def __str__(self):
        return f"Métriques {self.template.name}: {self.total_uses} utilisations"
    
    @property
    def success_rate(self):
        """Taux de succès en pourcentage"""
        if self.total_uses == 0:
            return 0
        return (self.successful_generations / self.total_uses) * 100

class TemplatePerformance(TimestampedMixin):
    """Performance détaillée des templates"""
    template = models.ForeignKey('ai_templates_core.BaseTemplate', on_delete=models.CASCADE, related_name='performance_logs')
    user = models.ForeignKey('users_core.CustomUser', on_delete=models.CASCADE)
    generation_time = models.FloatField(help_text="Temps de génération (secondes)")
    tokens_used = models.PositiveIntegerField(default=0)
    output_quality_score = models.FloatField(null=True, blank=True, help_text="Score qualité 0-10")
    variables_used = models.JSONField(default=dict, help_text="Variables utilisées pour cette génération")
    was_successful = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'template_performance'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['template', 'was_successful']),
            models.Index(fields=['user', 'created_at'])
        ]
    
    def __str__(self):
        status = "✅" if self.was_successful else "❌"
        return f"{status} {self.template.name} - {self.generation_time}s"

class TemplatePopularity(TimestampedMixin):
    """Classements de popularité par catégorie/brand"""
    template = models.ForeignKey('ai_templates_core.BaseTemplate', on_delete=models.CASCADE, related_name='popularity_rankings')
    category = models.ForeignKey('ai_templates_categories.TemplateCategory', on_delete=models.CASCADE, null=True, blank=True)
    brand = models.ForeignKey('brands_core.Brand', on_delete=models.CASCADE)
    ranking_period = models.CharField(max_length=20, choices=[
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
        ('yearly', 'Annuel')
    ])
    rank_position = models.PositiveIntegerField()
    usage_count = models.PositiveIntegerField()
    period_start = models.DateField()
    period_end = models.DateField()
    
    class Meta:
        db_table = 'template_popularity'
        ordering = ['ranking_period', 'rank_position']
        indexes = [
            models.Index(fields=['brand', 'ranking_period', 'period_start']),
            models.Index(fields=['category', 'ranking_period'])
        ]
        unique_together = ['template', 'ranking_period', 'period_start', 'brand']
    
    def __str__(self):
        return f"#{self.rank_position} {self.template.name} ({self.ranking_period})"

class TemplateFeedback(TimestampedMixin):
    """Notes et commentaires utilisateurs"""
    template = models.ForeignKey('ai_templates_core.BaseTemplate', on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey('users_core.CustomUser', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    feedback_type = models.CharField(max_length=20, choices=[
        ('quality', 'Qualité'),
        ('ease_of_use', 'Facilité d\'usage'),
        ('relevance', 'Pertinence'),
        ('bug_report', 'Bug'),
        ('suggestion', 'Suggestion')
    ])
    is_public = models.BooleanField(default=False, help_text="Commentaire visible publiquement")
    admin_response = models.TextField(blank=True)
    
    class Meta:
        db_table = 'template_feedback'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['template', 'rating']),
            models.Index(fields=['feedback_type', 'is_public'])
        ]
        unique_together = ['template', 'user']  # Un feedback par user/template
    
    def __str__(self):
        return f"{self.rating}⭐ {self.template.name} par {self.user.username}"
