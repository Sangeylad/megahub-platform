# backend/seo_pages_workflow/serializers/base_serializers.py

from rest_framework import serializers

class PageWorkflowBaseSerializer(serializers.ModelSerializer):
    """Classe abstraite de base pour tous les serializers seo_pages_workflow"""
    
    class Meta:
        abstract = True
