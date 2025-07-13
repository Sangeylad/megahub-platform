# backend/seo_pages_layout/serializers/base_serializers.py

from rest_framework import serializers

class PageLayoutBaseSerializer(serializers.ModelSerializer):
    """Classe abstraite de base pour tous les serializers seo_pages_layout"""
    
    class Meta:
        abstract = True
