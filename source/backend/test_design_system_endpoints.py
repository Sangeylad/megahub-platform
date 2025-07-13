# backend/test_design_system_endpoints.py

import pytest
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse, resolve
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from company_core.models import Company
from brands_core.models import Brand
from seo_websites_core.models import Website
from brands_design_colors.models import BrandColorPalette, WebsiteColorConfig
from brands_design_typography.models import BrandTypography, WebsiteTypographyConfig
from brands_design_spacing.models import BrandSpacingSystem, WebsiteLayoutConfig
from brands_design_tailwind.models import WebsiteTailwindConfig

User = get_user_model()


class TestDesignSystemEndpoints(APITestCase):
    """Tests des endpoints pour le design system"""
    
        def setUp(self):
        """Setup données de test"""
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
        
        # Ajouter user aux brands ET company
        self.user.brands.add(self.brand)
        self.user.company = self.company
        self.user.save()
        
        # Setup client API avec mock du middleware brand
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Mock du middleware brand - IMPORTANT!
        def mock_get_response(request):
            request.current_brand = self.brand
            return None
        
        from unittest.mock import patch
        self.brand_middleware_patcher = patch(
            'common.middleware.brand_middleware.BrandContextMiddleware.process_request',
            return_value=None
        )
        self.brand_middleware_patcher.start()
    
    def test_colors_endpoints_exist(self):
        """Vérifie que les endpoints colors existent"""
        endpoints = [
            '/design/colors/brand-palettes/',
            '/design/colors/website-configs/',
        ]
        
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertNotEqual(response.status_code, 404, 
                                  f"Endpoint {endpoint} not found")
    
    def test_typography_endpoints_exist(self):
        """Vérifie que les endpoints typography existent"""
        endpoints = [
            '/design/typography/brand-typography/',
            '/design/typography/website-configs/',
        ]
        
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertNotEqual(response.status_code, 404,
                                  f"Endpoint {endpoint} not found")
    
    def test_spacing_endpoints_exist(self):
        """Vérifie que les endpoints spacing existent"""
        endpoints = [
            '/design/spacing/brand-spacing/',
            '/design/spacing/website-configs/',
        ]
        
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertNotEqual(response.status_code, 404,
                                  f"Endpoint {endpoint} not found")
    
    def test_tailwind_endpoints_exist(self):
        """Vérifie que les endpoints tailwind existent"""
        endpoints = [
            '/design/tailwind/website-configs/',
            '/design/tailwind/exports/',
        ]
        
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertNotEqual(response.status_code, 404,
                                  f"Endpoint {endpoint} not found")
    
    def test_create_brand_color_palette(self):
        """Test création palette couleurs brand"""
        data = {
            'brand': self.brand.id,
            'primary_color': '#FF6B35',
            'secondary_color': '#F7931E',
            'accent_color': '#FFD23F'
        }
        
        response = self.client.post('/design/colors/brand-palettes/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BrandColorPalette.objects.count(), 1)
        
        palette = BrandColorPalette.objects.first()
        self.assertEqual(palette.primary_color, '#FF6B35')
        self.assertEqual(palette.brand, self.brand)
    
    def test_create_website_color_config(self):
        """Test création config couleurs website"""
        # Créer palette brand d'abord
        palette = BrandColorPalette.objects.create(
            brand=self.brand,
            primary_color='#FF6B35',
            secondary_color='#F7931E',
            accent_color='#FFD23F'
        )
        
        data = {
            'website': self.website.id,
            'primary_override': '#123456',
        }
        
        response = self.client.post('/design/colors/website-configs/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WebsiteColorConfig.objects.count(), 1)
        
        config = WebsiteColorConfig.objects.first()
        self.assertEqual(config.primary_override, '#123456')
        self.assertEqual(config.website, self.website)
    
    def test_css_variables_action(self):
        """Test action CSS variables"""
        # Créer palette
        palette = BrandColorPalette.objects.create(
            brand=self.brand,
            primary_color='#FF6B35',
            secondary_color='#F7931E',
            accent_color='#FFD23F'
        )
        
        response = self.client.get(f'/design/colors/brand-palettes/{palette.id}/css_variables/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('css_variables', data)
        self.assertIn('--color-primary', data['css_variables'])
        self.assertEqual(data['css_variables']['--color-primary'], '#FF6B35')
    
    def test_typography_font_sizes_action(self):
        """Test action font sizes typography"""
        # Mock current_brand pour ce test
        self.client.defaults['HTTP_X_CURRENT_BRAND_ID'] = str(self.brand.id)
        typography = BrandTypography.objects.create(
            brand=self.brand,
            font_primary='Inter',
            base_font_size=16,
            scale_ratio=1.25
        )
        
        response = self.client.get(f'/design/typography/brand-typography/{typography.id}/font_sizes/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('font_sizes', data)
        self.assertIn('tailwind_config', data)
        self.assertIn('base', data['font_sizes'])
    
    def test_spacing_tailwind_spacing_action(self):
        """Test action tailwind spacing"""
        # Mock current_brand pour ce test
        self.client.defaults['HTTP_X_CURRENT_BRAND_ID'] = str(self.brand.id)
        spacing = BrandSpacingSystem.objects.create(
            brand=self.brand,
            base_unit=8,
            spacing_scale=1.0
        )
        
        response = self.client.get(f'/design/spacing/brand-spacing/{spacing.id}/tailwind_spacing/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('spacing_scale', data)
        self.assertIn('tailwind_config', data)
        self.assertIn('4', data['spacing_scale'])  # Base unit
    
    def test_tailwind_regenerate_config(self):
        """Test régénération config Tailwind"""
        # Mock current_brand pour ce test
        self.client.defaults['HTTP_X_CURRENT_BRAND_ID'] = str(self.brand.id)
        # Créer toutes les dépendances
        palette = BrandColorPalette.objects.create(
            brand=self.brand,
            primary_color='#FF6B35',
            secondary_color='#F7931E',
            accent_color='#FFD23F'
        )
        
        typography = BrandTypography.objects.create(
            brand=self.brand,
            font_primary='Inter'
        )
        
        spacing = BrandSpacingSystem.objects.create(
            brand=self.brand,
            base_unit=8
        )
        
        color_config = WebsiteColorConfig.objects.create(website=self.website)
        typo_config = WebsiteTypographyConfig.objects.create(website=self.website)
        layout_config = WebsiteLayoutConfig.objects.create(website=self.website)
        
        tailwind_config = WebsiteTailwindConfig.objects.create(website=self.website)
        
        response = self.client.post(f'/design/tailwind/website-configs/{tailwind_config.id}/regenerate_config/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('message', data)
        self.assertIn('tailwind_config', data)
    
    def test_export_config_action(self):
        """Test export config Tailwind"""
        tailwind_config = WebsiteTailwindConfig.objects.create(
            website=self.website,
            tailwind_config={'theme': {'extend': {'colors': {'primary': '#FF6B35'}}}}
        )
        
        # Test export JSON
        response = self.client.get(f'/design/tailwind/website-configs/{tailwind_config.id}/export_config/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test export JS
        response = self.client.get(f'/design/tailwind/website-configs/{tailwind_config.id}/export_config/?format=js')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('module.exports', data['content'])
    
    def test_permissions_brand_scoped(self):
        """Test que les permissions sont bien scopées par brand"""
        # Mock current_brand pour ce test
        self.client.defaults['HTTP_X_CURRENT_BRAND_ID'] = str(self.brand.id)
        # Créer autre user + brand
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        other_company = Company.objects.create(
            name='Other Company',
            admin=other_user
        )
        
        other_brand = Brand.objects.create(
            name='Other Brand',
            company=other_company,
            brand_admin=other_user
        )
        
        # Créer palette pour autre brand
        other_palette = BrandColorPalette.objects.create(
            brand=other_brand,
            primary_color='#000000',
            secondary_color='#111111',
            accent_color='#222222'
        )
        
        # Tester que user actuel ne voit pas la palette de l'autre brand
        response = self.client.get('/design/colors/brand-palettes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        palette_ids = [item['id'] for item in data['results']]
        self.assertNotIn(other_palette.id, palette_ids)
    
    def test_url_patterns_resolution(self):
        """Test que les patterns d'URLs se résolvent correctement"""
        url_patterns = {
            '/design/colors/brand-palettes/': 'brands_design_colors:brandcolorpalette-list',
            '/design/typography/brand-typography/': 'brands_design_typography:brandtypography-list',
            '/design/spacing/brand-spacing/': 'brands_design_spacing:brandspacingsystem-list',
            '/design/tailwind/website-configs/': 'brands_design_tailwind:websitetailwindconfig-list',
        }
        
        for url, expected_name in url_patterns.items():
            with self.subTest(url=url):
                resolved = resolve(url)
                # Vérifier que l'URL se résout sans erreur
                self.assertIsNotNone(resolved)

    def tearDown(self):
        """Cleanup après tests"""
        if hasattr(self, 'brand_middleware_patcher'):
            self.brand_middleware_patcher.stop()


if __name__ == '__main__':
    import django
    django.setup()
    pytest.main([__file__, '-v'])
