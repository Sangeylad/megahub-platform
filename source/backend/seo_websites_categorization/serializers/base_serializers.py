# backend/seo_websites_categorization/serializers/base_serializers.py

from rest_framework import serializers

class SeoWebsitesCategorizationBaseSerializer(serializers.ModelSerializer):
    """Classe abstraite de base pour tous les serializers seo_websites_categorization"""
    
    class Meta:
        abstract = True