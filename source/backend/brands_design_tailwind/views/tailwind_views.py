# backend/brands_design_tailwind/views/tailwind_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import json
import logging

from common.permissions.business_permissions import IsAuthenticated, IsBrandMember
from brands_design_colors.models import BrandColorPalette, WebsiteColorConfig
from brands_design_typography.models import BrandTypography, WebsiteTypographyConfig
from brands_design_spacing.models import BrandSpacingSystem, WebsiteLayoutConfig

from ..models import WebsiteTailwindConfig, TailwindThemeExport
from ..serializers import (
    WebsiteTailwindConfigSerializer,
    TailwindThemeExportSerializer
)

logger = logging.getLogger(__name__)

class WebsiteTailwindConfigViewSet(viewsets.ModelViewSet):
    """CRUD config Tailwind websites"""
    
    queryset = WebsiteTailwindConfig.objects.all()
    serializer_class = WebsiteTailwindConfigSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user_brands = self.request.user.brands.all()
        return queryset.filter(website__brand__in=user_brands).select_related(
            'website', 'website__brand'
        )
    
    @action(detail=True, methods=['post'], url_path='regenerate-config')
    def regenerate_config(self, request, pk=None):
        """POST /design/tailwind/website-configs/{id}/regenerate-config/"""
        config = self.get_object()
        
        try:
            # ✅ Créer les dépendances manquantes
            self._ensure_website_configs(config.website)
            
            # ✅ Générer config avec fallbacks sécurisés
            new_config = self._generate_safe_tailwind_config(config)
            css_vars = self._generate_safe_css_variables(config)
            
            # ✅ Sauvegarder
            config.tailwind_config = new_config
            config.css_variables = css_vars
            config.save()
            
            return Response({
                'message': 'Configuration régénérée avec succès',
                'tailwind_config': new_config,
                'css_variables': css_vars,
                'website_name': config.website.name
            })
            
        except Exception as e:
            logger.error(f"Erreur régénération config: {e}")
            return Response({
                'error': f'Erreur lors de la régénération: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], url_path='export-config')
    def export_config(self, request, pk=None):
        """GET /design/tailwind/website-configs/{id}/export-config/"""
        config = self.get_object()
        export_format = request.query_params.get('format', 'json')
        
        try:
            # ✅ Vérifier que la config existe, sinon générer
            if not config.tailwind_config:
                self._ensure_website_configs(config.website)
                config.tailwind_config = self._generate_safe_tailwind_config(config)
                config.css_variables = self._generate_safe_css_variables(config)
                config.save()
            
            # ✅ Export selon format
            if export_format == 'js':
                content = f"module.exports = {json.dumps(config.tailwind_config, indent=2)}"
                content_type = 'application/javascript'
            elif export_format == 'css':
                content = config.css_variables or ':root { /* No variables */ }'
                content_type = 'text/css'
            else:
                content = json.dumps(config.tailwind_config, indent=2)
                content_type = 'application/json'
            
            return Response({
                'content': content,
                'content_type': content_type,
                'filename': f"tailwind-{config.website.name}.{export_format}"
            })
            
        except Exception as e:
            logger.error(f"Erreur export config: {e}")
            return Response({
                'error': f'Erreur lors de l\'export: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _ensure_website_configs(self, website):
        """Crée les configs manquantes pour un website"""
        # ✅ Créer brand palette si manquante
        if not hasattr(website.brand, 'color_palette'):
            BrandColorPalette.objects.create(
                brand=website.brand,
                primary_color='#3B82F6',
                secondary_color='#8B5CF6',
                accent_color='#10B981'
            )
        
        # ✅ Créer brand typography si manquante
        if not hasattr(website.brand, 'typography'):
            BrandTypography.objects.create(
                brand=website.brand,
                font_primary='Inter',
                base_font_size=16,
                scale_ratio=1.25
            )
        
        # ✅ Créer brand spacing si manquant
        if not hasattr(website.brand, 'spacing_system'):
            BrandSpacingSystem.objects.create(
                brand=website.brand,
                base_unit=8,
                max_width='1200px',
                grid_columns=12
            )
        
        # ✅ Créer website configs si manquantes
        if not hasattr(website, 'color_config'):
            WebsiteColorConfig.objects.create(website=website)
        
        if not hasattr(website, 'typography_config'):
            WebsiteTypographyConfig.objects.create(website=website)
        
        if not hasattr(website, 'layout_config'):
            WebsiteLayoutConfig.objects.create(website=website)
    
    def _generate_safe_tailwind_config(self, config):
        """Génère config Tailwind avec fallbacks sécurisés"""
        try:
            website = config.website
            
            # ✅ Récupération sécurisée des configs
            color_config = getattr(website, 'color_config', None)
            typo_config = getattr(website, 'typography_config', None)
            layout_config = getattr(website, 'layout_config', None)
            
            # ✅ Build theme.extend avec fallbacks
            theme_extend = {
                'colors': {
                    'primary': {
                        'DEFAULT': color_config.get_effective_primary() if color_config else '#3B82F6',
                        '500': color_config.get_effective_primary() if color_config else '#3B82F6',
                    },
                    'secondary': {
                        'DEFAULT': color_config.get_effective_secondary() if color_config else '#8B5CF6',
                        '500': color_config.get_effective_secondary() if color_config else '#8B5CF6',
                    },
                    'accent': {
                        'DEFAULT': color_config.get_effective_accent() if color_config else '#10B981',
                        '500': color_config.get_effective_accent() if color_config else '#10B981',
                    }
                },
                'fontFamily': {
                    'sans': [
                        typo_config.get_effective_font_primary() if typo_config else 'Inter',
                        'sans-serif'
                    ],
                },
                'fontSize': {
                    'base': f"{typo_config.get_effective_base_size() if typo_config else 16}px",
                    'lg': '1.125rem',
                    'xl': '1.25rem',
                },
                'spacing': {
                    '4': '1rem',
                    '8': '2rem',
                    '16': '4rem',
                },
                'maxWidth': {
                    'container': layout_config.get_effective_max_width() if layout_config else '1200px',
                }
            }
            
            return {
                'theme': {
                    'extend': theme_extend
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur génération config sécurisée: {e}")
            # ✅ Config par défaut en cas d'erreur
            return {
                'theme': {
                    'extend': {
                        'colors': {
                            'primary': {'DEFAULT': '#3B82F6'},
                            'secondary': {'DEFAULT': '#8B5CF6'},
                            'accent': {'DEFAULT': '#10B981'}
                        }
                    }
                }
            }
    
    def _generate_safe_css_variables(self, config):
        """Génère CSS variables avec fallbacks sécurisés"""
        try:
            website = config.website
            color_config = getattr(website, 'color_config', None)
            
            variables = [":root {"]
            
            if color_config:
                css_vars = color_config.to_css_variables()
                for var, value in css_vars.items():
                    variables.append(f"  {var}: {value};")
            else:
                # ✅ Variables par défaut
                variables.extend([
                    "  --color-primary: #3B82F6;",
                    "  --color-secondary: #8B5CF6;",
                    "  --color-accent: #10B981;"
                ])
            
            variables.append("}")
            
            return "\n".join(variables)
            
        except Exception as e:
            logger.error(f"Erreur génération CSS sécurisée: {e}")
            return ":root {\n  --color-primary: #3B82F6;\n}"

class TailwindThemeExportViewSet(viewsets.ReadOnlyModelViewSet):
    """Lecture exports Tailwind"""
    
    queryset = TailwindThemeExport.objects.all()
    serializer_class = TailwindThemeExportSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user_brands = self.request.user.brands.all()
        return queryset.filter(website__brand__in=user_brands).select_related(
            'website'
        )