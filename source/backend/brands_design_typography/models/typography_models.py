# backend/brands_design_typography/models/typography_models.py

from django.db import models
import logging

from common.models.mixins import TimestampedMixin

logger = logging.getLogger(__name__)

class BrandTypography(TimestampedMixin):
    """Configuration typographique centralisée pour une marque"""
    
    brand = models.OneToOneField(
        'brands_core.Brand',
        on_delete=models.CASCADE,
        related_name='typography'
    )
    
    # Font families
    font_primary = models.CharField(
        max_length=100,
        help_text="Font principale (ex: Inter, Roboto)"
    )
    font_secondary = models.CharField(
        max_length=100,
        blank=True,
        help_text="Font secondaire (ex: Roboto Slab)"
    )
    font_mono = models.CharField(
        max_length=100,
        default="Fira Code",
        help_text="Font monospace pour code"
    )
    
    # Google Fonts integration
    google_fonts_url = models.URLField(
        blank=True,
        help_text="URL Google Fonts à charger"
    )
    
    # Typography scale
    base_font_size = models.IntegerField(
        default=16,
        help_text="Taille de base en px"
    )
    scale_ratio = models.FloatField(
        default=1.25,
        help_text="Ratio d'échelle typographique (1.125, 1.25, 1.5)"
    )
    
    # Line height
    base_line_height = models.FloatField(
        default=1.6,
        help_text="Hauteur de ligne de base"
    )
    
    def generate_font_sizes(self):
        """Génère échelle typographique"""
        sizes = {}
        base = self.base_font_size
        ratio = self.scale_ratio
        
        sizes_config = [
            ('xs', base / (ratio ** 2)),
            ('sm', base / ratio),
            ('base', base),
            ('lg', base * ratio),
            ('xl', base * (ratio ** 2)),
            ('2xl', base * (ratio ** 3)),
            ('3xl', base * (ratio ** 4)),
        ]
        
        for name, size in sizes_config:
            sizes[name] = f"{round(size)}px"
        
        return sizes
    
    def __str__(self):
        return f"Typography {self.brand.name}"
    
    class Meta:
        db_table = 'brands_design_typography_brand'
        verbose_name = "Typographie Marque"
        verbose_name_plural = "Typographies Marques"

class WebsiteTypographyConfig(TimestampedMixin):
    """Configuration typographique spécifique à un website (extension)"""
    
    website = models.OneToOneField(
        'seo_websites_core.Website',
        on_delete=models.CASCADE,
        related_name='typography_config'
    )
    
    # Overrides optionnels
    font_primary_override = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Override font primaire pour ce site"
    )
    base_font_size_override = models.IntegerField(
        null=True, 
        blank=True,
        help_text="Override taille base pour ce site"
    )
    scale_ratio_override = models.FloatField(
        null=True,
        blank=True,
        help_text="Override ratio échelle pour ce site"
    )
    
    def get_effective_font_primary(self):
        """Font primaire effective (override ou brand)"""
        if self.font_primary_override:
            return self.font_primary_override
        return self.website.brand.typography.font_primary
    
    def get_effective_base_size(self):
        """Taille de base effective (override ou brand)"""
        if self.base_font_size_override:
            return self.base_font_size_override
        return self.website.brand.typography.base_font_size
    
    def get_effective_scale_ratio(self):
        """Ratio d'échelle effectif (override ou brand)"""
        if self.scale_ratio_override:
            return self.scale_ratio_override
        return self.website.brand.typography.scale_ratio
    
    def generate_effective_font_sizes(self):
        """Génère échelle avec overrides appliqués"""
        base = self.get_effective_base_size()
        ratio = self.get_effective_scale_ratio()
        
        sizes_config = [
            ('xs', base / (ratio ** 2)),
            ('sm', base / ratio),
            ('base', base),
            ('lg', base * ratio),
            ('xl', base * (ratio ** 2)),
            ('2xl', base * (ratio ** 3)),
            ('3xl', base * (ratio ** 4)),
        ]
        
        return {name: f"{round(size)}px" for name, size in sizes_config}
    
    def __str__(self):
        return f"Typography {self.website.name}"
    
    class Meta:
        db_table = 'brands_design_typography_website'
        verbose_name = "Configuration Typographie Website"
        verbose_name_plural = "Configurations Typographie Websites"
