# backend/seo_pages_hierarchy/serializers/base_serializers.py

from rest_framework import serializers

class PageHierarchyBaseSerializer(serializers.ModelSerializer):
    """Classe abstraite de base pour tous les serializers seo_pages_hierarchy"""
    
    class Meta:
        abstract = True
