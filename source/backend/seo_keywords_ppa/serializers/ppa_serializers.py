# backend/seo_keywords_ppa/serializers/ppa_serializers.py

from rest_framework import serializers

# Common - avec fallback
try:
    from common.serializers.mixins import TimestampedSerializer
except ImportError:
    TimestampedSerializer = serializers.ModelSerializer

# Local imports
from ..models import PPA, KeywordPPA


class PPAListSerializer(serializers.ModelSerializer):
    """Serializer optimisé pour liste PPA"""
    
    keywords_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = PPA
        fields = ['id', 'question', 'keywords_count', 'created_at']


class PPASerializer(TimestampedSerializer):
    """Serializer complet pour PPA"""
    
    keywords_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = PPA
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class KeywordPPASerializer(TimestampedSerializer):
    """Serializer pour associations keyword-PPA"""
    
    keyword_text = serializers.CharField(source='keyword.keyword', read_only=True)
    keyword_volume = serializers.IntegerField(source='keyword.volume', read_only=True)
    ppa_question = serializers.CharField(source='ppa.question', read_only=True)
    
    class Meta:
        model = KeywordPPA
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_position(self, value):
        """Validation position entre 1 et 4"""
        if value < 1 or value > 4:
            raise serializers.ValidationError("Position must be between 1 and 4")
        return value


class KeywordPPAListSerializer(serializers.ModelSerializer):
    """Serializer optimisé pour liste associations"""
    
    keyword_text = serializers.CharField(source='keyword.keyword', read_only=True)
    ppa_question = serializers.CharField(source='ppa.question', read_only=True)
    
    class Meta:
        model = KeywordPPA
        fields = ['id', 'keyword_text', 'ppa_question', 'position', 'created_at']