# backend/ai_openai/serializers/openai_serializers.py

from rest_framework import serializers
from decimal import Decimal  # 🆕 Import nécessaire
from common.serializers.mixins import DynamicFieldsSerializer
from ..models import OpenAIJob

class ChatCompletionSerializer(serializers.Serializer):
    """Serializer pour requête chat completion multi-modèles"""
    messages = serializers.ListField()
    model = serializers.CharField(default='gpt-4o')
    
    # Paramètres legacy - 🔧 CORRECTION des validators
    temperature = serializers.FloatField(
        required=False, 
        min_value=Decimal('0.0'),   # 🆕 Decimal au lieu d'int
        max_value=Decimal('2.0')    # 🆕 Decimal au lieu d'int
    )
    max_tokens = serializers.IntegerField(
        required=False,
        min_value=1,               # int OK pour IntegerField
        max_value=100000           # int OK pour IntegerField
    )
    
    # 🆕 NOUVEAUX PARAMÈTRES O3/GPT-4.1
    reasoning_effort = serializers.ChoiceField(
        choices=['low', 'medium', 'high'],
        required=False
    )
    max_completion_tokens = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=100000
    )
    
    # Paramètres communs
    description = serializers.CharField(required=False, max_length=500)
    tools = serializers.ListField(required=False)
    tool_resources = serializers.DictField(required=False)
    response_format = serializers.DictField(required=False)
    
    def validate(self, data):
        """Validation selon le modèle"""
        model = data.get('model', 'gpt-4o')
        
        # Validation O3
        if model.startswith('o3'):
            if 'temperature' in data:
                raise serializers.ValidationError(
                    "O3 models don't support temperature parameter"
                )
            if not data.get('reasoning_effort'):
                data['reasoning_effort'] = 'medium'
            
            # O3 utilise max_completion_tokens
            if 'max_tokens' in data and 'max_completion_tokens' not in data:
                data['max_completion_tokens'] = data.pop('max_tokens')
        
        # Validation gpt-4.1
        elif model == 'gpt-4.1':
            if not data.get('temperature'):
                data['temperature'] = 1.0
        
        # Validation legacy
        else:
            if 'reasoning_effort' in data:
                raise serializers.ValidationError(
                    f"Model {model} doesn't support reasoning_effort parameter"
                )
            if not data.get('temperature'):
                data['temperature'] = 0.7
        
        return data

class OpenAIJobSerializer(DynamicFieldsSerializer):
    """Serializer job OpenAI avec nouveaux champs"""
    ai_job_id = serializers.CharField(source='ai_job.job_id', read_only=True)
    ai_job_status = serializers.CharField(source='ai_job.status', read_only=True)
    is_new_generation = serializers.BooleanField(source='is_new_generation_model', read_only=True)
    
    class Meta:
        model = OpenAIJob
        fields = '__all__'
        read_only_fields = [
            'openai_id', 'completion_tokens', 'prompt_tokens', 
            'total_tokens', 'assistant_id', 'thread_id', 'run_id',
            'messages_format'
        ]