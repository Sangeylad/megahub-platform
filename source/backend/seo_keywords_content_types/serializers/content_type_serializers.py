# backend/seo_keywords_content_types/serializers/content_type_serializers.py

from rest_framework import serializers

# Common - avec fallback
try:
    from common.serializers.mixins import TimestampedSerializer
except ImportError:
    TimestampedSerializer = serializers.ModelSerializer

# Local imports
from ..models import ContentType, KeywordContentType


class ContentTypeListSerializer(serializers.ModelSerializer):
    """Serializer optimisé pour liste des types de contenu"""
    
    keywords_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ContentType
        fields = ['id', 'name', 'description', 'keywords_count', 'created_at']


class ContentTypeSerializer(TimestampedSerializer):
    """Serializer complet pour types de contenu"""
    
    keywords_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ContentType
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class KeywordContentTypeListSerializer(serializers.ModelSerializer):
    """Serializer optimisé pour liste associations"""
    
    keyword_text = serializers.CharField(source='keyword.keyword', read_only=True)
    keyword_volume = serializers.IntegerField(source='keyword.volume', read_only=True)
    content_type_name = serializers.CharField(source='content_type.name', read_only=True)
    
    class Meta:
        model = KeywordContentType
        fields = ['id', 'keyword_text', 'keyword_volume', 'content_type_name', 'priority', 'created_at']


class KeywordContentTypeSerializer(TimestampedSerializer):
    """Serializer pour associations keyword-content type"""
    
    keyword_text = serializers.CharField(source='keyword.keyword', read_only=True)
    keyword_volume = serializers.IntegerField(source='keyword.volume', read_only=True)
    content_type_name = serializers.CharField(source='content_type.name', read_only=True)
    
    class Meta:
        model = KeywordContentType
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_priority(self, value):
        """Validation priorité positive"""
        if value < 0:
            raise serializers.ValidationError("Priority must be >= 0")
        return value