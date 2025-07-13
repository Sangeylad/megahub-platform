# backend/seo_websites_core/tests/test_website_filters_advanced.py

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from company_core.models import Company
from seo_websites_core.models import Website
from seo_websites_core.filters import WebsiteFilter

# Import conditionnel des modèles cross-app
try:
    from seo_pages_content.models import Page
    HAS_PAGES_CONTENT = True
except ImportError:
    HAS_PAGES_CONTENT = False

try:
    from seo_pages_seo.models import PageSEO
    HAS_SEO = True
except ImportError:
    HAS_SEO = False

try:
    from seo_pages_layout.models import PageLayout, PageSection
    HAS_LAYOUT = True
except ImportError:
    HAS_LAYOUT = False

try:
    from seo_websites_categorization.models import WebsiteCategory, WebsiteCategorization
    HAS_CATEGORIZATION = True
except ImportError:
    HAS_CATEGORIZATION = False

try:
    from seo_pages_keywords.models import PageKeyword
    from seo_keywords_base.models import Keyword
    HAS_KEYWORDS = True
except ImportError:
    HAS_KEYWORDS = False

User = get_user_model()


class WebsiteFilterAdvancedTestCase(TestCase):
    """Tests avancés pour WebsiteFilter - SEO, Layout, Categorization"""
    
    def setUp(self):
        """Setup data pour tests avancés"""
        # Setup identique au basic mais avec les apps avancées
        self.admin_user = User.objects.create_user(
            username="admin_user",
            email="admin@example.com", 
            password="adminpass123"
        )
        
        self.company = Company.objects.create(
            name="Test Company", 
            slots=10,
            admin=self.admin_user
        )
        
        self.admin_user.company = self.company
        self.admin_user.save()
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            company=self.company
        )
        
        # Brands & Websites
        self.brand_ecommerce = Brand.objects.create(
            name="Brand Ecommerce",
            company=self.company,
            brand_admin=self.user,
            chatgpt_key="sk-test123",
            gemini_key=""
        )
        
        self.brand_blog = Brand.objects.create(
            name="Brand Blog",
            company=self.company,
            brand_admin=self.user,
            chatgpt_key="",
            gemini_key="gemini-key-456"
        )
        
        self.brand_corporate = Brand.objects.create(
            name="Brand Corporate",
            company=self.company,
            brand_admin=self.user,
            chatgpt_key="sk-corporate789",
            gemini_key="gemini-corporate"
        )
        
        self.website_ecommerce = Website.objects.create(
            name="Site E-commerce",
            url="https://ecommerce.test.com",
            brand=self.brand_ecommerce,
            domain_authority=75,
            max_competitor_backlinks=50000,
            max_competitor_kd=0.8
        )
        
        self.website_blog = Website.objects.create(
            name="Blog Marketing",
            url="https://blog.test.com",
            brand=self.brand_blog,
            domain_authority=45,
            max_competitor_backlinks=10000,
            max_competitor_kd=0.5
        )
        
        self.website_corporate = Website.objects.create(
            name="Site Corporate",
            url="https://corporate.test.com",
            brand=self.brand_corporate,
            domain_authority=60,
            max_competitor_backlinks=25000,
            max_competitor_kd=0.6
        )
        
        # Setup avancé uniquement
        self._setup_pages_content()
        self._setup_seo_data()
        self._setup_layout_data()
        self._setup_categorization_data()
        self._setup_keywords_data()
    
    def _setup_pages_content(self):
        """Setup pages content pour tests avancés"""
        if not HAS_PAGES_CONTENT:
            return
        
        # Pages minimales pour les tests avancés
        self.page_home_ecom = Page.objects.create(
            title="Accueil E-commerce",
            url_path="/",
            website=self.website_ecommerce,
            page_type="vitrine",
            search_intent="MOFU",
            meta_description="Page d'accueil e-commerce"
        )
        
        self.page_produit1_ecom = Page.objects.create(
            title="Produit Premium",
            url_path="/produit/premium",
            website=self.website_ecommerce,
            page_type="produit",
            search_intent="BOFU"
        )
        
        self.page_home_blog = Page.objects.create(
            title="Accueil Blog",
            url_path="/",
            website=self.website_blog,
            page_type="vitrine",
            search_intent="TOFU",
            meta_description="Blog marketing"
        )
        
        self.page_article1_blog = Page.objects.create(
            title="Article Marketing",
            url_path="/article/marketing",
            website=self.website_blog,
            page_type="blog",
            search_intent="TOFU"
        )
        
        self.page_home_corporate = Page.objects.create(
            title="Accueil Corporate",
            url_path="/",
            website=self.website_corporate,
            page_type="vitrine",
            search_intent="MOFU"
        )
    
    def _setup_seo_data(self):
        """Setup SEO data avec bons related_names"""
        if not (HAS_SEO and HAS_PAGES_CONTENT):
            return
        
        # 🔥 Site e-commerce : configs SEO avec featured images
        PageSEO.objects.create(
            page=self.page_home_ecom,
            featured_image="https://example.com/home.jpg",
            sitemap_priority=1.0,
            sitemap_changefreq='weekly',
            exclude_from_sitemap=False
        )
        PageSEO.objects.create(
            page=self.page_produit1_ecom,
            featured_image="https://example.com/product1.jpg",
            sitemap_priority=0.8,
            sitemap_changefreq='monthly',
            exclude_from_sitemap=False
        )
        
        # 🔥 Site blog : configs SEO avec featured images
        PageSEO.objects.create(
            page=self.page_home_blog,
            featured_image="https://example.com/blog.jpg",
            sitemap_priority=0.9,
            sitemap_changefreq='daily',
            exclude_from_sitemap=False
        )
        PageSEO.objects.create(
            page=self.page_article1_blog,
            featured_image="https://example.com/article1.jpg",
            sitemap_priority=0.6,
            sitemap_changefreq='weekly',
            exclude_from_sitemap=False
        )
        
        # 🔥 Site corporate : config SEO sans featured image
        PageSEO.objects.create(
            page=self.page_home_corporate,
            sitemap_priority=0.8,
            sitemap_changefreq='monthly',
            exclude_from_sitemap=False
        )
    
    def _setup_layout_data(self):
        """Setup layout data avec bons related_names"""
        if not (HAS_LAYOUT and HAS_PAGES_CONTENT):
            return
        
        # 🔥 Site e-commerce : page builder
        PageLayout.objects.create(
            page=self.page_home_ecom,
            render_strategy='sections',
            layout_data={'template': 'hero_with_products'}
        )
        PageLayout.objects.create(
            page=self.page_produit1_ecom,
            render_strategy='sections',
            layout_data={'template': 'product_detail'}
        )
        
        # Sections
        PageSection.objects.create(
            page=self.page_home_ecom,
            section_type='hero_banner',
            data={'title': 'E-commerce Hero'},
            order=1,
            created_by=self.user
        )
        PageSection.objects.create(
            page=self.page_home_ecom,
            section_type='features_grid',
            data={'features': []},
            order=2,
            created_by=self.user
        )
        
        # 🔥 Site blog : page builder
        PageLayout.objects.create(
            page=self.page_home_blog,
            render_strategy='sections',
            layout_data={'template': 'blog_home'}
        )
        
        PageSection.objects.create(
            page=self.page_home_blog,
            section_type='hero_banner',
            data={'title': 'Blog Marketing'},
            order=1,
            created_by=self.user
        )
    
    def _setup_categorization_data(self):
        """Setup categorization data"""
        if not HAS_CATEGORIZATION:
            return
        
        # Catégories avec ranges cohérents
        self.category_ecommerce = WebsiteCategory.objects.create(
            name="E-commerce",
            typical_da_range_min=40,
            typical_da_range_max=80,  # Website = 75, donc dans la norme
            typical_pages_count=20
        )
        self.category_blog = WebsiteCategory.objects.create(
            name="Blog",
            typical_da_range_min=20,
            typical_da_range_max=60,  # Website = 45, donc dans la norme
            typical_pages_count=10
        )
        self.category_corporate = WebsiteCategory.objects.create(
            name="Corporate",
            typical_da_range_min=50,
            typical_da_range_max=90,  # Website = 60, donc dans la norme
            typical_pages_count=5
        )
        
        # Catégorisation des 3 websites
        WebsiteCategorization.objects.create(
            website=self.website_ecommerce,
            category=self.category_ecommerce,
            is_primary=True,
            source='manual',
            categorized_by=self.user
        )
        WebsiteCategorization.objects.create(
            website=self.website_blog,
            category=self.category_blog,
            is_primary=True,
            source='automatic',
            categorized_by=self.user
        )
        WebsiteCategorization.objects.create(
            website=self.website_corporate,
            category=self.category_corporate,
            is_primary=True,
            source='ai_suggested',
            categorized_by=self.user
        )
    
    def _setup_keywords_data(self):
        """Setup keywords minimal pour tests avancés"""
        if not (HAS_KEYWORDS and HAS_PAGES_CONTENT):
            return
        
        # Keywords minimaux
        self.keyword_ecom = Keyword.objects.create(
            keyword="e-commerce premium",
            volume=5000
        )
        self.keyword_marketing = Keyword.objects.create(
            keyword="marketing digital",
            volume=8000
        )
        
        # Associations minimales
        PageKeyword.objects.create(
            page=self.page_home_ecom,
            keyword=self.keyword_ecom,
            keyword_type='primary',
            is_ai_selected=True
        )
        PageKeyword.objects.create(
            page=self.page_home_blog,
            keyword=self.keyword_marketing,
            keyword_type='primary',
            is_ai_selected=True
        )
    
    # ===== TESTS SEO =====
    
    @pytest.mark.skipif(not (HAS_SEO and HAS_PAGES_CONTENT), reason="SEO app not available")
    def test_filter_has_featured_images(self):
        """Test filtre images featured avec bon related_name"""
        filter_set = WebsiteFilter({'has_featured_images': True})
        results = list(filter_set.qs)
        
        # Site ecommerce : 2 pages avec images
        # Site blog : 2 pages avec images  
        # Site corporate : 0 pages avec images
        self.assertEqual(len(results), 2)  # ecommerce + blog
    
    @pytest.mark.skipif(not (HAS_SEO and HAS_PAGES_CONTENT), reason="SEO app not available")
    def test_filter_has_seo_config(self):
        """Test filtre config SEO"""
        filter_set = WebsiteFilter({'has_seo_config': True})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 3)  # Tous ont des configs SEO
    
    @pytest.mark.skipif(not (HAS_SEO and HAS_PAGES_CONTENT), reason="SEO app not available")
    def test_filter_avg_sitemap_priority(self):
        """Test priorité sitemap moyenne"""
        # Site e-commerce : (1.0 + 0.8) / 2 = 0.9
        # Site blog : (0.9 + 0.6) / 2 = 0.75  
        # Site corporate : 0.8
        filter_set = WebsiteFilter({'avg_sitemap_priority_min': 0.8})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 2)  # ecommerce + corporate
    
    @pytest.mark.skipif(not (HAS_SEO and HAS_PAGES_CONTENT), reason="SEO app not available")
    def test_filter_excluded_from_sitemap_count(self):
        """Test pages exclues du sitemap"""
        filter_set = WebsiteFilter({'excluded_from_sitemap_count_min': 1})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 0)  # Aucune page exclue dans ce setup
    
    # ===== TESTS LAYOUT =====
    
    @pytest.mark.skipif(not (HAS_LAYOUT and HAS_PAGES_CONTENT), reason="Layout app not available")
    def test_filter_has_page_builder(self):
        """Test filtre page builder avec bon related_name"""
        filter_set = WebsiteFilter({'has_page_builder': True})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 2)  # ecommerce + blog
    
    @pytest.mark.skipif(not (HAS_LAYOUT and HAS_PAGES_CONTENT), reason="Layout app not available")
    def test_filter_sections_count(self):
        """Test nombre de sections"""
        # Site e-commerce : 2 sections
        filter_set = WebsiteFilter({'sections_count_min': 2})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_ecommerce)
    
    @pytest.mark.skipif(not (HAS_LAYOUT and HAS_PAGES_CONTENT), reason="Layout app not available")
    def test_filter_layout_coverage(self):
        """Test couverture layout"""
        # Site e-commerce : 2/2 = 1.0
        # Site blog : 1/2 = 0.5
        filter_set = WebsiteFilter({'layout_coverage_min': 0.8})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_ecommerce)
    
    @pytest.mark.skipif(not (HAS_LAYOUT and HAS_PAGES_CONTENT), reason="Layout app not available")
    def test_filter_popular_section_types(self):
        """Test types de sections populaires"""
        filter_set = WebsiteFilter({'popular_section_types': 'hero_banner'})
        results = list(filter_set.qs)
        # Ecommerce : 1 hero_banner, Blog : 1 hero_banner
        self.assertEqual(len(results), 2)  # ecommerce + blog
    
    @pytest.mark.skipif(not (HAS_LAYOUT and HAS_PAGES_CONTENT), reason="Layout app not available")
    def test_filter_render_strategy(self):
        """Test stratégie de rendu"""
        filter_set = WebsiteFilter({'render_strategy': 'sections'})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 2)  # ecommerce + blog
    
    # ===== TESTS CATEGORIZATION =====
    
    @pytest.mark.skipif(not HAS_CATEGORIZATION, reason="Categorization app not available")
    def test_filter_has_primary_category(self):
        """Test filtre catégorie principale"""
        filter_set = WebsiteFilter({'has_primary_category': True})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 3)  # Tous ont une catégorie principale
    
    @pytest.mark.skipif(not HAS_CATEGORIZATION, reason="Categorization app not available")
    def test_filter_categorization_source(self):
        """Test source de catégorisation"""
        filter_set = WebsiteFilter({'categorization_source': 'manual'})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_ecommerce)
        
        filter_set = WebsiteFilter({'categorization_source': 'automatic'})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_blog)
    
    @pytest.mark.skipif(not HAS_CATEGORIZATION, reason="Categorization app not available")
    def test_filter_da_above_category(self):
        """Test DA supérieur à la catégorie"""
        # Tous les sites sont dans la norme, donc aucun au-dessus
        filter_set = WebsiteFilter({'da_above_category': True})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 0)
    
    @pytest.mark.skipif(not (HAS_CATEGORIZATION and HAS_PAGES_CONTENT), reason="Apps not available")
    def test_filter_pages_above_category(self):
        """Test pages supérieures à la catégorie"""
        filter_set = WebsiteFilter({'pages_above_category': True})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 0)  # Aucun site ne dépasse sa catégorie
    
    @pytest.mark.skipif(not HAS_CATEGORIZATION, reason="Categorization app not available")
    def test_filter_performance_vs_category(self):
        """Test performance vs catégorie"""
        filter_set = WebsiteFilter({'performance_vs_category': 'typical'})
        results = list(filter_set.qs)
        # Tous les sites sont dans la norme de leur catégorie
        self.assertEqual(len(results), 3)
    
    # ===== TESTS COMBINÉS AVANCÉS =====
    
    @pytest.mark.skipif(not (HAS_KEYWORDS and HAS_SEO and HAS_PAGES_CONTENT), reason="Apps not available")
    def test_filter_combined_keywords_seo(self):
        """Test filtres combinés keywords + SEO avec bons related_names"""
        filter_set = WebsiteFilter({
            'has_keywords': True,
            'has_primary_keywords': True,
            'has_featured_images': True,
            'avg_sitemap_priority_min': 0.7
        })
        results = list(filter_set.qs)
        self.assertEqual(len(results), 2)  # ecommerce + blog
    
    @pytest.mark.skipif(not (HAS_LAYOUT and HAS_CATEGORIZATION), reason="Apps not available")
    def test_filter_combined_layout_category(self):
        """Test filtres combinés layout + catégorie avec bons related_names"""
        filter_set = WebsiteFilter({
            'has_page_builder': True,
            'has_primary_category': True,
            'categorization_source': 'manual'
        })
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_ecommerce)
    
    def test_filter_combined_brand_basics(self):
        """Test filtres combinés brand + bases"""
        filter_set = WebsiteFilter({
            'has_chatgpt_key': True,
            'domain_authority_min': 70,
            'name': 'E-commerce'
        })
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_ecommerce)
    
    # ===== TESTS EDGE CASES =====
    
    def test_filter_no_results(self):
        """Test filtres sans résultats"""
        filter_set = WebsiteFilter({
            'domain_authority_min': 100,
            'name': 'inexistant'
        })
        results = list(filter_set.qs)
        self.assertEqual(len(results), 0)
    
    @pytest.mark.skipif(not HAS_PAGES_CONTENT, reason="Pages content app not available")
    def test_filter_pages_count_zero(self):
        """Test sites sans pages"""
        # Créer un site sans pages
        brand_empty = Brand.objects.create(
            name="Brand Empty",
            company=self.company,
            brand_admin=self.user
        )
        website_empty = Website.objects.create(
            name="Site Vide",
            url="https://empty.test.com",
            brand=brand_empty,
            domain_authority=30
        )
        
        filter_set = WebsiteFilter({'pages_count_max': 0})
        results = list(filter_set.qs)
        self.assertIn(website_empty, results)