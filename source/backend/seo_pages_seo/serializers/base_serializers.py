# backend/seo_pages_seo/serializers/base_serializers.py

from rest_framework import serializers

class PageSeoBaseSerializer(serializers.ModelSerializer):
    """Classe abstraite de base pour tous les serializers seo_pages_seo"""
    
    class Meta:
        abstract = True
