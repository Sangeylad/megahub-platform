# backend/seo_websites_core/serializers/base_serializers.py

from rest_framework import serializers

class WebsiteCoreBaseSerializer(serializers.ModelSerializer):
    """Classe abstraite de base pour tous les serializers seo_websites_core"""
    
    class Meta:
        abstract = True
