# backend/ai_openai/models/usage_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class OpenAIUsage(TimestampedMixin):
    """Extension OneToOne pour tracking usage OpenAI"""
    
    # Relation vers AIJob
    ai_job = models.OneToOneField(
        'ai_core.AIJob',
        on_delete=models.CASCADE,
        related_name='openai_usage'
    )
    
    # Tokens
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    
    # Coûts
    cost_usd = models.DecimalField(max_digits=10, decimal_places=4, default=0.0000)
    
    # Métriques
    execution_time_ms = models.IntegerField(default=0)
    api_calls_count = models.IntegerField(default=1)
    
    # Rate limiting
    requests_per_minute = models.IntegerField(null=True, blank=True)
    tokens_per_minute = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'openai_usage'
        verbose_name = "Usage OpenAI"
        verbose_name_plural = "Usages OpenAI"
        indexes = [
            models.Index(fields=['created_at', 'cost_usd']),
        ]
    
    def __str__(self):
        return f"Usage OpenAI - {self.total_tokens} tokens (${self.cost_usd})"
    
    @property
    def cost_per_token(self):
        """Coût par token"""
        if self.total_tokens > 0:
            return float(self.cost_usd) / self.total_tokens
        return 0
