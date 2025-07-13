# backend/test_design_system_endpoints_complete.py

import pytest
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse, resolve
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from company_core.models import Company
from brands_core.models import Brand
from seo_websites_core.models import Website
from brands_design_colors.models import BrandColorPalette, WebsiteColorConfig
from brands_design_typography.models import BrandTypography, WebsiteTypographyConfig
from brands_design_spacing.models import BrandSpacingSystem, WebsiteLayoutConfig
from brands_design_tailwind.models import WebsiteTailwindConfig, TailwindThemeExport

User = get_user_model()


class TestDesignSystemEndpointsComplete(APITestCase):
    """Tests complets des endpoints design system avec brand middleware"""
    
    def setUp(self):
        """Setup données de test avec brand middleware"""
        # Créer user + company + brand + website
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.company = Company.objects.create(
            name='Test Company',
            admin=self.user
        )
        
        self.brand = Brand.objects.create(
            name='Test Brand',
            company=self.company,
            brand_admin=self.user
        )
        
        self.website = Website.objects.create(
            name='Test Website',
            url='https://test.com',
            brand=self.brand
        )
        
        # Setup user avec accès brand
        self.user.brands.add(self.brand)
        self.user.company = self.company
        self.user.save()
        
        # Setup client API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Mock du brand middleware - CRUCIAL
        self.middleware_patcher = patch(
            'common.middleware.brand_middleware.BrandContextMiddleware.process_view'
        )
        mock_middleware = self.middleware_patcher.start()
        
        # Le middleware doit setter request.current_brand
        def mock_process_view(request, view_func, view_args, view_kwargs):
            request.current_brand = self.brand
            return None
        
        mock_middleware.side_effect = mock_process_view
    
    def tearDown(self):
        """Cleanup des patches"""
        self.middleware_patcher.stop()
    
    # =========== TESTS EXISTENCE ENDPOINTS ===========
    
    def test_all_design_endpoints_exist(self):
        """Vérifie que tous les endpoints design existent"""
        endpoints = [
            # Colors
            '/design/colors/brand-palettes/',
            '/design/colors/website-configs/',
            
            # Typography
            '/design/typography/brand-typography/',
            '/design/typography/website-configs/',
            
            # Spacing
            '/design/spacing/brand-spacing/',
            '/design/spacing/website-configs/',
            
            # Tailwind
            '/design/tailwind/website-configs/',
            '/design/tailwind/exports/',
        ]
        
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertNotEqual(response.status_code, 404, 
                                  f"Endpoint {endpoint} not found")
                self.assertIn(response.status_code, [200, 403], 
                            f"Endpoint {endpoint} should exist (got {response.status_code})")
    
    # =========== TESTS CRUD COLORS ===========
    
    def test_crud_brand_color_palette(self):
        """Test CRUD complet palette couleurs brand"""
        # CREATE
        create_data = {
            'brand': self.brand.id,
            'primary_color': '#FF6B35',
            'secondary_color': '#F7931E',
            'accent_color': '#FFD23F',
            'neutral_dark': '#1A1A1A',
            'neutral_light': '#F8F9FA'
        }
        
        response = self.client.post('/design/colors/brand-palettes/', create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        palette_id = response.json()['id']
        self.assertEqual(BrandColorPalette.objects.count(), 1)
        
        # READ
        response = self.client.get(f'/design/colors/brand-palettes/{palette_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['primary_color'], '#FF6B35')
        self.assertEqual(data['brand_name'], 'Test Brand')
        
        # UPDATE
        update_data = {'primary_color': '#123456'}
        response = self.client.patch(f'/design/colors/brand-palettes/{palette_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier update
        palette = BrandColorPalette.objects.get(id=palette_id)
        self.assertEqual(palette.primary_color, '#123456')
        
        # LIST avec filtre
        response = self.client.get('/design/colors/brand-palettes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        
        # DELETE
        response = self.client.delete(f'/design/colors/brand-palettes/{palette_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BrandColorPalette.objects.count(), 0)
    
    def test_crud_website_color_config(self):
        """Test CRUD config couleurs website"""
        # Créer palette brand d'abord
        palette = BrandColorPalette.objects.create(
            brand=self.brand,
            primary_color='#FF6B35',
            secondary_color='#F7931E',
            accent_color='#FFD23F'
        )
        
        # CREATE website config
        create_data = {
            'website': self.website.id,
            'primary_override': '#123456',
            'secondary_override': '#789ABC'
        }
        
        response = self.client.post('/design/colors/website-configs/', create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        config_id = response.json()['id']
        
        # READ avec fallback
        response = self.client.get(f'/design/colors/website-configs/{config_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Vérifier effective colors (override + fallback)
        self.assertEqual(data['effective_primary'], '#123456')  # Override
        self.assertEqual(data['effective_accent'], '#FFD23F')    # Fallback sur brand
    
    # =========== TESTS ACTIONS CUSTOM ===========
    
    def test_css_variables_action(self):
        """Test action CSS variables"""
        palette = BrandColorPalette.objects.create(
            brand=self.brand,
            primary_color='#FF6B35',
            secondary_color='#F7931E',
            accent_color='#FFD23F'
        )
        
        # ✅ CORRECT avec hyphen
        response = self.client.get(f'/design/colors/brand-palettes/{palette.id}/css-variables/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('css_variables', data)
        self.assertIn('css_content', data)
        
        # Vérifier format CSS variables
        css_vars = data['css_variables']
        self.assertEqual(css_vars['--color-primary'], '#FF6B35')
        self.assertEqual(css_vars['--color-secondary'], '#F7931E')
        
        # Vérifier CSS content formaté
        css_content = data['css_content']
        self.assertIn('--color-primary: #FF6B35;', css_content)
    
    def test_website_css_variables_with_overrides(self):
        """Test CSS variables website avec overrides"""
        # Setup palette + config
        palette = BrandColorPalette.objects.create(
            brand=self.brand,
            primary_color='#FF6B35',
            secondary_color='#F7931E',
            accent_color='#FFD23F'
        )
        
        config = WebsiteColorConfig.objects.create(
            website=self.website,
            primary_override='#123456'
        )
        
        # ✅ CORRECT avec hyphen
        response = self.client.get(f'/design/colors/website-configs/{config.id}/css-variables/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        css_vars = data['css_variables']
        
        # Override appliqué
        self.assertEqual(css_vars['--color-primary'], '#123456')
        # Fallback sur brand
        self.assertEqual(css_vars['--color-secondary'], '#F7931E')
    
    def test_reset_overrides_action(self):
        """Test action reset overrides"""
        palette = BrandColorPalette.objects.create(
            brand=self.brand,
            primary_color='#FF6B35',
            secondary_color='#F7931E',
            accent_color='#FFD23F'
        )
        
        config = WebsiteColorConfig.objects.create(
            website=self.website,
            primary_override='#123456',
            secondary_override='#789ABC'
        )
        
        # ✅ CORRECT avec hyphen
        response = self.client.post(f'/design/colors/website-configs/{config.id}/reset-overrides/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier reset
        config.refresh_from_db()
        self.assertEqual(config.primary_override, '')
        self.assertEqual(config.secondary_override, '')
    
    # =========== TESTS TYPOGRAPHY ===========
    
    def test_typography_font_sizes_generation(self):
        """Test génération échelle typographique"""
        typography = BrandTypography.objects.create(
            brand=self.brand,
            font_primary='Inter',
            font_secondary='Roboto Slab',
            base_font_size=16,
            scale_ratio=1.25
        )
        
        # ✅ CORRECT avec hyphen
        response = self.client.get(f'/design/typography/brand-typography/{typography.id}/font-sizes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('font_sizes', data)
        self.assertIn('tailwind_config', data)
        
        # Vérifier échelle générée
        font_sizes = data['font_sizes']
        self.assertIn('base', font_sizes)
        self.assertIn('lg', font_sizes)
        self.assertIn('xl', font_sizes)
        
        # Vérifier config Tailwind
        tailwind_config = data['tailwind_config']
        self.assertIn('fontSize', tailwind_config)
        self.assertEqual(tailwind_config['fontSize'], font_sizes)
    
    def test_website_typography_effective_values(self):
        """Test valeurs effectives typography website"""
        # Brand typography
        brand_typo = BrandTypography.objects.create(
            brand=self.brand,
            font_primary='Inter',
            base_font_size=16,
            scale_ratio=1.25
        )
        
        # Website override
        website_typo = WebsiteTypographyConfig.objects.create(
            website=self.website,
            font_primary_override='Roboto',
            base_font_size_override=18
        )
        
        response = self.client.get(f'/design/typography/website-configs/{website_typo.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        
        # Vérifier effective values
        self.assertEqual(data['effective_font_primary'], 'Roboto')    # Override
        self.assertEqual(data['effective_base_size'], 18)             # Override
        self.assertEqual(data['effective_scale_ratio'], 1.25)         # Fallback brand
    
    # =========== TESTS SPACING ===========
    
    def test_spacing_scale_generation(self):
        """Test génération échelle spacing"""
        spacing = BrandSpacingSystem.objects.create(
            brand=self.brand,
            base_unit=8,
            spacing_scale=1.0,
            max_width='1200px',
            grid_columns=12
        )
        
        # ✅ CORRECT avec hyphen
        response = self.client.get(f'/design/spacing/brand-spacing/{spacing.id}/tailwind-spacing/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('spacing_scale', data)
        self.assertIn('tailwind_config', data)
        
        # Vérifier échelle spacing
        spacing_scale = data['spacing_scale']
        self.assertIn('4', spacing_scale)   # Base unit
        self.assertIn('8', spacing_scale)   # 2x base
        self.assertIn('16', spacing_scale)  # 4x base
        
        # Vérifier config Tailwind
        tailwind_config = data['tailwind_config']
        self.assertIn('spacing', tailwind_config)
        self.assertIn('maxWidth', tailwind_config)
        self.assertEqual(tailwind_config['maxWidth']['container'], '1200px')
    
    # =========== TESTS TAILWIND CONFIG ===========
    
    def test_tailwind_config_generation(self):
        """Test génération complète config Tailwind"""
        # Setup toutes les dépendances
        palette = BrandColorPalette.objects.create(
            brand=self.brand,
            primary_color='#FF6B35',
            secondary_color='#F7931E',
            accent_color='#FFD23F'
        )
        
        typography = BrandTypography.objects.create(
            brand=self.brand,
            font_primary='Inter',
            base_font_size=16,
            scale_ratio=1.25
        )
        
        spacing = BrandSpacingSystem.objects.create(
            brand=self.brand,
            base_unit=8,
            max_width='1200px',
            grid_columns=12
        )
        
        # Configs website
        color_config = WebsiteColorConfig.objects.create(
            website=self.website,
            primary_override='#123456'
        )
        
        typo_config = WebsiteTypographyConfig.objects.create(
            website=self.website
        )
        
        layout_config = WebsiteLayoutConfig.objects.create(
            website=self.website
        )
        
        # Config Tailwind
        tailwind_config = WebsiteTailwindConfig.objects.create(
            website=self.website
        )
        
        # ✅ CORRECT avec hyphen
        response = self.client.post(f'/design/tailwind/website-configs/{tailwind_config.id}/regenerate-config/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('message', data)
        self.assertIn('tailwind_config', data)
        self.assertIn('css_variables', data)
        
        # Vérifier structure config Tailwind
        config = data['tailwind_config']
        self.assertIn('theme', config)
        self.assertIn('extend', config['theme'])
        
        extend = config['theme']['extend']
        self.assertIn('colors', extend)
        self.assertIn('fontFamily', extend)
        
        # Vérifier override couleur appliqué
        self.assertEqual(extend['colors']['primary']['DEFAULT'], '#123456')
    
    def test_tailwind_export_formats(self):
        """Test exports Tailwind différents formats"""
        
        print(f"🔍 Setup: Website {self.website.id}, Brand {self.brand.id}")
        
        # Créer config Tailwind avec données minimales requises
        tailwind_config = WebsiteTailwindConfig.objects.create(
            website=self.website,
            tailwind_config={'theme': {'extend': {'colors': {'primary': '#FF6B35'}}}},
            css_variables=':root { --color-primary: #FF6B35; }'
        )
        
        print(f"🔍 Created tailwind_config ID: {tailwind_config.id}")
        
        # ✅ DEBUG: Vérifier l'objet existe et est accessible
        response = self.client.get(f'/design/tailwind/website-configs/{tailwind_config.id}/')
        print(f"🔍 GET object status: {response.status_code}")
        if response.status_code != 200:
            print(f"❌ GET object failed: {response.content}")
            # Essayer de comprendre pourquoi
            all_configs = WebsiteTailwindConfig.objects.all()
            print(f"🔍 All configs: {[(c.id, c.website.id) for c in all_configs]}")
            self.fail(f"Object not accessible: {response.content}")
        
        # ✅ Si l'objet est OK, tester export
        url = f'/design/tailwind/website-configs/{tailwind_config.id}/export-config/'
        print(f"🔍 Testing URL: {url}")
        
        response = self.client.get(url)
        print(f"🔍 Export status: {response.status_code}")
        print(f"🔍 Export content: {response.content}")
        
        # ✅ Debug plus poussé si ça échoue
        if response.status_code == 404:
            # Tester URL alternatives
            alt_url = f'/design/tailwind/website-configs/{tailwind_config.id}/export_config/'
            alt_response = self.client.get(alt_url)
            print(f"🔍 Alt URL (underscore) status: {alt_response.status_code}")
            
            # Vérifier les permissions
            print(f"🔍 User brands: {list(self.user.brands.all())}")
            print(f"🔍 Config website brand: {tailwind_config.website.brand}")
            
            self.fail(f"Export failed with 404. URL: {url}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    
    
    # =========== TESTS PERMISSIONS ===========
    
    def test_brand_scoped_permissions(self):
        """Test permissions scopées par brand"""
        # ✅ CORRECT - Créer admin pour other_company
        other_admin = User.objects.create_user(
            username='otheradmin',
            email='otheradmin@example.com',
            password='testpass123'
        )
        
        other_company = Company.objects.create(
            name='Other Company',
            admin=other_admin  # ✅ ADMIN REQUIS
        )
        
        other_brand = Brand.objects.create(
            name='Other Brand',
            company=other_company,
            brand_admin=other_admin  # ✅ COHÉRENT
        )
        
        other_palette = BrandColorPalette.objects.create(
            brand=other_brand,
            primary_color='#000000',
            secondary_color='#111111',
            accent_color='#222222'
        )
        
        # Lister palettes - ne doit pas voir l'autre brand
        response = self.client.get('/design/colors/brand-palettes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        palette_ids = [item['id'] for item in data['results']]
        self.assertNotIn(other_palette.id, palette_ids)
        
        # Essayer d'accéder directement à l'autre palette
        response = self.client.get(f'/design/colors/brand-palettes/{other_palette.id}/')
        self.assertIn(response.status_code, [403, 404])  # Forbidden ou Not Found
    
    def test_website_permissions_via_brand(self):
        """Test permissions website via brand ownership"""
        # ✅ CORRECT - Créer admin pour other_company
        other_admin = User.objects.create_user(
            username='otheradmin2',  # Username unique
            email='otheradmin2@example.com',
            password='testpass123'
        )
        
        other_company = Company.objects.create(
            name='Other Company',
            admin=other_admin  # ✅ ADMIN REQUIS
        )
        
        other_brand = Brand.objects.create(
            name='Other Brand',
            company=other_company,
            brand_admin=other_admin
        )
        other_website = Website.objects.create(
            name='Other Website',
            url='https://other.com',
            brand=other_brand
        )
        
        other_config = WebsiteColorConfig.objects.create(
            website=other_website,
            primary_override='#000000'
        )
        
        # Lister configs website - ne doit pas voir l'autre
        response = self.client.get('/design/colors/website-configs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        config_ids = [item['id'] for item in data['results']]
        self.assertNotIn(other_config.id, config_ids)
    
    # =========== TESTS SERIALIZERS ===========
    
    def test_serializer_computed_fields(self):
        """Test champs calculés des serializers"""
        # Setup données
        palette = BrandColorPalette.objects.create(
            brand=self.brand,
            primary_color='#FF6B35',
            secondary_color='#F7931E',
            accent_color='#FFD23F'
        )
        
        config = WebsiteColorConfig.objects.create(
            website=self.website,
            primary_override='#123456'
        )
        
        # Test serializer website config détaillé
        response = self.client.get(f'/design/colors/website-configs/{config.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        
        # Vérifier champs computed
        self.assertIn('effective_primary', data)
        self.assertIn('effective_secondary', data)
        self.assertIn('effective_accent', data)
        self.assertIn('website_name', data)
        self.assertIn('brand_name', data)
        
        # Vérifier valeurs
        self.assertEqual(data['effective_primary'], '#123456')    # Override
        self.assertEqual(data['effective_secondary'], '#F7931E')  # Fallback
        self.assertEqual(data['website_name'], 'Test Website')
        self.assertEqual(data['brand_name'], 'Test Brand')
    
    # =========== TESTS INTÉGRATION ===========
    
    def test_full_design_system_workflow(self):
        """Test workflow complet du design system"""
        
        # ============= ÉTAPE 1 : CRÉER BRAND DESIGN SYSTEM =============
        
        # 1.1 Créer palette couleurs brand
        palette_data = {
            'brand': self.brand.id,
            'primary_color': '#FF6B35',
            'secondary_color': '#F7931E',
            'accent_color': '#FFD23F',
            'neutral_dark': '#1A1A1A',
            'neutral_light': '#F8F9FA',
            'success_color': '#10B981',
            'warning_color': '#F59E0B',
            'error_color': '#EF4444'
        }
        response = self.client.post('/design/colors/brand-palettes/', palette_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        palette_id = response.json()['id']
        
        # 1.2 Créer typography brand
        typo_data = {
            'brand': self.brand.id,
            'font_primary': 'Inter',
            'font_secondary': 'Roboto Slab',
            'base_font_size': 16,
            'scale_ratio': 1.25,
            'line_height_base': 1.6,
            'letter_spacing_base': 0
        }
        response = self.client.post('/design/typography/brand-typography/', typo_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        typography_id = response.json()['id']
        
        # 1.3 Créer spacing system brand
        spacing_data = {
            'brand': self.brand.id,
            'base_unit': 8,
            'spacing_scale': 1.0,
            'max_width': '1200px',
            'grid_columns': 12,
            'breakpoints': {
                'sm': '640px',
                'md': '768px',
                'lg': '1024px',
                'xl': '1280px'
            }
        }
        response = self.client.post('/design/spacing/brand-spacing/', spacing_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        spacing_id = response.json()['id']
        
        # ============= ÉTAPE 2 : CRÉER WEBSITE CONFIGS =============
        
        # 2.1 Config couleurs website avec overrides
        website_color_data = {
            'website': self.website.id,
            'primary_override': '#123456',
            'secondary_override': '#789ABC',
            'custom_colors': {
                'brand_special': '#FF00FF',
                'website_unique': '#00FFFF'
            }
        }
        response = self.client.post('/design/colors/website-configs/', website_color_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        website_color_id = response.json()['id']
        
        # 2.2 Config typography website
        website_typo_data = {
            'website': self.website.id,
            'font_primary_override': 'Roboto',
            'base_font_size_override': 18,
            'custom_font_sizes': {
                'hero': '3.5rem',
                'subhero': '1.75rem'
            }
        }
        response = self.client.post('/design/typography/website-configs/', website_typo_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        website_typo_id = response.json()['id']
        
        # 2.3 Config layout website
        website_layout_data = {
            'website': self.website.id,
            'max_width_override': '1400px',
            'grid_columns_override': 16,
            'custom_breakpoints': {
                'xs': '480px',
                'xxl': '1600px'
            }
        }
        response = self.client.post('/design/spacing/website-configs/', website_layout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        website_layout_id = response.json()['id']
        
        # ============= ÉTAPE 3 : GÉNÉRER CONFIG TAILWIND =============
        
        # 3.1 Créer config Tailwind principale
        tailwind_data = {
            'website': self.website.id,
            'tailwind_config': {  # ✅ CORRECT : tailwind_config au lieu de custom_config
                'theme': {
                    'extend': {
                        'animation': {
                            'custom-bounce': 'bounce 1s infinite'
                        }
                    }
                }
            }
        }
        response = self.client.post('/design/tailwind/website-configs/', tailwind_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        tailwind_id = response.json()['id']
        
        # 3.2 Régénérer config complète - ✅ CORRECT avec hyphen
        response = self.client.post(f'/design/tailwind/website-configs/{tailwind_id}/regenerate-config/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # ============= ÉTAPE 4 : TESTER EXPORTS =============
        
        # 4.1 Export JSON (default) - ✅ CORRECT avec hyphen
        response = self.client.get(f'/design/tailwind/website-configs/{tailwind_id}/export-config/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4.2 Export JavaScript - ✅ CORRECT avec hyphen
        response = self.client.get(f'/design/tailwind/website-configs/{tailwind_id}/export-config/?format=js')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        js_export = response.json()
        self.assertIn('module.exports', js_export['content'])
        
        print("✅ Workflow complet du design system testé avec succès !")


    def test_debug_tailwind_issues(self):
        """Debug précis des actions Tailwind"""
        
        # Créer config Tailwind avec toutes les dépendances
        tailwind_config = WebsiteTailwindConfig.objects.create(
            website=self.website,
            tailwind_config={'theme': {'extend': {'colors': {'primary': '#FF6B35'}}}},
            css_variables=':root { --color-primary: #FF6B35; }'
        )
        
        print(f"✅ Created tailwind_config ID: {tailwind_config.id}")
        print(f"✅ Website ID: {self.website.id}")
        print(f"✅ Brand ID: {self.brand.id}")
        
        # Test 1: Vérifier que l'objet est accessible
        response = self.client.get(f'/design/tailwind/website-configs/{tailwind_config.id}/')
        print(f"✅ GET object status: {response.status_code}")
        if response.status_code != 200:
            print(f"❌ GET object error: {response.content}")
            return
        
        # Test 2: Tester export-config
        print("\n🔍 Testing export-config...")
        response = self.client.get(f'/design/tailwind/website-configs/{tailwind_config.id}/export-config/')
        print(f"Export status: {response.status_code}")
        if response.status_code != 200:
            print(f"Export error: {response.content}")
            print(f"Export headers: {dict(response.items())}")
        else:
            print(f"✅ Export success: {response.json()}")
        
        # Test 3: Tester regenerate-config
        print("\n🔍 Testing regenerate-config...")
        response = self.client.post(f'/design/tailwind/website-configs/{tailwind_config.id}/regenerate-config/')
        print(f"Regenerate status: {response.status_code}")
        if response.status_code != 200:
            print(f"Regenerate error: {response.content}")
            print(f"Regenerate headers: {dict(response.items())}")
        else:
            print(f"✅ Regenerate success: {response.json()}")

if __name__ == '__main__':
    import django
    django.setup()
    
    # Run avec coverage
    import pytest
    pytest.main([__file__, '-v', '--tb=short'])