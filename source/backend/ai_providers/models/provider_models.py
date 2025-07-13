# backend/ai_providers/models/provider_models.py

from django.db import models
from django.contrib.auth.models import User
from common.models.mixins import TimestampedMixin

class AIProvider(TimestampedMixin):
    """Providers IA disponibles"""
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    base_url = models.URLField()
    
    # Capabilities
    supports_chat = models.BooleanField(default=True)
    supports_assistants = models.BooleanField(default=False)
    supports_files = models.BooleanField(default=False)
    supports_vision = models.BooleanField(default=False)
    
    # Config
    default_model = models.CharField(max_length=100)
    available_models = models.JSONField(default=list)
    rate_limit_rpm = models.IntegerField(default=60)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'ai_provider'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.display_name

class AICredentials(TimestampedMixin):
    """Extension Company pour credentials IA"""
    company = models.OneToOneField(
        'company_core.Company',
        on_delete=models.CASCADE,
        related_name='ai_credentials'
    )
    
    # Credentials chiffrées par provider
    openai_api_key = models.TextField(blank=True)
    anthropic_api_key = models.TextField(blank=True)
    google_api_key = models.TextField(blank=True)
    
    # Fallback settings global
    use_global_fallback = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'ai_credentials'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Credentials {self.company.name}"

class AIQuota(TimestampedMixin):
    """Quotas et limites par company/provider"""
    company = models.ForeignKey('company_core.Company', on_delete=models.CASCADE)
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE)
    
    # Limites mensuelles
    monthly_token_limit = models.IntegerField(default=1000000)
    monthly_cost_limit = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    
    # Compteurs actuels
    current_tokens_used = models.IntegerField(default=0)
    current_cost_used = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Reset automatique
    last_reset_date = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_quota'
        unique_together = ['company', 'provider']
    
    def __str__(self):
        return f"Quota {self.company.name} - {self.provider.name}"
