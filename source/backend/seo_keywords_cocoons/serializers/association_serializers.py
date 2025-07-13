# backend/seo_keywords_cocoons/serializers/association_serializers.py

from rest_framework import serializers

# Local imports
from ..models import CocoonKeyword


class CocoonKeywordSerializer(serializers.ModelSerializer):
    """Serializer pour associations cocoon-keyword"""
    
    cocoon_name = serializers.CharField(source='cocoon.name', read_only=True)
    keyword_text = serializers.CharField(source='keyword.keyword', read_only=True)
    keyword_volume = serializers.IntegerField(source='keyword.volume', read_only=True)
    
    class Meta:
        model = CocoonKeyword
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class CocoonKeywordListSerializer(serializers.ModelSerializer):
    """Serializer optimisé pour liste"""
    
    cocoon_name = serializers.CharField(source='cocoon.name', read_only=True)
    keyword_text = serializers.CharField(source='keyword.keyword', read_only=True)
    keyword_volume = serializers.IntegerField(source='keyword.volume', read_only=True)
    
    class Meta:
        model = CocoonKeyword
        fields = ['id', 'cocoon_name', 'keyword_text', 'keyword_volume', 'created_at']