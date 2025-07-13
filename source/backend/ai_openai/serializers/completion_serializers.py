# backend/ai_openai/serializers/completion_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer
from ..models import OpenAICompletion

class OpenAICompletionSerializer(DynamicFieldsSerializer):
    """Serializer pour les completions OpenAI"""
    
    # Relations
    job_id = serializers.CharField(source='ai_job.job_id', read_only=True)
    job_status = serializers.CharField(source='ai_job.status', read_only=True)
    brand_name = serializers.CharField(source='ai_job.brand.name', read_only=True)
    
    # Usage (si disponible)
    tokens_used = serializers.SerializerMethodField()
    cost_usd = serializers.SerializerMethodField()
    
    class Meta:
        model = OpenAICompletion
        fields = [
            'id', 'job_id', 'job_status', 'brand_name',
            'model', 'temperature', 'max_tokens',
            'completion_text', 'tokens_used', 'cost_usd',
            'openai_request_id', 'assistant_id', 'thread_id',
            'created_at', 'updated_at'
        ]
    
    def get_tokens_used(self, obj):
        """Récupère les tokens utilisés depuis l'usage"""
        if hasattr(obj.ai_job, 'openai_usage'):
            return obj.ai_job.openai_usage.total_tokens
        return None
    
    def get_cost_usd(self, obj):
        """Récupère le coût depuis l'usage"""
        if hasattr(obj.ai_job, 'openai_usage'):
            return float(obj.ai_job.openai_usage.cost_usd)
        return None
