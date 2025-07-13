# backend/seo_pages_keywords/serializers/base_serializers.py

from rest_framework import serializers

class PageKeywordsBaseSerializer(serializers.ModelSerializer):
    """Classe abstraite de base pour tous les serializers seo_pages_keywords"""
    
    class Meta:
        abstract = True
