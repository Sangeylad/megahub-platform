# backend/brands_design_colors/models/color_models.py

from django.db import models
import logging

from common.models.mixins import TimestampedMixin

logger = logging.getLogger(__name__)

class BrandColorPalette(TimestampedMixin):
    """Palette de couleurs centralisée pour une marque"""
    
    brand = models.OneToOneField(
        'brands_core.Brand',
        on_delete=models.CASCADE,
        related_name='color_palette'
    )
    
    # Base colors
    primary_color = models.CharField(
        max_length=7,
        help_text="Couleur primaire (ex: #FF6B35)"
    )
    secondary_color = models.CharField(
        max_length=7,
        help_text="Couleur secondaire (ex: #F7931E)"
    )
    accent_color = models.CharField(
        max_length=7,
        help_text="Couleur d'accent (ex: #FFD23F)"
    )
    
    # UI colors
    neutral_dark = models.CharField(
        max_length=7,
        default="#1A1A1A",
        help_text="Couleur neutre sombre"
    )
    neutral_light = models.CharField(
        max_length=7,
        default="#F8F9FA",
        help_text="Couleur neutre claire"
    )
    
    # Status colors
    success_color = models.CharField(max_length=7, default="#10B981")
    warning_color = models.CharField(max_length=7, default="#F59E0B")
    error_color = models.CharField(max_length=7, default="#EF4444")
    
    def to_css_variables(self):
        """Génère les variables CSS"""
        return {
            '--color-primary': self.primary_color,
            '--color-secondary': self.secondary_color,
            '--color-accent': self.accent_color,
            '--color-neutral-dark': self.neutral_dark,
            '--color-neutral-light': self.neutral_light,
            '--color-success': self.success_color,
            '--color-warning': self.warning_color,
            '--color-error': self.error_color,
        }
    
    def __str__(self):
        return f"Palette {self.brand.name}"
    
    class Meta:
        db_table = 'brands_design_colors_palette'
        verbose_name = "Palette de Couleurs"
        verbose_name_plural = "Palettes de Couleurs"

class WebsiteColorConfig(TimestampedMixin):
    """Configuration couleurs spécifique à un website (extension)"""
    
    website = models.OneToOneField(
        'seo_websites_core.Website',
        on_delete=models.CASCADE,
        related_name='color_config'
    )
    
    # Overrides optionnels (fallback sur brand palette)
    primary_override = models.CharField(
        max_length=7, 
        blank=True,
        help_text="Override couleur primaire pour ce site"
    )
    secondary_override = models.CharField(
        max_length=7, 
        blank=True,
        help_text="Override couleur secondaire pour ce site"
    )
    accent_override = models.CharField(
        max_length=7, 
        blank=True,
        help_text="Override couleur accent pour ce site"
    )
    
    def get_effective_primary(self):
        """Couleur primaire effective (override ou brand)"""
        if self.primary_override:
            return self.primary_override
        return self.website.brand.color_palette.primary_color
    
    def get_effective_secondary(self):
        """Couleur secondaire effective (override ou brand)"""
        if self.secondary_override:
            return self.secondary_override
        return self.website.brand.color_palette.secondary_color
    
    def get_effective_accent(self):
        """Couleur accent effective (override ou brand)"""
        if self.accent_override:
            return self.accent_override
        return self.website.brand.color_palette.accent_color
    
    def to_css_variables(self):
        """Variables CSS avec overrides appliqués"""
        brand_vars = self.website.brand.color_palette.to_css_variables()
        brand_vars.update({
            '--color-primary': self.get_effective_primary(),
            '--color-secondary': self.get_effective_secondary(),
            '--color-accent': self.get_effective_accent(),
        })
        return brand_vars
    
    def __str__(self):
        return f"Colors {self.website.name}"
    
    class Meta:
        db_table = 'brands_design_colors_website'
        verbose_name = "Configuration Couleurs Website"
        verbose_name_plural = "Configurations Couleurs Websites"
