# backend/ai_providers/serializers/provider_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer

from ..models import AIProvider, AICredentials, AIQuota

class AIProviderSerializer(DynamicFieldsSerializer):
    """Serializer providers IA"""
    
    class Meta:
        model = AIProvider
        fields = '__all__'

class AICredentialsSerializer(DynamicFieldsSerializer):
    """Serializer credentials - write only keys"""
    openai_api_key = serializers.CharField(write_only=True, required=False)
    anthropic_api_key = serializers.CharField(write_only=True, required=False)
    google_api_key = serializers.CharField(write_only=True, required=False)
    
    has_openai = serializers.SerializerMethodField()
    has_anthropic = serializers.SerializerMethodField()
    has_google = serializers.SerializerMethodField()
    
    class Meta:
        model = AICredentials
        fields = [
            'company', 'use_global_fallback',
            'openai_api_key', 'anthropic_api_key', 'google_api_key',
            'has_openai', 'has_anthropic', 'has_google'
        ]
        read_only_fields = ['company']
    
    def get_has_openai(self, obj):
        return bool(obj.openai_api_key)
    
    def get_has_anthropic(self, obj):
        return bool(obj.anthropic_api_key)
    
    def get_has_google(self, obj):
        return bool(obj.google_api_key)
