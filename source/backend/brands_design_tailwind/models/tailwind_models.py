# backend/brands_design_tailwind/models/tailwind_models.py

from django.db import models
import logging
import json
import hashlib

from common.models.mixins import TimestampedMixin

logger = logging.getLogger(__name__)

class WebsiteTailwindConfig(TimestampedMixin):
    """Configuration Tailwind générée pour un website"""
    
    website = models.OneToOneField(
        'seo_websites_core.Website',
        on_delete=models.CASCADE,
        related_name='tailwind_config'
    )
    
    # Config Tailwind theme.extend auto-générée
    tailwind_config = models.JSONField(
        default=dict,
        help_text="Configuration theme.extend Tailwind"
    )
    
    # CSS variables générées
    css_variables = models.TextField(
        blank=True,
        help_text="Variables CSS générées"
    )
    
    # Cache et meta
    last_generated_at = models.DateTimeField(null=True, blank=True)
    config_hash = models.CharField(
        max_length=64,
        help_text="Hash pour invalidation cache"
    )
    
    def generate_tailwind_config(self):
        """Génère config Tailwind depuis colors + typography + spacing"""
        try:
            # Récupère les configs
            colors = self.website.color_config
            typography = self.website.typography_config  
            spacing = self.website.layout_config
            
            # Build theme.extend
            theme_extend = {
                'colors': {
                    'primary': {
                        'DEFAULT': colors.get_effective_primary(),
                        '50': self._lighten_color(colors.get_effective_primary(), 0.9),
                        '500': colors.get_effective_primary(),
                        '900': self._darken_color(colors.get_effective_primary(), 0.7),
                    },
                    'secondary': {
                        'DEFAULT': colors.get_effective_secondary(),
                        '500': colors.get_effective_secondary(),
                    },
                    'accent': {
                        'DEFAULT': colors.get_effective_accent(),
                        '500': colors.get_effective_accent(),
                    }
                },
                'fontFamily': {
                    'sans': [typography.get_effective_font_primary(), 'sans-serif'],
                    'heading': [typography.get_effective_font_primary(), 'sans-serif'],
                },
                'fontSize': typography.generate_effective_font_sizes(),
                'spacing': spacing.website.brand.spacing_system.generate_spacing_scale(),
                'maxWidth': {
                    'container': spacing.get_effective_max_width(),
                },
                'gridTemplateColumns': {
                    'site': f"repeat({spacing.get_effective_grid_columns()}, minmax(0, 1fr))",
                }
            }
            
            config = {
                'theme': {
                    'extend': theme_extend
                }
            }
            
            # Update config et hash
            self.tailwind_config = config
            self.config_hash = self._generate_config_hash(config)
            
            return config
            
        except Exception as e:
            logger.error(f"Erreur génération config Tailwind: {e}")
            return {}
    
    def generate_css_variables(self):
        """Génère CSS variables depuis les configs"""
        try:
            colors = self.website.color_config
            typography = self.website.typography_config
            spacing = self.website.layout_config
            
            variables = []
            variables.append(":root {")
            
            # Colors
            color_vars = colors.to_css_variables()
            for var, value in color_vars.items():
                variables.append(f"  {var}: {value};")
            
            # Typography
            variables.append(f"  --font-primary: {typography.get_effective_font_primary()};")
            variables.append(f"  --font-size-base: {typography.get_effective_base_size()}px;")
            
            # Spacing
            variables.append(f"  --container-max-width: {spacing.get_effective_max_width()};")
            variables.append(f"  --grid-columns: {spacing.get_effective_grid_columns()};")
            
            variables.append("}")
            
            css = "\n".join(variables)
            self.css_variables = css
            
            return css
            
        except Exception as e:
            logger.error(f"Erreur génération CSS variables: {e}")
            return ""
    
    def _generate_config_hash(self, config):
        """Génère hash de la config pour cache"""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    def _lighten_color(self, hex_color, factor):
        """Éclaircit une couleur hex"""
        # Implémentation basique - à améliorer
        return hex_color  # Placeholder
    
    def _darken_color(self, hex_color, factor):
        """Assombrit une couleur hex"""
        # Implémentation basique - à améliorer  
        return hex_color  # Placeholder
    
    def save(self, *args, **kwargs):
        """Auto-génère config au save"""
        from django.utils import timezone
        
        # Génère config si pas présente
        if not self.tailwind_config:
            self.generate_tailwind_config()
            
        # Génère CSS si pas présent
        if not self.css_variables:
            self.generate_css_variables()
            
        self.last_generated_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Tailwind {self.website.name}"
    
    class Meta:
        db_table = 'brands_design_tailwind_website'
        verbose_name = "Configuration Tailwind Website"
        verbose_name_plural = "Configurations Tailwind Websites"

class TailwindThemeExport(TimestampedMixin):
    """Export/cache des thèmes Tailwind"""
    
    website = models.ForeignKey(
        'seo_websites_core.Website',
        on_delete=models.CASCADE,
        related_name='tailwind_exports'
    )
    
    export_type = models.CharField(
        max_length=20,
        choices=[
            ('config', 'Config JS'),
            ('css', 'CSS Variables'),
            ('json', 'JSON Export'),
        ]
    )
    
    content = models.TextField(help_text="Contenu exporté")
    file_hash = models.CharField(max_length=64)
    
    def __str__(self):
        return f"Export {self.export_type} - {self.website.name}"
    
    class Meta:
        db_table = 'brands_design_tailwind_export'
        verbose_name = "Export Tailwind"
        verbose_name_plural = "Exports Tailwind"
        unique_together = ['website', 'export_type']
