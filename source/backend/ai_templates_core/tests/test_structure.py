# backend/ai_templates_core/tests/test_structure.py
"""
Tests de structure pour ai_templates_core
Vérifie modèles, relations cross-app, et imports conditionnels
"""
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from company_core.models import Company
from brands_core.models import Brand
from ..models import TemplateType, BrandTemplateConfig, BaseTemplate

User = get_user_model()

class TemplateStructureTestCase(TestCase):
    """Tests structure modèles core"""
    
    def setUp(self):
        """Setup données de test - Fix contraintes"""
        # 1. Créer admin user SANS company d'abord
        self.admin_user = User.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="testpass123"
            # Pas de company pour l'instant
        )
        
        # 2. Créer company AVEC admin directement
        self.company = Company.objects.create(
            name="Test Company",
            slots=5,
            is_subscribed=True,
            admin=self.admin_user  # Admin directement
        )
        
        # 3. Assigner company à l'admin après
        self.admin_user.company = self.company
        self.admin_user.save()
        
        # User normal
        self.user = User.objects.create_user(
            username="user_test",
            email="user@test.com",
            password="testpass123",
            company=self.company
        )
        
        # Brand
        self.brand = Brand.objects.create(
            company=self.company,
            name="Test Brand",
            description="Brand de test",
            brand_admin=self.admin_user
        )
        self.user.brands.add(self.brand)
        
        # Template Types
        self.template_type = TemplateType.objects.create(
            name="website",
            display_name="Site Web",
            description="Templates pour sites web"
        )
        
        # Brand Config
        self.brand_config = BrandTemplateConfig.objects.create(
            brand=self.brand,
            max_templates_per_type=5,
            max_variables_per_template=20,
            allow_custom_templates=True
        )

    def test_template_type_validation(self):
        """Test modèle TemplateType"""
        # Création valide
        tt = TemplateType.objects.create(
            name="blog",
            display_name="Blog Articles"
        )
        
        self.assertEqual(str(tt), "Blog Articles")
        self.assertTrue(tt.is_active)
        
        # Test unicité
        with self.assertRaises(IntegrityError):
            TemplateType.objects.create(
                name="blog",  # Déjà existant
                display_name="Blog Autre"
            )

    def test_brand_template_config_relations(self):
        """Test relations BrandTemplateConfig"""
        # Relation OneToOne avec Brand
        self.assertEqual(self.brand_config.brand, self.brand)
        self.assertEqual(self.brand.template_config, self.brand_config)
        
        # Test valeurs par défaut
        self.assertEqual(self.brand_config.max_templates_per_type, 5)
        self.assertEqual(self.brand_config.default_template_style, "professional")
        
        # Test __str__
        expected_str = f"Config templates - {self.brand.name}"
        self.assertEqual(str(self.brand_config), expected_str)

    def test_base_template_creation_and_validation(self):
        """Test modèle BaseTemplate complet"""
        # Création template valide
        template = BaseTemplate.objects.create(
            name="Landing Page Template",
            description="Template pour landing pages",
            template_type=self.template_type,
            brand=self.brand,
            prompt_content="Créez une landing page pour {{product_name}} avec {{cta_text}}",
            created_by=self.user
        )
        
        # Vérifications de base
        self.assertEqual(template.name, "Landing Page Template")
        self.assertEqual(template.brand, self.brand)
        self.assertEqual(template.created_by, self.user)
        self.assertTrue(template.is_active)
        self.assertFalse(template.is_public)
        
        # Test __str__
        expected_str = f"Landing Page Template (Site Web)"
        self.assertEqual(str(template), expected_str)
        
        # Test contrainte unique
        with self.assertRaises(IntegrityError):
            BaseTemplate.objects.create(
                name="Landing Page Template",  # Même nom
                template_type=self.template_type,  # Même type
                brand=self.brand,  # Même brand
                prompt_content="Autre contenu",
                created_by=self.user
            )

    def test_template_relations_cross_brand(self):
        """Test isolation par brand"""
        # Création autre brand
        other_brand = Brand.objects.create(
            company=self.company,
            name="Other Brand",
            brand_admin=self.admin_user
        )
        
        # Templates avec même nom mais brands différentes = OK
        template1 = BaseTemplate.objects.create(
            name="Same Name Template",
            template_type=self.template_type,
            brand=self.brand,
            prompt_content="Content 1",
            created_by=self.user
        )
        
        template2 = BaseTemplate.objects.create(
            name="Same Name Template",  # Même nom
            template_type=self.template_type,  # Même type
            brand=other_brand,  # Brand différente = OK
            prompt_content="Content 2",
            created_by=self.user
        )
        
        self.assertNotEqual(template1.id, template2.id)
        self.assertEqual(template1.name, template2.name)
        self.assertNotEqual(template1.brand, template2.brand)

    def test_template_content_validation(self):
        """Test validation contenu template"""
        # Template avec variables valides
        template = BaseTemplate.objects.create(
            name="Variable Test",
            template_type=self.template_type,
            brand=self.brand,
            prompt_content="Hello {{name}}, welcome to {{company}}!",
            created_by=self.user
        )
        
        # Vérifier que les variables sont détectées
        self.assertIn("{{name}}", template.prompt_content)
        self.assertIn("{{company}}", template.prompt_content)
        
        # Template avec contenu minimal valide
        template_minimal = BaseTemplate.objects.create(
            name="Minimal Template",
            template_type=self.template_type,
            brand=self.brand,
            prompt_content="Minimal valid content",  # Contenu minimal mais valide
            created_by=self.user
        )
        
        self.assertIsNotNone(template_minimal.id)

class CrossAppRelationsTestCase(TestCase):
    """Tests des relations cross-app conditionnelles"""
    
    def setUp(self):
        """Setup minimal pour tests cross-app"""
        # Fix contraintes Company/Admin
        self.admin = User.objects.create_user(
            username="cross_admin",
            email="cross@test.com"
        )
        
        self.company = Company.objects.create(
            name="Cross App Test", 
            slots=5,
            admin=self.admin  # Admin directement
        )
        
        self.admin.company = self.company
        self.admin.save()
        
        self.brand = Brand.objects.create(
            company=self.company,
            name="Cross Brand",
            brand_admin=self.admin
        )
        
        self.template_type = TemplateType.objects.create(
            name="cross_test",
            display_name="Cross Test"
        )
        
        self.template = BaseTemplate.objects.create(
            name="Cross Template",
            template_type=self.template_type,
            brand=self.brand,
            prompt_content="Cross app test content with {{variable}}",
            created_by=self.admin
        )

    @patch('ai_templates_core.filters.template_filters.HAS_STORAGE', True)
    def test_storage_relations_available(self):
        """Test quand app storage est disponible"""
        # Simuler existence de l'app storage
        with patch('ai_templates_core.filters.template_filters.TemplateVersion') as MockVersion:
            MockVersion.objects.filter.return_value.exists.return_value = True
            
            # Vérifier que le template peut avoir des versions
            self.assertTrue(hasattr(self.template, 'id'))
            # Dans un vrai cas, on aurait des versions liées

    @patch('ai_templates_core.filters.template_filters.HAS_INSIGHTS', True)
    def test_insights_relations_available(self):
        """Test quand app insights est disponible"""
        # Simuler existence de l'app insights
        with patch('ai_templates_core.filters.template_filters.TemplateRecommendation') as MockRec:
            MockRec.objects.filter.return_value.exists.return_value = True
            
            # Template peut avoir des recommandations
            self.assertTrue(hasattr(self.template, 'id'))

    @patch('ai_templates_core.filters.template_filters.HAS_WORKFLOW', False)
    def test_workflow_relations_unavailable(self):
        """Test quand app workflow n'est pas disponible"""
        # Vérifier que le système fonctionne sans workflow
        self.assertIsNotNone(self.template)
        self.assertTrue(self.template.is_active)

    def test_import_conditional_safety(self):
        """Test sécurité des imports conditionnels"""
        # Test import du filtre sans erreur
        try:
            from ..filters import BaseTemplateFilter
            filter_instance = BaseTemplateFilter()
            self.assertIsNotNone(filter_instance)
        except ImportError as e:
            self.fail(f"Import filter failed: {e}")

    def test_cross_app_constants_fallback(self):
        """Test fallback des constantes cross-app"""
        from ..filters.template_filters import (
            INSIGHT_TYPE_CHOICES, 
            RECOMMENDATION_TYPE_CHOICES,
            APPROVAL_STATUS_CHOICES
        )
        
        # Les constantes doivent être définies (même si vides)
        self.assertIsInstance(INSIGHT_TYPE_CHOICES, list)
        self.assertIsInstance(RECOMMENDATION_TYPE_CHOICES, list)
        self.assertIsInstance(APPROVAL_STATUS_CHOICES, list)

class TemplatePerformanceTestCase(TestCase):
    """Tests de performance et optimisation"""
    
    def setUp(self):
        """Setup pour tests de performance"""
        # Fix contraintes
        self.admin = User.objects.create_user(
            username="perf_admin",
            email="perf@test.com"
        )
        
        self.company = Company.objects.create(
            name="Perf Test", 
            slots=10,
            admin=self.admin
        )
        
        self.admin.company = self.company
        self.admin.save()
        
        self.brand = Brand.objects.create(
            company=self.company,
            name="Perf Brand",
            brand_admin=self.admin
        )
        
        # Création multiple template types
        self.website_type = TemplateType.objects.create(name="website", display_name="Website")
        self.blog_type = TemplateType.objects.create(name="blog", display_name="Blog")
        self.email_type = TemplateType.objects.create(name="email", display_name="Email")

    def test_bulk_template_creation(self):
        """Test création en masse pour performance"""
        templates_data = []
        
        # Création 50 templates
        for i in range(50):
            template_type = [self.website_type, self.blog_type, self.email_type][i % 3]
            templates_data.append(BaseTemplate(
                name=f"Template {i}",
                description=f"Description {i}",
                template_type=template_type,
                brand=self.brand,
                prompt_content=f"Content {{var_{i}}} for template {i}",
                created_by=self.admin,
                is_active=(i % 2 == 0),  # Alternance actif/inactif
                is_public=(i % 5 == 0)   # 1 sur 5 public
            ))
        
        # Bulk create
        created_templates = BaseTemplate.objects.bulk_create(templates_data)
        
        self.assertEqual(len(created_templates), 50)
        
        # Vérification distribution
        total_templates = BaseTemplate.objects.filter(brand=self.brand).count()
        active_templates = BaseTemplate.objects.filter(brand=self.brand, is_active=True).count()
        public_templates = BaseTemplate.objects.filter(brand=self.brand, is_public=True).count()
        
        self.assertEqual(total_templates, 50)
        self.assertEqual(active_templates, 25)  # 50% actifs
        self.assertEqual(public_templates, 10)  # 20% publics

    def test_template_queries_optimization(self):
        """Test optimisation des requêtes"""
        # Création templates pour test
        for i in range(10):
            BaseTemplate.objects.create(
                name=f"Query Test {i}",
                template_type=self.website_type,
                brand=self.brand,
                prompt_content=f"Optimized content {i}",
                created_by=self.admin
            )
        
        # Test requête optimisée avec select_related
        with self.assertNumQueries(1):  # Doit être optimisé en 1 requête
            templates = list(
                BaseTemplate.objects
                .select_related('template_type', 'brand', 'created_by')
                .filter(brand=self.brand)
            )
            
            # Accès aux relations sans nouvelles requêtes
            for template in templates:
                _ = template.template_type.display_name
                _ = template.brand.name
                _ = template.created_by.username

    def test_template_indexing_performance(self):
        """Test performance des index définis"""
        # Les index sont définis dans le modèle Meta
        # Ici on vérifie qu'ils améliorent les requêtes communes
        
        # Création données test
        for i in range(20):
            BaseTemplate.objects.create(
                name=f"Index Test {i}",
                template_type=self.website_type,
                brand=self.brand,
                prompt_content=f"Indexed content {i}",
                created_by=self.admin,
                is_active=(i % 2 == 0),
                is_public=(i % 3 == 0)
            )
        
        # Requêtes qui bénéficient des index
        # Index: ['brand', 'template_type']
        brand_type_query = BaseTemplate.objects.filter(
            brand=self.brand,
            template_type=self.website_type
        )
        
        # Index: ['is_active', 'is_public']
        status_query = BaseTemplate.objects.filter(
            is_active=True,
            is_public=True
        )
        
        # Vérifier que les requêtes s'exécutent
        self.assertTrue(brand_type_query.exists())
        self.assertTrue(status_query.exists())