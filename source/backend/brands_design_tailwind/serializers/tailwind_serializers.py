# backend/brands_design_tailwind/serializers/tailwind_serializers.py

from rest_framework import serializers
import logging

from common.serializers.mixins import DynamicFieldsSerializer

from ..models import WebsiteTailwindConfig, TailwindThemeExport

logger = logging.getLogger(__name__)

class WebsiteTailwindConfigSerializer(DynamicFieldsSerializer):
    """Serializer config Tailwind website"""
    
    website_name = serializers.CharField(source='website.name', read_only=True)
    brand_name = serializers.CharField(source='website.brand.name', read_only=True)
    
    class Meta:
        model = WebsiteTailwindConfig
        fields = [
            'id', 'website', 'website_name', 'brand_name',
            'tailwind_config', 'css_variables', 'config_hash',
            'last_generated_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'config_hash', 'last_generated_at', 'created_at', 'updated_at']

class TailwindThemeExportSerializer(DynamicFieldsSerializer):
    """Serializer exports Tailwind"""
    
    website_name = serializers.CharField(source='website.name', read_only=True)
    
    class Meta:
        model = TailwindThemeExport
        fields = [
            'id', 'website', 'website_name', 'export_type',
            'content', 'file_hash', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'file_hash', 'created_at', 'updated_at']
