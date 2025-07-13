# backend/brands_design_spacing/models/spacing_models.py

from django.db import models
import logging

from common.models.mixins import TimestampedMixin

logger = logging.getLogger(__name__)

class BrandSpacingSystem(TimestampedMixin):
    """Système d'espacement centralisé pour une marque"""
    
    brand = models.OneToOneField(
        'brands_core.Brand',
        on_delete=models.CASCADE,
        related_name='spacing_system'
    )
    
    # Base spacing unit
    base_unit = models.IntegerField(
        default=8,
        help_text="Unité de base en px (4, 8, 16)"
    )
    spacing_scale = models.FloatField(
        default=1.0,
        help_text="Multiplicateur d'espacement (0.8-1.2)"
    )
    
    # Container rules
    max_width = models.CharField(
        max_length=20,
        default="1200px",
        help_text="Largeur max container"
    )
    container_padding = models.IntegerField(
        default=24,
        help_text="Padding container en px"
    )
    
    # Grid system
    grid_columns = models.IntegerField(
        default=12,
        help_text="Nombre de colonnes grid"
    )
    grid_gap = models.IntegerField(
        default=24,
        help_text="Espacement entre colonnes en px"
    )
    
    # Breakpoints
    breakpoint_sm = models.IntegerField(default=640)
    breakpoint_md = models.IntegerField(default=768)
    breakpoint_lg = models.IntegerField(default=1024)
    breakpoint_xl = models.IntegerField(default=1280)
    
    def generate_spacing_scale(self):
        """Génère échelle d'espacement"""
        base = self.base_unit * self.spacing_scale
        
        return {
            '0': '0px',
            '1': f"{round(base * 0.25)}px",
            '2': f"{round(base * 0.5)}px", 
            '3': f"{round(base * 0.75)}px",
            '4': f"{round(base)}px",
            '5': f"{round(base * 1.25)}px",
            '6': f"{round(base * 1.5)}px",
            '8': f"{round(base * 2)}px",
            '10': f"{round(base * 2.5)}px",
            '12': f"{round(base * 3)}px",
            '16': f"{round(base * 4)}px",
            '20': f"{round(base * 5)}px",
            '24': f"{round(base * 6)}px",
            '32': f"{round(base * 8)}px",
        }
    
    def __str__(self):
        return f"Spacing {self.brand.name}"
    
    class Meta:
        db_table = 'brands_design_spacing_brand'
        verbose_name = "Système Espacement"
        verbose_name_plural = "Systèmes Espacement"

class WebsiteLayoutConfig(TimestampedMixin):
    """Configuration layout spécifique à un website (extension)"""
    
    website = models.OneToOneField(
        'seo_websites_core.Website',
        on_delete=models.CASCADE,
        related_name='layout_config'
    )
    
    # Container overrides
    max_width_override = models.CharField(
        max_length=20, 
        blank=True,
        help_text="Override largeur max pour ce site"
    )
    grid_columns_override = models.IntegerField(
        null=True, 
        blank=True,
        help_text="Override nombre colonnes pour ce site"
    )
    
    # Layout preferences spécifiques website
    sidebar_width = models.IntegerField(
        default=280,
        help_text="Largeur sidebar en px"
    )
    header_height = models.IntegerField(
        default=80,
        help_text="Hauteur header en px"
    )
    footer_height = models.IntegerField(
        default=120,
        help_text="Hauteur footer en px"
    )
    
    # Navigation preferences
    nav_collapse_breakpoint = models.CharField(
        max_length=10,
        default="md",
        choices=[
            ('sm', 'Small (640px)'),
            ('md', 'Medium (768px)'),
            ('lg', 'Large (1024px)'),
        ],
        help_text="Breakpoint collapse navigation"
    )
    
    def get_effective_max_width(self):
        """Largeur max effective (override ou brand)"""
        if self.max_width_override:
            return self.max_width_override
        return self.website.brand.spacing_system.max_width
    
    def get_effective_grid_columns(self):
        """Colonnes grid effectives (override ou brand)"""
        if self.grid_columns_override:
            return self.grid_columns_override
        return self.website.brand.spacing_system.grid_columns
    
    def __str__(self):
        return f"Layout {self.website.name}"
    
    class Meta:
        db_table = 'brands_design_spacing_website'
        verbose_name = "Configuration Layout Website"
        verbose_name_plural = "Configurations Layout Websites"
