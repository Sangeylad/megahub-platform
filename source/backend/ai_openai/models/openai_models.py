# backend/ai_openai/models/openai_models.py

from django.db import models
from common.models.mixins import TimestampedMixin
from django.core.validators import MinValueValidator, MaxValueValidator  # 🆕 Import manquant


class OpenAIJob(TimestampedMixin):
    """Extension spécialisée OpenAI pour AIJob"""
    ai_job = models.OneToOneField(
        'ai_core.AIJob',
        on_delete=models.CASCADE,
        related_name='openai_job'
    )
    
    # Config OpenAI
    model = models.CharField(max_length=50, default='gpt-4o')
    temperature = models.FloatField(
        null=True, blank=True,  # 🆕 Permettre NULL
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0)],
        help_text="Temperature entre 0.0 et 2.0. NULL pour O3."
    )
    

    max_tokens = models.IntegerField(null=True, blank=True)
    
    # 🆕 NOUVEAUX PARAMÈTRES O3
    reasoning_effort = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        null=True, blank=True,
        help_text="Effort de raisonnement pour O3"
    )
    max_completion_tokens = models.IntegerField(null=True, blank=True)
    
    # 🆕 FORMAT DE MESSAGES FLEXIBLE
    messages = models.JSONField(default=list)
    messages_format = models.CharField(
        max_length=20,
        choices=[('legacy', 'Legacy'), ('structured', 'Structured')],
        default='legacy'
    )
    
    # Tools et response format
    tools = models.JSONField(default=list, blank=True)
    tool_resources = models.JSONField(default=dict, blank=True)
    response_format = models.JSONField(default=dict, blank=True)
    
    # Response OpenAI
    openai_id = models.CharField(max_length=100, blank=True)
    completion_tokens = models.IntegerField(default=0)
    prompt_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    
    # Assistants specifique
    assistant_id = models.CharField(max_length=100, blank=True)
    thread_id = models.CharField(max_length=100, blank=True)
    run_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'openai_job'
        ordering = ['-created_at'] 
    
    def __str__(self):
        return f"OpenAI {self.ai_job.job_id}"
    
    @property
    def is_o3_model(self):
        """Détecte si c'est un modèle O3"""
        return self.model.startswith('o3')
    
    @property
    def is_new_generation_model(self):
        """Détecte si c'est un modèle nouvelle génération (o3, gpt-4.1)"""
        return self.model.startswith('o3') or self.model in ['gpt-4.1']

class OpenAIConfig(TimestampedMixin):
    """Configuration globale OpenAI"""
    name = models.CharField(max_length=100, unique=True)
    base_url = models.URLField(default='https://api.openai.com')
    timeout_seconds = models.IntegerField(default=300)
    max_retries = models.IntegerField(default=3)
    
    # Models disponibles
    available_models = models.JSONField(default=list)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'openai_config'
    
    def __str__(self):
        return self.name
