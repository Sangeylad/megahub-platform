# backend/seo_pages_content/serializers/base_serializers.py

from rest_framework import serializers

class PageContentBaseSerializer(serializers.ModelSerializer):
    """Classe abstraite de base pour tous les serializers seo_pages_content"""
    
    class Meta:
        abstract = True
