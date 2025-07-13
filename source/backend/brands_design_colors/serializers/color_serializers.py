# backend/brands_design_colors/serializers/color_serializers.py

from rest_framework import serializers
import logging

from common.serializers.mixins import DynamicFieldsSerializer
from common.serializers.mixins import StatsMixin

from ..models import BrandColorPalette, WebsiteColorConfig

logger = logging.getLogger(__name__)

class BrandColorPaletteSerializer(DynamicFieldsSerializer):
    """Serializer palette couleurs brand"""
    
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    
    class Meta:
        model = BrandColorPalette
        fields = [
            'id', 'brand', 'brand_name',
            'primary_color', 'secondary_color', 'accent_color',
            'neutral_dark', 'neutral_light',
            'success_color', 'warning_color', 'error_color',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class WebsiteColorConfigSerializer(DynamicFieldsSerializer):
    """Serializer config couleurs website"""
    
    website_name = serializers.CharField(source='website.name', read_only=True)
    brand_name = serializers.CharField(source='website.brand.name', read_only=True)
    
    # Couleurs effectives (avec fallback)
    effective_primary = serializers.SerializerMethodField()
    effective_secondary = serializers.SerializerMethodField()
    effective_accent = serializers.SerializerMethodField()
    
    class Meta:
        model = WebsiteColorConfig
        fields = [
            'id', 'website', 'website_name', 'brand_name',
            'primary_override', 'secondary_override', 'accent_override',
            'effective_primary', 'effective_secondary', 'effective_accent',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_effective_primary(self, obj):
        return obj.get_effective_primary()
    
    def get_effective_secondary(self, obj):
        return obj.get_effective_secondary()
    
    def get_effective_accent(self, obj):
        return obj.get_effective_accent()

class WebsiteColorConfigDetailSerializer(StatsMixin, WebsiteColorConfigSerializer):
    """Serializer détaillé avec CSS variables"""
    
    css_variables = serializers.SerializerMethodField()
    brand_palette = BrandColorPaletteSerializer(source='website.brand.color_palette', read_only=True)
    
    class Meta(WebsiteColorConfigSerializer.Meta):
        fields = WebsiteColorConfigSerializer.Meta.fields + [
            'css_variables', 'brand_palette'
        ]
    
    def get_css_variables(self, obj):
        return obj.to_css_variables()
