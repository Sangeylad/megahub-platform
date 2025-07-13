# backend/test_design_system_structure.py

import pytest
import os
from django.apps import apps
from django.db import models
from django.test import TestCase


class TestDesignSystemStructure(TestCase):
    """Tests de structure pour les 4 apps design system"""
    
    def test_apps_installed(self):
        """Vérifie que toutes les apps design sont installées"""
        required_apps = [
            'brands_design_colors',
            'brands_design_typography', 
            'brands_design_spacing',
            'brands_design_tailwind'
        ]
        
        installed_apps = [app.name for app in apps.get_app_configs()]
        
        for app_name in required_apps:
            with self.subTest(app=app_name):
                self.assertIn(app_name, installed_apps, f"App {app_name} not installed")
    
    def test_models_exist(self):
        """Vérifie que tous les modèles requis existent"""
        expected_models = {
            'brands_design_colors': ['BrandColorPalette', 'WebsiteColorConfig'],
            'brands_design_typography': ['BrandTypography', 'WebsiteTypographyConfig'],
            'brands_design_spacing': ['BrandSpacingSystem', 'WebsiteLayoutConfig'],
            'brands_design_tailwind': ['WebsiteTailwindConfig', 'TailwindThemeExport']
        }
        
        for app_name, model_names in expected_models.items():
            app = apps.get_app_config(app_name)
            app_models = {model._meta.object_name for model in app.get_models()}
            
            for model_name in model_names:
                with self.subTest(app=app_name, model=model_name):
                    self.assertIn(model_name, app_models, 
                                f"Model {model_name} not found in {app_name}")
    
    def test_relations_brand(self):
        """Vérifie les relations OneToOne avec Brand"""
        brand_related_models = [
            ('brands_design_colors', 'BrandColorPalette'),
            ('brands_design_typography', 'BrandTypography'),
            ('brands_design_spacing', 'BrandSpacingSystem')
        ]
        
        for app_name, model_name in brand_related_models:
            model = apps.get_model(app_name, model_name)
            
            # Cherche le champ brand
            brand_field = None
            for field in model._meta.fields:
                if field.name == 'brand':
                    brand_field = field
                    break
            
            with self.subTest(app=app_name, model=model_name):
                self.assertIsNotNone(brand_field, f"Field 'brand' not found in {model_name}")
                self.assertIsInstance(brand_field, models.OneToOneField, 
                                    f"Field 'brand' should be OneToOneField in {model_name}")
                self.assertEqual(brand_field.related_model._meta.label, 'brands_core.Brand',
                               f"Brand field should point to brands_core.Brand in {model_name}")
    
    def test_relations_website(self):
        """Vérifie les relations OneToOne avec Website"""
        website_related_models = [
            ('brands_design_colors', 'WebsiteColorConfig'),
            ('brands_design_typography', 'WebsiteTypographyConfig'),
            ('brands_design_spacing', 'WebsiteLayoutConfig'),
            ('brands_design_tailwind', 'WebsiteTailwindConfig')
        ]
        
        for app_name, model_name in website_related_models:
            model = apps.get_model(app_name, model_name)
            
            # Cherche le champ website
            website_field = None
            for field in model._meta.fields:
                if field.name == 'website':
                    website_field = field
                    break
            
            with self.subTest(app=app_name, model=model_name):
                self.assertIsNotNone(website_field, f"Field 'website' not found in {model_name}")
                self.assertIsInstance(website_field, models.OneToOneField,
                                    f"Field 'website' should be OneToOneField in {model_name}")
                self.assertEqual(website_field.related_model._meta.label, 'seo_websites_core.Website',
                               f"Website field should point to seo_websites_core.Website in {model_name}")
    
    def test_mixins_inheritance(self):
        """Vérifie que tous les modèles héritent de TimestampedMixin"""
        all_models = []
        
        for app_name in ['brands_design_colors', 'brands_design_typography', 
                        'brands_design_spacing', 'brands_design_tailwind']:
            app = apps.get_app_config(app_name)
            all_models.extend(app.get_models())
        
        for model in all_models:
            with self.subTest(model=model._meta.label):
                # Vérifie présence des champs TimestampedMixin
                field_names = [field.name for field in model._meta.fields]
                self.assertIn('created_at', field_names, 
                            f"created_at field missing in {model._meta.label}")
                self.assertIn('updated_at', field_names,
                            f"updated_at field missing in {model._meta.label}")
    
    def test_file_structure(self):
        """Vérifie la structure des fichiers dans chaque app"""
        required_structure = {
            'models': ['__init__.py'],
            'serializers': ['__init__.py'],
            'views': ['__init__.py'],
            'files': ['apps.py', 'urls.py']
        }
        
        for app_name in ['brands_design_colors', 'brands_design_typography',
                        'brands_design_spacing', 'brands_design_tailwind']:
            
            app_path = f"{app_name}"
            
            with self.subTest(app=app_name):
                self.assertTrue(os.path.exists(app_path), f"App directory {app_name} does not exist")
                
                # Vérifier dossiers
                for folder in ['models', 'serializers', 'views']:
                    folder_path = os.path.join(app_path, folder)
                    self.assertTrue(os.path.exists(folder_path), 
                                  f"Folder {folder} missing in {app_name}")
                    
                    # Vérifier __init__.py
                    init_file = os.path.join(folder_path, '__init__.py')
                    self.assertTrue(os.path.exists(init_file),
                                  f"__init__.py missing in {app_name}/{folder}")
                
                # Vérifier fichiers racine
                for filename in ['apps.py', 'urls.py']:
                    file_path = os.path.join(app_path, filename)
                    self.assertTrue(os.path.exists(file_path),
                                  f"File {filename} missing in {app_name}")
    
    def test_model_methods_exist(self):
        """Vérifie que les méthodes importantes existent sur les modèles"""
        method_checks = {
            ('brands_design_colors', 'BrandColorPalette'): ['to_css_variables'],
            ('brands_design_colors', 'WebsiteColorConfig'): [
                'get_effective_primary', 'get_effective_secondary', 'get_effective_accent'
            ],
            ('brands_design_typography', 'BrandTypography'): ['generate_font_sizes'],
            ('brands_design_typography', 'WebsiteTypographyConfig'): [
                'get_effective_font_primary', 'generate_effective_font_sizes'
            ],
            ('brands_design_spacing', 'BrandSpacingSystem'): ['generate_spacing_scale'],
            ('brands_design_spacing', 'WebsiteLayoutConfig'): [
                'get_effective_max_width', 'get_effective_grid_columns'
            ],
            ('brands_design_tailwind', 'WebsiteTailwindConfig'): [
                'generate_tailwind_config', 'generate_css_variables'
            ]
        }
        
        for (app_name, model_name), methods in method_checks.items():
            model = apps.get_model(app_name, model_name)
            
            for method_name in methods:
                with self.subTest(app=app_name, model=model_name, method=method_name):
                    self.assertTrue(hasattr(model, method_name),
                                  f"Method {method_name} missing in {model_name}")


if __name__ == '__main__':
    import django
    django.setup()
    pytest.main([__file__, '-v'])
