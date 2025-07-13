# backend/brands_design_spacing/serializers/spacing_serializers.py

from rest_framework import serializers
import logging

from common.serializers.mixins import DynamicFieldsSerializer
from common.serializers.mixins import StatsMixin

from ..models import BrandSpacingSystem, WebsiteLayoutConfig

logger = logging.getLogger(__name__)

class BrandSpacingSystemSerializer(DynamicFieldsSerializer):
    """Serializer spacing system brand"""
    
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    spacing_scale_values = serializers.SerializerMethodField()
    breakpoints = serializers.SerializerMethodField()
    
    class Meta:
        model = BrandSpacingSystem
        fields = [
            'id', 'brand', 'brand_name',
            'base_unit', 'spacing_scale', 'max_width', 'container_padding',
            'grid_columns', 'grid_gap',
            'breakpoint_sm', 'breakpoint_md', 'breakpoint_lg', 'breakpoint_xl',
            'spacing_scale_values', 'breakpoints',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_spacing_scale_values(self, obj):
        return obj.generate_spacing_scale()
    
    def get_breakpoints(self, obj):
        return {
            'sm': f"{obj.breakpoint_sm}px",
            'md': f"{obj.breakpoint_md}px", 
            'lg': f"{obj.breakpoint_lg}px",
            'xl': f"{obj.breakpoint_xl}px",
        }

class WebsiteLayoutConfigSerializer(DynamicFieldsSerializer):
    """Serializer layout config website"""
    
    website_name = serializers.CharField(source='website.name', read_only=True)
    brand_name = serializers.CharField(source='website.brand.name', read_only=True)
    
    # Valeurs effectives
    effective_max_width = serializers.SerializerMethodField()
    effective_grid_columns = serializers.SerializerMethodField()
    
    class Meta:
        model = WebsiteLayoutConfig
        fields = [
            'id', 'website', 'website_name', 'brand_name',
            'max_width_override', 'grid_columns_override',
            'sidebar_width', 'header_height', 'footer_height', 'nav_collapse_breakpoint',
            'effective_max_width', 'effective_grid_columns',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_effective_max_width(self, obj):
        return obj.get_effective_max_width()
    
    def get_effective_grid_columns(self, obj):
        return obj.get_effective_grid_columns()

class WebsiteLayoutConfigDetailSerializer(StatsMixin, WebsiteLayoutConfigSerializer):
    """Serializer détaillé avec spacing system"""
    
    brand_spacing = BrandSpacingSystemSerializer(source='website.brand.spacing_system', read_only=True)
    
    class Meta(WebsiteLayoutConfigSerializer.Meta):
        fields = WebsiteLayoutConfigSerializer.Meta.fields + [
            'brand_spacing'
        ]
