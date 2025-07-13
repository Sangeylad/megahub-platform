# backend/brands_design_typography/serializers/typography_serializers.py

from rest_framework import serializers
import logging

from common.serializers.mixins import DynamicFieldsSerializer
from common.serializers.mixins import StatsMixin

from ..models import BrandTypography, WebsiteTypographyConfig

logger = logging.getLogger(__name__)

class BrandTypographySerializer(DynamicFieldsSerializer):
    """Serializer typography brand"""
    
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    font_sizes = serializers.SerializerMethodField()
    
    class Meta:
        model = BrandTypography
        fields = [
            'id', 'brand', 'brand_name',
            'font_primary', 'font_secondary', 'font_mono',
            'google_fonts_url', 'base_font_size', 'scale_ratio', 'base_line_height',
            'font_sizes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_font_sizes(self, obj):
        return obj.generate_font_sizes()

class WebsiteTypographyConfigSerializer(DynamicFieldsSerializer):
    """Serializer config typography website"""
    
    website_name = serializers.CharField(source='website.name', read_only=True)
    brand_name = serializers.CharField(source='website.brand.name', read_only=True)
    
    # Valeurs effectives
    effective_font_primary = serializers.SerializerMethodField()
    effective_base_size = serializers.SerializerMethodField()
    effective_scale_ratio = serializers.SerializerMethodField()
    
    class Meta:
        model = WebsiteTypographyConfig
        fields = [
            'id', 'website', 'website_name', 'brand_name',
            'font_primary_override', 'base_font_size_override', 'scale_ratio_override',
            'effective_font_primary', 'effective_base_size', 'effective_scale_ratio',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_effective_font_primary(self, obj):
        return obj.get_effective_font_primary()
    
    def get_effective_base_size(self, obj):
        return obj.get_effective_base_size()
    
    def get_effective_scale_ratio(self, obj):
        return obj.get_effective_scale_ratio()

class WebsiteTypographyConfigDetailSerializer(StatsMixin, WebsiteTypographyConfigSerializer):
    """Serializer détaillé avec échelle générée"""
    
    effective_font_sizes = serializers.SerializerMethodField()
    brand_typography = BrandTypographySerializer(source='website.brand.typography', read_only=True)
    
    class Meta(WebsiteTypographyConfigSerializer.Meta):
        fields = WebsiteTypographyConfigSerializer.Meta.fields + [
            'effective_font_sizes', 'brand_typography'
        ]
    
    def get_effective_font_sizes(self, obj):
        return obj.generate_effective_font_sizes()
