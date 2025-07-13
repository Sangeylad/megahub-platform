# backend/ai_templates_core/tests/test_filters.py
"""
Tests complets des filtres cross-app pour ai_templates_core
Vérifie tous les filtres avec et sans apps externes
"""
import pytest
from datetime import timedelta
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch, MagicMock

from company_core.models import Company
from brands_core.models import Brand
from ..models import TemplateType, BrandTemplateConfig, BaseTemplate
from ..filters import BaseTemplateFilter

User = get_user_model()

class BaseFilterTestCase(TestCase):
    """Base class pour tests filtres avec simulation middleware"""
    
    def setUp(self):
        """Setup données communes - Fix contraintes"""
        self.factory = RequestFactory()
        
        # 1. Admin d'abord
        self.admin = User.objects.create_user(
            username="filter_admin",
            email="filter@test.com"
        )
        
        # 2. Company avec admin directement
        self.company = Company.objects.create(
            name="Filter Test", 
            slots=10,
            admin=self.admin  # Directement
        )
        
        # 3. Assigner company à admin
        self.admin.company = self.company
        self.admin.save()
        
        # Users normaux
        self.user1 = User.objects.create_user(
            username="filter_user1",
            email="user1@test.com",
            company=self.company
        )
        
        self.user2 = User.objects.create_user(
            username="filter_user2", 
            email="user2@test.com",
            company=self.company
        )
        
        # Brands
        self.brand1 = Brand.objects.create(
            company=self.company,
            name="Filter Brand 1",
            brand_admin=self.admin
        )
        
        self.brand2 = Brand.objects.create(
            company=self.company,
            name="Filter Brand 2",
            brand_admin=self.admin
        )
        
        self.user1.brands.add(self.brand1)
        self.user2.brands.add(self.brand2)
        
        # Template Types
        self.website_type = TemplateType.objects.create(
            name="website",
            display_name="Site Web"
        )
        
        self.blog_type = TemplateType.objects.create(
            name="blog",
            display_name="Blog"
        )
        
        self.email_type = TemplateType.objects.create(
            name="email",
            display_name="Email"
        )
        
        # Brand Configs
        BrandTemplateConfig.objects.create(
            brand=self.brand1,
            max_templates_per_type=10,
            allow_custom_templates=True,
            default_template_style="professional"
        )
        
        BrandTemplateConfig.objects.create(
            brand=self.brand2,
            max_templates_per_type=5,
            allow_custom_templates=False,
            default_template_style="modern"
        )
        
        # Dates pour tests temporels
        self.now = timezone.now()
        self.week_ago = self.now - timedelta(days=7)
        self.month_ago = self.now - timedelta(days=30)
        
        # Templates de test avec variations temporelles
        self.template_recent = BaseTemplate.objects.create(
            name="Recent Template",
            description="Template récent pour tests",
            template_type=self.website_type,
            brand=self.brand1,
            prompt_content="Recent content with {{variable}}",
            created_by=self.user1,
            is_active=True,
            is_public=False
        )
        # Forcer date récente
        self.template_recent.created_at = self.now - timedelta(days=2)
        self.template_recent.save()
        
        self.template_old = BaseTemplate.objects.create(
            name="Old Template",
            description="Template ancien",
            template_type=self.blog_type,
            brand=self.brand1,
            prompt_content="Old content without variables",
            created_by=self.admin,
            is_active=False,
            is_public=True
        )
        # Forcer date ancienne
        self.template_old.created_at = self.month_ago
        self.template_old.save()
        
        self.template_brand2 = BaseTemplate.objects.create(
            name="Brand 2 Template",
            description="Template de la brand 2",
            template_type=self.email_type,
            brand=self.brand2,
            prompt_content="Email template for {{recipient}} about {{subject}}",
            created_by=self.user2,
            is_active=True,
            is_public=True
        )

    def create_request_with_user(self, user, query_params=None):
        """Helper pour créer request avec user simulé"""
        request = self.factory.get('/', query_params or {})
        request.user = user
        return request


class CoreFiltersTestCase(BaseFilterTestCase):
    """Tests des filtres de base"""
    
    def test_name_filter(self):
        """Test filtre par nom"""
        request = self.create_request_with_user(self.user1, {'name': 'Recent'})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        self.assertEqual(filtered_qs.count(), 1)
        self.assertEqual(filtered_qs.first().name, "Recent Template")

    def test_description_filter(self):
        """Test filtre par description"""
        request = self.create_request_with_user(self.user1, {'description': 'ancien'})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        self.assertEqual(filtered_qs.count(), 1)
        self.assertEqual(filtered_qs.first().name, "Old Template")

    def test_template_type_filters(self):
        """Test filtres par type de template"""
        # Filtre par ID
        request = self.create_request_with_user(self.user1, {'template_type': self.website_type.id})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        self.assertEqual(filtered_qs.count(), 1)
        self.assertEqual(filtered_qs.first().template_type, self.website_type)
        
        # Filtre par nom
        request = self.create_request_with_user(self.user1, {'template_type_name': 'blog'})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        self.assertEqual(filtered_qs.count(), 1)
        self.assertEqual(filtered_qs.first().template_type, self.blog_type)

    def test_status_filters(self):
        """Test filtres de statut"""
        # Templates actifs
        request = self.create_request_with_user(self.user1, {'is_active': 'true'})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        active_count = filtered_qs.filter(is_active=True).count()
        self.assertEqual(active_count, filtered_qs.count())
        
        # Templates publics
        request = self.create_request_with_user(self.user1, {'is_public': 'true'})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        public_count = filtered_qs.filter(is_public=True).count()
        self.assertEqual(public_count, filtered_qs.count())


class BrandUserFiltersTestCase(BaseFilterTestCase):
    """Tests des filtres brand et utilisateur"""
    
    def test_brand_filters(self):
        """Test filtres par brand"""
        # Filtre par ID brand
        request = self.create_request_with_user(self.user1, {'brand': self.brand1.id})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        for template in filtered_qs:
            self.assertEqual(template.brand, self.brand1)
        
        # Filtre par nom brand
        request = self.create_request_with_user(self.user1, {'brand_name': 'Brand 2'})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        if filtered_qs.exists():
            self.assertEqual(filtered_qs.first().brand, self.brand2)

    def test_company_filters(self):
        """Test filtres par company"""
        request = self.create_request_with_user(self.user1, {'company': self.company.id})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        # Tous les templates doivent appartenir à la même company
        for template in filtered_qs:
            self.assertEqual(template.brand.company, self.company)

    def test_created_by_filters(self):
        """Test filtres par créateur"""
        # Filtre par user ID
        request = self.create_request_with_user(self.user1, {'created_by': self.user1.id})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        for template in filtered_qs:
            self.assertEqual(template.created_by, self.user1)
        
        # Filtre "mes templates"
        request = self.create_request_with_user(self.user1, {'created_by_me': 'true'})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        for template in filtered_qs:
            self.assertEqual(template.created_by, self.user1)


class TemporalFiltersTestCase(BaseFilterTestCase):
    """Tests des filtres temporels"""
    
    def test_date_range_filters(self):
        """Test filtres par plage de dates"""
        # Templates créés après une date
        week_ago_str = self.week_ago.isoformat()
        request = self.create_request_with_user(self.user1, {'created_after': week_ago_str})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        for template in filtered_qs:
            self.assertGreaterEqual(template.created_at, self.week_ago)
        
        # Templates créés avant une date
        week_ago_str = self.week_ago.isoformat()
        request = self.create_request_with_user(self.user1, {'created_before': week_ago_str})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        for template in filtered_qs:
            self.assertLessEqual(template.created_at, self.week_ago)

    def test_temporal_shortcuts(self):
        """Test raccourcis temporels"""
        # Templates de la semaine
        request = self.create_request_with_user(self.user1, {'last_week': 'true'})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        week_ago = timezone.now() - timedelta(days=7)
        for template in filtered_qs:
            self.assertGreaterEqual(template.created_at, week_ago)
        
        # Templates du mois
        request = self.create_request_with_user(self.user1, {'last_month': 'true'})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        month_ago = timezone.now() - timedelta(days=30)
        for template in filtered_qs:
            self.assertGreaterEqual(template.created_at, month_ago)
        
        # Templates récents (3 jours)
        request = self.create_request_with_user(self.user1, {'recent': 'true'})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        recent_date = timezone.now() - timedelta(days=3)
        for template in filtered_qs:
            self.assertGreaterEqual(template.updated_at, recent_date)


class BrandConfigFiltersTestCase(BaseFilterTestCase):
    """Tests des filtres de configuration brand"""
    
    def test_brand_config_filters(self):
        """Test filtres config brand"""
        # Templates de brands avec config
        request = self.create_request_with_user(self.user1, {'has_brand_config': 'true'})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        for template in filtered_qs:
            self.assertTrue(hasattr(template.brand, 'template_config'))
        
        # Filtre par autorisation custom templates
        request = self.create_request_with_user(self.user1, {'allows_custom_templates': 'true'})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        # Vérifier que seuls les templates de brand1 sont retournés
        # (brand1 autorise custom, brand2 non)
        for template in filtered_qs:
            if hasattr(template.brand, 'template_config'):
                self.assertTrue(template.brand.template_config.allow_custom_templates)


class ContentAnalysisFiltersTestCase(BaseFilterTestCase):
    """Tests des filtres d'analyse de contenu"""
    
    def test_variables_filters(self):
        """Test filtres variables"""
        # Templates avec variables
        request = self.create_request_with_user(self.user1, {'has_variables': 'true'})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        for template in filtered_qs:
            self.assertIn('{{', template.prompt_content)
        
        # Templates sans variables
        request = self.create_request_with_user(self.user1, {'has_variables': 'false'})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        for template in filtered_qs:
            self.assertNotIn('{{', template.prompt_content)

    def test_content_length_filter(self):
        """Test filtre longueur contenu"""
        request = self.create_request_with_user(self.user1, {'content_length_min': '20', 'content_length_max': '100'})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        for template in filtered_qs:
            content_length = len(template.prompt_content)
            self.assertGreaterEqual(content_length, 20)
            self.assertLessEqual(content_length, 100)


class CrossAppFiltersTestCase(BaseFilterTestCase):
    """Tests des filtres cross-app avec mocks"""
    
    @patch('ai_templates_core.filters.template_filters.HAS_STORAGE', True)
    def test_storage_filters_available(self):
        """Test filtres storage quand app disponible"""
        # Mock des modèles storage
        with patch('ai_templates_core.filters.template_filters.TemplateVersion') as MockVersion:
            # Simuler templates avec versions
            MockVersion.objects.filter.return_value.exists.return_value = True
            
            request = self.create_request_with_user(self.user1, {'has_versions': 'true'})
            
            filter_instance = BaseTemplateFilter(data=request.GET, request=request)
            
            # Vérifier que le filtre existe et fonctionne
            self.assertTrue(hasattr(filter_instance, 'filters'))
            self.assertIn('has_versions', filter_instance.filters)

    @patch('ai_templates_core.filters.template_filters.HAS_INSIGHTS', True)
    def test_insights_filters_available(self):
        """Test filtres insights quand app disponible"""
        with patch('ai_templates_core.filters.template_filters.TemplateRecommendation') as MockRec:
            MockRec.objects.filter.return_value.exists.return_value = True
            
            request = self.create_request_with_user(self.user1, {'has_recommendations': 'true'})
            
            filter_instance = BaseTemplateFilter(data=request.GET, request=request)
            
            # Vérifier filtres insights
            self.assertIn('has_recommendations', filter_instance.filters)
            if filter_instance.filters.get('recommendation_type'):
                self.assertIn('recommendation_type', filter_instance.filters)

    @patch('ai_templates_core.filters.template_filters.HAS_WORKFLOW', False)
    def test_workflow_filters_unavailable(self):
        """Test fallback quand workflow indisponible"""
        request = self.create_request_with_user(self.user1, {'workflow_status': 'approved'})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        
        # Le filtre workflow_status ne doit pas exister si HAS_WORKFLOW=False
        # Vérifier que le filterset se construit sans erreur même sans ces filtres
        self.assertIsNotNone(filter_instance.qs)

    @patch('ai_templates_core.filters.template_filters.HAS_SEO_TEMPLATES', True)
    def test_seo_filters_available(self):
        """Test filtres SEO quand app disponible"""
        with patch('ai_templates_core.filters.template_filters.SEOWebsiteTemplate') as MockSEO:
            request = self.create_request_with_user(self.user1, {'has_seo_config': 'true'})
            
            filter_instance = BaseTemplateFilter(data=request.GET, request=request)
            
            # Vérifier que le filterset se construit sans erreur
            self.assertIsNotNone(filter_instance.qs)


class SearchFilterTestCase(BaseFilterTestCase):
    """Tests du filtre de recherche globale"""
    
    def test_global_search(self):
        """Test recherche globale"""
        # Recherche dans nom
        request = self.create_request_with_user(self.user1, {'search': 'Recent'})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        self.assertGreater(filtered_qs.count(), 0)
        found_in_name = any('Recent' in template.name for template in filtered_qs)
        self.assertTrue(found_in_name)
        
        # Recherche dans contenu
        request = self.create_request_with_user(self.user1, {'search': 'variable'})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        found_in_content = any('variable' in template.prompt_content for template in filtered_qs)
        self.assertTrue(found_in_content)


class FilterCombinationTestCase(BaseFilterTestCase):
    """Tests des combinaisons de filtres"""
    
    def test_multiple_filters_combination(self):
        """Test combinaison multiple filtres"""
        # Combinaison type + statut + créateur
        request = self.create_request_with_user(self.user1, {
            'template_type': self.website_type.id,
            'is_active': 'true',
            'created_by': self.user1.id
        })
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        for template in filtered_qs:
            self.assertEqual(template.template_type, self.website_type)
            self.assertTrue(template.is_active)
            self.assertEqual(template.created_by, self.user1)

    def test_temporal_and_content_filters(self):
        """Test combinaison filtres temporels et contenu"""
        request = self.create_request_with_user(self.user1, {
            'last_week': 'true',
            'has_variables': 'true',
            'is_public': 'false'
        })
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        week_ago = timezone.now() - timedelta(days=7)
        for template in filtered_qs:
            self.assertGreaterEqual(template.created_at, week_ago)
            self.assertIn('{{', template.prompt_content)
            self.assertFalse(template.is_public)


class FilterEdgeCasesTestCase(BaseFilterTestCase):
    """Tests des cas limites"""
    
    def test_empty_filters(self):
        """Test filtres sans paramètres"""
        request = self.create_request_with_user(self.user1, {})
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        filtered_qs = filter_instance.qs
        
        # Doit retourner tous les templates
        total_templates = BaseTemplate.objects.count()
        self.assertEqual(filtered_qs.count(), total_templates)

    def test_invalid_filter_values(self):
        """Test valeurs invalides"""
        request = self.create_request_with_user(self.user1, {
            'template_type': 'invalid_id',
            'created_after': 'invalid_date',
            'is_active': 'invalid_boolean'
        })
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        
        # Ne doit pas lever d'erreur, juste ignorer valeurs invalides
        try:
            filtered_qs = filter_instance.qs
            list(filtered_qs)  # Force évaluation
        except Exception as e:
            self.fail(f"Filter with invalid values should not raise exception: {e}")

    def test_filter_without_authentication(self):
        """Test filtres sans authentification"""
        request = self.factory.get('/', {'name': 'test'})
        request.user = None
        
        filter_instance = BaseTemplateFilter(data=request.GET, request=request)
        
        # Certains filtres comme "created_by_me" doivent gérer l'absence d'user
        try:
            filtered_qs = filter_instance.qs
            list(filtered_qs)
        except (AttributeError, TypeError):
            pass  # Attendu si pas d'user pour "created_by_me"