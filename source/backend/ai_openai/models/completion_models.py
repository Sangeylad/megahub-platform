# backend/ai_openai/models/completion_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class OpenAICompletion(TimestampedMixin):
    """Extension OneToOne pour jobs OpenAI completion"""
    
    # Relation vers AIJob
    ai_job = models.OneToOneField(
        'ai_core.AIJob',
        on_delete=models.CASCADE,
        related_name='openai_completion'
    )
    
    # Paramètres OpenAI
    model = models.CharField(max_length=50, default="gpt-4o")
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(null=True, blank=True)
    
    # Messages et prompts
    messages = models.JSONField(default=list)
    system_prompt = models.TextField(blank=True)
    
    # Tools et resources
    tools = models.JSONField(default=list, blank=True)
    tool_resources = models.JSONField(default=dict, blank=True)
    
    # Réponse OpenAI
    openai_response = models.JSONField(default=dict, blank=True)
    completion_text = models.TextField(blank=True)
    
    # Identifiants OpenAI
    openai_request_id = models.CharField(max_length=100, blank=True)
    assistant_id = models.CharField(max_length=100, blank=True)
    thread_id = models.CharField(max_length=100, blank=True)
    run_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'openai_completion'
        verbose_name = "Completion OpenAI"
        verbose_name_plural = "Completions OpenAI"
    
    def __str__(self):
        return f"OpenAI {self.model} - Job {self.ai_job.job_id}"
