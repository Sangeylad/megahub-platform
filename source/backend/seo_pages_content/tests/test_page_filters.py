# backend/seo_pages_content/tests/test_page_filters.py

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from company_core.models import Company
from seo_websites_core.models import Website
from seo_pages_content.models import Page
from seo_pages_content.filters import PageFilter

# Imports conditionnels pour cross-app
try:
    from seo_pages_workflow.models import PageStatus
    from seo_pages_workflow.models import PageScheduling
    HAS_WORKFLOW = True
except ImportError:
    HAS_WORKFLOW = False

try:
    from seo_pages_hierarchy.models import PageHierarchy
    HAS_HIERARCHY = True
except ImportError:
    HAS_HIERARCHY = False

try:
    from seo_pages_keywords.models import PageKeyword
    from seo_keywords_base.models import Keyword
    HAS_KEYWORDS = True
except ImportError:
    HAS_KEYWORDS = False

try:
    from seo_pages_seo.models import PageSEO, PagePerformance
    HAS_SEO = True
except ImportError:
    HAS_SEO = False

try:
    from seo_pages_layout.models import PageLayout, PageSection
    HAS_LAYOUT = True
except ImportError:
    HAS_LAYOUT = False

# 🔥 NOUVEAU : Import categorization SEULEMENT
try:
    from seo_websites_categorization.models import WebsiteCategory, WebsiteCategorization
    HAS_CATEGORIZATION = True
except ImportError:
    HAS_CATEGORIZATION = False

User = get_user_model()

class PageFilterTestCase(TestCase):
    """Tests complets pour PageFilter cross-app"""
    
    def setUp(self):
        """Setup data pour tests"""
        # 🔥 1. D'ABORD créer l'admin de la company
        self.admin_user = User.objects.create_user(
            username="admin_user",
            email="admin@example.com", 
            password="adminpass123"
        )
        
        # 🔥 2. PUIS créer la company avec cet admin
        self.company = Company.objects.create(
            name="Test Company", 
            slots=10,
            admin=self.admin_user  # OBLIGATOIRE !
        )
        
        # 🔥 3. Assigner la company à l'admin (relation bidirectionnelle)
        self.admin_user.company = self.company
        self.admin_user.save()
        
        # 4. Créer le user de test normal
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            company=self.company  # Membre de la company
        )
        
        # 5. Brand & Website (inchangé)
        self.brand = Brand.objects.create(
            name="Test Brand",
            company=self.company,
            brand_admin=self.user  # Peut être l'user normal
        )
        
        self.website = Website.objects.create(
            name="Test Website",
            url="https://test.com",
            brand=self.brand,
            domain_authority=65
        )
        
        # Pages de base
        self.page_vitrine = Page.objects.create(
            title="Page Vitrine",
            url_path="/vitrine",
            website=self.website,
            page_type="vitrine",
            search_intent="MOFU",
            meta_description="Description vitrine"
        )
        
        self.page_blog = Page.objects.create(
            title="Article Blog",
            url_path="/blog/article",
            website=self.website,
            page_type="blog",
            search_intent="TOFU"
        )
        
        self.page_sans_meta = Page.objects.create(
            title="Page Sans Meta",
            url_path="/sans-meta",
            website=self.website,
            page_type="autre"
        )
        
        # Setup cross-app data si disponibles (IDENTIQUE À TON ORIGINAL)
        self._setup_workflow_data()
        self._setup_hierarchy_data()
        self._setup_keywords_data()
        self._setup_seo_data()
        self._setup_layout_data()
        self._setup_categorization_data()  # 🔥 JUSTE CETTE LIGNE AJOUTÉE
    
    # ===== TOUS TES SETUPS ORIGINAUX INCHANGÉS =====
    
    def _setup_workflow_data(self):
        """Setup workflow data si app disponible"""
        if not HAS_WORKFLOW:
            return
        
        # Status workflow
        self.status_published = PageStatus.objects.create(
            page=self.page_vitrine,
            status='published',
            status_changed_by=self.user
        )
        
        self.status_draft = PageStatus.objects.create(
            page=self.page_blog,
            status='draft',
            status_changed_by=self.user
        )
        
        self.status_scheduled = PageStatus.objects.create(
            page=self.page_sans_meta,
            status='scheduled',
            status_changed_by=self.user
        )
        
        # Scheduling pour page scheduled
        PageScheduling.objects.create(
            page=self.page_sans_meta,
            scheduled_publish_date=timezone.now() + timedelta(days=1),
            auto_publish=True,
            scheduled_by=self.user
        )
    
    def _setup_hierarchy_data(self):
        """Setup hierarchy data si app disponible"""
        if not HAS_HIERARCHY:
            return
        
        # Page parent (niveau 1)
        self.page_parent = Page.objects.create(
            title="Page Parent",
            url_path="/parent",
            website=self.website,
            page_type="vitrine"
        )
        
        # Hiérarchies
        PageHierarchy.objects.create(
            page=self.page_parent,
            parent=None  # Page racine
        )
        
        PageHierarchy.objects.create(
            page=self.page_vitrine,
            parent=self.page_parent  # Niveau 2
        )
        
        PageHierarchy.objects.create(
            page=self.page_blog,
            parent=None  # Page racine aussi
        )
    
    def _setup_keywords_data(self):
        """Setup keywords data si app disponible"""
        if not HAS_KEYWORDS:
            return
        
        # Créer des keywords de test
        self.keyword1 = Keyword.objects.create(
            keyword="seo test",
            volume=1000
        )
        self.keyword2 = Keyword.objects.create(
            keyword="marketing digital",
            volume=5000
        )
        
        # Associations page-keyword
        PageKeyword.objects.create(
            page=self.page_vitrine,
            keyword=self.keyword1,
            keyword_type='primary',
            is_ai_selected=True
        )
        
        PageKeyword.objects.create(
            page=self.page_vitrine,
            keyword=self.keyword2,
            keyword_type='secondary',
            is_ai_selected=False
        )
        
        PageKeyword.objects.create(
            page=self.page_blog,
            keyword=self.keyword1,
            keyword_type='secondary',
            is_ai_selected=True
        )
    
    def _setup_seo_data(self):
        """Setup SEO data si app disponible"""
        if not HAS_SEO:
            return
        
        # Config SEO (inchangé)
        PageSEO.objects.create(
            page=self.page_vitrine,
            featured_image="https://example.com/featured.jpg",
            sitemap_priority=0.8,
            sitemap_changefreq='weekly',
            exclude_from_sitemap=False
        )
        
        PageSEO.objects.create(
            page=self.page_blog,
            sitemap_priority=0.6,
            sitemap_changefreq='daily',
            exclude_from_sitemap=False
        )
        
        # 🔥 FIX : PagePerformance avec dates FUTURES (après updated_at)
        future_time = timezone.now() + timedelta(minutes=5)  # Dans le futur
        
        # Page vitrine : rendu APRÈS sa création (PAS besoin de régénération)
        PagePerformance.objects.create(
            page=self.page_vitrine,
            last_rendered_at=future_time,  # 🔥 FUTUR = pas de regen
            render_time_ms=250
        )
        
        # Page blog : BESOIN de régénération (pas de last_rendered_at)
        PagePerformance.objects.create(
            page=self.page_blog,
            last_rendered_at=None,  # 🔥 NULL = needs regeneration
            render_time_ms=None
        )
        
        # Page sans meta : rendu dans le futur aussi
        PagePerformance.objects.create(
            page=self.page_sans_meta,
            last_rendered_at=future_time + timedelta(minutes=1),
            render_time_ms=180
        )
        
        # Page parent : rendu dans le futur
        if hasattr(self, 'page_parent'):
            PagePerformance.objects.create(
                page=self.page_parent,
                last_rendered_at=future_time + timedelta(minutes=2),
                render_time_ms=320
            )
    
    def _setup_layout_data(self):
        """Setup layout data si app disponible"""
        if not HAS_LAYOUT:
            return
        
        # Layout config
        PageLayout.objects.create(
            page=self.page_vitrine,
            render_strategy='sections',
            layout_data={'template': 'hero_with_cta'}
        )
        
        # Sections
        PageSection.objects.create(
            page=self.page_vitrine,
            section_type='hero_banner',
            data={'title': 'Hero Title'},
            order=1,
            created_by=self.user
        )
        
        PageSection.objects.create(
            page=self.page_vitrine,
            section_type='cta_banner',
            data={'button': 'CTA Button'},
            order=2,
            created_by=self.user
        )
    
    def _setup_categorization_data(self):
        """🔥 NOUVEAU MINIMALISTE : Setup categorization data"""
        if not HAS_CATEGORIZATION:
            return
        
        # Créer UNE SEULE catégorie pour pas casser les comptes
        self.category_ecommerce = WebsiteCategory.objects.create(
            name="E-commerce",
            typical_da_range_min=30,
            typical_da_range_max=70,
            typical_pages_count=100
        )
        
        # Catégoriser le website (UNE SEULE catégorisation)
        self.categorization_primary = WebsiteCategorization.objects.create(
            website=self.website,
            category=self.category_ecommerce,
            is_primary=True,
            source='manual',
            categorized_by=self.user
        )
    
    # ===== TOUS TES TESTS ORIGINAUX IDENTIQUES =====
    
    def test_filter_title(self):
        """Test filtre par titre"""
        filter_set = PageFilter({'title': 'Vitrine'})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_vitrine)
    
    def test_filter_url_path(self):
        """Test filtre par URL"""
        filter_set = PageFilter({'url_path': 'blog'})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_blog)
    
    def test_filter_page_type(self):
        """Test filtre par type de page"""
        filter_set = PageFilter({'page_type': 'blog'})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_blog)
    
    def test_filter_search_intent(self):
        """Test filtre par intention de recherche"""
        filter_set = PageFilter({'search_intent': 'MOFU'})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_vitrine)
    
    def test_filter_has_meta_description(self):
        """Test filtre meta description"""
        # Avec meta
        filter_set = PageFilter({'has_meta_description': True})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_vitrine)
        
        # Sans meta
        filter_set = PageFilter({'has_meta_description': False})
        results = filter_set.qs.filter(website=self.website)
        self.assertIn(self.page_blog, results)
        self.assertIn(self.page_sans_meta, results)
    
    def test_filter_search_global(self):
        """Test recherche globale"""
        filter_set = PageFilter({'search': 'Article'})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_blog)
    
    # ===== TESTS WORKFLOW =====
    
    @pytest.mark.skipif(not HAS_WORKFLOW, reason="Workflow app not available")
    def test_filter_workflow_status(self):
        """Test filtre statut workflow"""
        filter_set = PageFilter({'workflow_status': 'published'})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_vitrine)
    
    @pytest.mark.skipif(not HAS_WORKFLOW, reason="Workflow app not available")
    def test_filter_is_published(self):
        """Test filtre pages publiées"""
        filter_set = PageFilter({'is_published': True})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_vitrine)
    
    @pytest.mark.skipif(not HAS_WORKFLOW, reason="Workflow app not available")
    def test_filter_is_scheduled(self):
        """Test filtre pages programmées"""
        filter_set = PageFilter({'is_scheduled': True})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_sans_meta)
    
    # ===== TESTS HIERARCHY =====
    
    @pytest.mark.skipif(not HAS_HIERARCHY, reason="Hierarchy app not available")
    def test_filter_hierarchy_level(self):
        """Test filtre niveau hiérarchique"""
        # Niveau 1 (racines)
        filter_set = PageFilter({'hierarchy_level': 1})
        results = filter_set.qs.filter(website=self.website)
        self.assertIn(self.page_parent, results)
        self.assertIn(self.page_blog, results)
        
        # Niveau 2
        filter_set = PageFilter({'hierarchy_level': 2})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_vitrine)
    
    @pytest.mark.skipif(not HAS_HIERARCHY, reason="Hierarchy app not available")
    def test_filter_has_parent(self):
        """Test filtre pages avec parent"""
        filter_set = PageFilter({'has_parent': True})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_vitrine)
    
    @pytest.mark.skipif(not HAS_HIERARCHY, reason="Hierarchy app not available")
    def test_filter_has_children(self):
        """Test filtre pages avec enfants"""
        filter_set = PageFilter({'has_children': True})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_parent)
    
    # ===== TESTS KEYWORDS =====
    
    @pytest.mark.skipif(not HAS_KEYWORDS, reason="Keywords app not available")
    def test_filter_has_keywords(self):
        """Test filtre pages avec mots-clés"""
        filter_set = PageFilter({'has_keywords': True})
        results = filter_set.qs.filter(website=self.website)
        self.assertIn(self.page_vitrine, results)
        self.assertIn(self.page_blog, results)
        self.assertNotIn(self.page_sans_meta, results)
    
    @pytest.mark.skipif(not HAS_KEYWORDS, reason="Keywords app not available")
    def test_filter_keyword_type(self):
        """Test filtre par type de mot-clé"""
        filter_set = PageFilter({'keyword_type': 'primary'})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_vitrine)
    
    @pytest.mark.skipif(not HAS_KEYWORDS, reason="Keywords app not available")
    def test_filter_has_primary_keyword(self):
        """Test filtre mot-clé principal"""
        filter_set = PageFilter({'has_primary_keyword': True})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_vitrine)
    
    @pytest.mark.skipif(not HAS_KEYWORDS, reason="Keywords app not available")
    def test_filter_is_ai_selected(self):
        """Test filtre mots-clés sélectionnés par IA"""
        filter_set = PageFilter({'is_ai_selected': True})
        results = filter_set.qs.filter(website=self.website)
        self.assertIn(self.page_vitrine, results)
        self.assertIn(self.page_blog, results)
    
    # ===== TESTS SEO =====
    
    @pytest.mark.skipif(not HAS_SEO, reason="SEO app not available")
    def test_filter_sitemap_priority(self):
        """Test filtre priorité sitemap"""
        filter_set = PageFilter({'sitemap_priority_min': 0.7})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_vitrine)
    
    @pytest.mark.skipif(not HAS_SEO, reason="SEO app not available")
    def test_filter_has_featured_image(self):
        """Test filtre image featured"""
        filter_set = PageFilter({'has_featured_image': True})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_vitrine)
    
    @pytest.mark.skipif(not HAS_SEO, reason="SEO app not available")
    def test_filter_sitemap_changefreq(self):
        """Test filtre fréquence sitemap"""
        filter_set = PageFilter({'sitemap_changefreq': 'weekly'})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_vitrine)
    
    @pytest.mark.skipif(not HAS_SEO, reason="SEO app not available")
    def test_filter_needs_regeneration(self):
        """Test filtre pages à régénérer"""
        print(f"\n=== DEBUG NEEDS_REGENERATION ===")
        
        # 🔥 1. Voir toutes les pages créées
        all_pages = Page.objects.filter(website=self.website)
        print(f"Total pages in website: {all_pages.count()}")
        for page in all_pages:
            print(f"  - {page.title} (ID: {page.id})")
        
        # 🔥 2. Voir toutes les PagePerformance créées
        if HAS_SEO:
            from seo_pages_seo.models import PagePerformance
            all_perfs = PagePerformance.objects.all()
            print(f"\nTotal PagePerformance records: {all_perfs.count()}")
            for perf in all_perfs:
                print(f"  - Page: {perf.page.title}, last_rendered_at: {perf.last_rendered_at}")
        
        # 🔥 3. Tester le filtre step by step
        from seo_pages_content.filters import PageFilter
        filter_set = PageFilter({'needs_regeneration': True})
        
        # Voir la query SQL générée
        from django.db import connection
        queryset = filter_set.qs.filter(website=self.website)
        query = str(queryset.query)
        print(f"\nSQL Query: {query}")
        
        # Voir les résultats
        results = list(queryset)
        print(f"\nFilter results: {len(results)} pages")
        for result in results:
            print(f"  - {result.title}")
        
        print("=" * 40)
        
        # Test original
        self.assertEqual(len(results), 1)
        if len(results) == 1:
            self.assertEqual(results[0], self.page_blog)
    
    # ===== TESTS LAYOUT =====
    
    @pytest.mark.skipif(not HAS_LAYOUT, reason="Layout app not available")
    def test_filter_has_layout(self):
        """Test filtre pages avec layout"""
        filter_set = PageFilter({'has_layout': True})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_vitrine)
    
    @pytest.mark.skipif(not HAS_LAYOUT, reason="Layout app not available")
    def test_filter_render_strategy(self):
        """Test filtre stratégie de rendu"""
        filter_set = PageFilter({'render_strategy': 'sections'})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_vitrine)
    
    @pytest.mark.skipif(not HAS_LAYOUT, reason="Layout app not available")
    def test_filter_has_sections(self):
        """Test filtre pages avec sections"""
        filter_set = PageFilter({'has_sections': True})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_vitrine)
    
    @pytest.mark.skipif(not HAS_LAYOUT, reason="Layout app not available")
    def test_filter_section_type(self):
        """Test filtre par type de section"""
        filter_set = PageFilter({'section_type': 'hero_banner'})
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_vitrine)
    
    # ===== TESTS COMBINÉS =====
    
    def test_filter_combined_basic(self):
        """Test filtres combinés de base"""
        filter_set = PageFilter({
            'page_type': 'vitrine',
            'search_intent': 'MOFU',
            'has_meta_description': True
        })
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_vitrine)
    
    @pytest.mark.skipif(not (HAS_WORKFLOW and HAS_KEYWORDS), reason="Cross-apps not available")
    def test_filter_combined_cross_app(self):
        """Test filtres combinés cross-app"""
        filter_set = PageFilter({
            'workflow_status': 'published',
            'has_keywords': True,
            'keyword_type': 'primary'
        })
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.page_vitrine)
    
    def test_filter_no_results(self):
        """Test filtres sans résultats"""
        filter_set = PageFilter({
            'page_type': 'inexistant',
            'search_intent': 'BOFU'
        })
        results = filter_set.qs.filter(website=self.website)
        self.assertEqual(results.count(), 0)

    # ===== 🔥 NOUVEAUX TESTS MINIMALISTES =====
    
    @pytest.mark.skipif(not HAS_CATEGORIZATION, reason="Categorization app not available")
    def test_filter_website_name(self):
        """Test filtre nom du website"""
        filter_set = PageFilter({'website_name': 'Test'})
        results = filter_set.qs.filter(website=self.website)
        # Nombre de pages dépend de si hierarchy est activé ou pas
        expected_count = 4 if HAS_HIERARCHY else 3
        self.assertEqual(results.count(), expected_count)
    
    @pytest.mark.skipif(not HAS_CATEGORIZATION, reason="Categorization app not available")
    def test_filter_has_primary_category(self):
        """Test filtre présence catégorie principale"""
        filter_set = PageFilter({'has_primary_category': True})
        results = filter_set.qs.filter(website=self.website)
        expected_count = 4 if HAS_HIERARCHY else 3
        self.assertEqual(results.count(), expected_count)


# ===== SCRIPT DE TEST MANUEL IDENTIQUE =====

def run_manual_filter_tests():
    """
    Script pour tester manuellement tous les filtres
    Usage: python manage.py shell -c "from seo_pages_content.tests.test_page_filters import run_manual_filter_tests; run_manual_filter_tests()"
    """
    from django.db import connection
    from seo_pages_content.models import Page
    
    print("🔥 MANUAL FILTER TESTING SCRIPT")
    print("=" * 50)
    
    # Test chaque filtre individuellement
    filters_to_test = [
        # Base filters
        {'title': 'Page'},
        {'url_path': '/'},
        {'page_type': 'vitrine'},
        {'search_intent': 'TOFU'},
        {'has_meta_description': True},
        
        # Workflow filters (if available)
        {'workflow_status': 'published'},
        {'is_published': True},
        {'is_scheduled': False},
        
        # Hierarchy filters (if available)
        {'hierarchy_level': 1},
        {'has_parent': False},
        {'has_children': True},
        {'is_root_page': True},
        
        # Keywords filters (if available)
        {'has_keywords': True},
        {'keyword_type': 'primary'},
        {'has_primary_keyword': True},
        {'is_ai_selected': True},
        
        # SEO filters (if available)
        {'sitemap_priority_min': 0.5},
        {'has_featured_image': True},
        {'sitemap_changefreq': 'weekly'},
        {'exclude_from_sitemap': False},
        
        # Layout filters (if available)
        {'has_layout': True},
        {'render_strategy': 'sections'},
        {'has_sections': True},
        {'section_type': 'hero_banner'},
        
        # Performance filters (if available)
        {'needs_regeneration': False},
        
        # 🔥 NOUVEAUX tests minimalistes
        {'website_name': 'Test'},
        {'has_primary_category': True},
        
        # Global search
        {'search': 'test'},
    ]
    
    for i, filter_params in enumerate(filters_to_test, 1):
        print(f"\n{i:2d}. Testing filter: {filter_params}")
        
        try:
            # Test avec Django ORM
            filter_set = PageFilter(filter_params)
            count = filter_set.qs.count()
            
            # Test SQL query 
            with connection.cursor() as cursor:
                query = str(filter_set.qs.query)
                
            print(f"    ✅ Results: {count} pages")
            print(f"    📝 SQL: {query[:100]}...")
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)[:100]}...")
    
    print(f"\n🎯 FILTER TESTING COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    run_manual_filter_tests()