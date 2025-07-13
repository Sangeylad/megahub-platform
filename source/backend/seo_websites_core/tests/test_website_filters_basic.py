# backend/seo_websites_core/tests/test_website_filters_basic.py

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
    from seo_pages_workflow.models import PageStatus
    HAS_WORKFLOW = True
except ImportError:
    HAS_WORKFLOW = False

try:
    from seo_pages_keywords.models import PageKeyword
    from seo_keywords_base.models import Keyword
    HAS_KEYWORDS = True
except ImportError:
    HAS_KEYWORDS = False

User = get_user_model()


class WebsiteFilterBasicTestCase(TestCase):
    """Tests de base pour WebsiteFilter - Relation 1:1 Brand-Website"""
    
    def setUp(self):
        """Setup data pour tests - 1 Brand = 1 Website"""
        # 1. Admin de la company
        self.admin_user = User.objects.create_user(
            username="admin_user",
            email="admin@example.com", 
            password="adminpass123"
        )
        
        # 2. Company avec admin
        self.company = Company.objects.create(
            name="Test Company", 
            slots=10,
            admin=self.admin_user
        )
        
        # 3. Assigner company à admin
        self.admin_user.company = self.company
        self.admin_user.save()
        
        # 4. User normal
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            company=self.company
        )
        
        # 🔥 BRANDS & WEBSITES - 1:1 RELATIONSHIP
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
        
        # 🔥 3 WEBSITES pour 3 BRANDS (OneToOneField)
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
        
        # Setup cross-app data minimal
        self._setup_pages_content()
        self._setup_workflow_data()
        self._setup_keywords_data()
    
    def _setup_pages_content(self):
        """Setup pages content si app disponible"""
        if not HAS_PAGES_CONTENT:
            return
        
        # 🔥 Site e-commerce (5 pages)
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
        
        self.page_produit2_ecom = Page.objects.create(
            title="Produit Standard",
            url_path="/produit/standard",
            website=self.website_ecommerce,
            page_type="produit",
            search_intent="BOFU",
            meta_description="Produit standard"
        )
        
        self.page_blog_ecom = Page.objects.create(
            title="Article Blog E-commerce",
            url_path="/blog/article-ecom",
            website=self.website_ecommerce,
            page_type="blog",
            search_intent="TOFU"
        )
        
        self.page_contact_ecom = Page.objects.create(
            title="Contact E-commerce",
            url_path="/contact",
            website=self.website_ecommerce,
            page_type="autre",
            search_intent="MOFU",
            meta_description="Contactez-nous"
        )
        
        # 🔥 Site blog (3 pages)
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
        
        self.page_article2_blog = Page.objects.create(
            title="Guide SEO",
            url_path="/article/guide-seo",
            website=self.website_blog,
            page_type="blog",
            search_intent="TOFU",
            meta_description="Guide complet SEO"
        )
        
        # 🔥 Site corporate (2 pages)
        self.page_home_corporate = Page.objects.create(
            title="Accueil Corporate",
            url_path="/",
            website=self.website_corporate,
            page_type="vitrine",
            search_intent="MOFU"
        )
        
        self.page_about_corporate = Page.objects.create(
            title="À Propos",
            url_path="/about",
            website=self.website_corporate,
            page_type="autre",
            search_intent="MOFU",
            meta_description="Notre entreprise"
        )
    
    def _setup_workflow_data(self):
        """Setup workflow si app disponible"""
        if not (HAS_WORKFLOW and HAS_PAGES_CONTENT):
            return
        
        # 🔥 Site e-commerce : 3 published, 1 draft, 1 scheduled
        PageStatus.objects.create(
            page=self.page_home_ecom,
            status='published',
            status_changed_by=self.user
        )
        PageStatus.objects.create(
            page=self.page_produit1_ecom,
            status='published',
            status_changed_by=self.user
        )
        PageStatus.objects.create(
            page=self.page_produit2_ecom,
            status='published',
            status_changed_by=self.user
        )
        PageStatus.objects.create(
            page=self.page_blog_ecom,
            status='draft',
            status_changed_by=self.user
        )
        PageStatus.objects.create(
            page=self.page_contact_ecom,
            status='scheduled',
            status_changed_by=self.user
        )
        
        # 🔥 Site blog : 2 published, 1 draft
        PageStatus.objects.create(
            page=self.page_home_blog,
            status='published',
            status_changed_by=self.user
        )
        PageStatus.objects.create(
            page=self.page_article1_blog,
            status='published',
            status_changed_by=self.user
        )
        PageStatus.objects.create(
            page=self.page_article2_blog,
            status='draft',
            status_changed_by=self.user
        )
        
        # 🔥 Site corporate : 1 published, 1 draft
        PageStatus.objects.create(
            page=self.page_home_corporate,
            status='published',
            status_changed_by=self.user
        )
        PageStatus.objects.create(
            page=self.page_about_corporate,
            status='draft',
            status_changed_by=self.user
        )
    
    def _setup_keywords_data(self):
        """Setup keywords si app disponible"""
        if not (HAS_KEYWORDS and HAS_PAGES_CONTENT):
            return
        
        # Créer des keywords
        self.keyword_ecom = Keyword.objects.create(
            keyword="e-commerce premium",
            volume=5000
        )
        self.keyword_marketing = Keyword.objects.create(
            keyword="marketing digital",
            volume=8000
        )
        self.keyword_seo = Keyword.objects.create(
            keyword="seo technique",
            volume=3000
        )
        self.keyword_corporate = Keyword.objects.create(
            keyword="entreprise b2b",
            volume=2000
        )
        
        # 🔥 Site e-commerce : 5 mots-clés (3 AI, 2 manuels)
        PageKeyword.objects.create(
            page=self.page_home_ecom,
            keyword=self.keyword_ecom,
            keyword_type='primary',
            is_ai_selected=True
        )
        PageKeyword.objects.create(
            page=self.page_produit1_ecom,
            keyword=self.keyword_ecom,
            keyword_type='secondary',
            is_ai_selected=True
        )
        PageKeyword.objects.create(
            page=self.page_produit2_ecom,
            keyword=self.keyword_marketing,
            keyword_type='primary',
            is_ai_selected=False
        )
        PageKeyword.objects.create(
            page=self.page_blog_ecom,
            keyword=self.keyword_seo,
            keyword_type='secondary',
            is_ai_selected=True
        )
        PageKeyword.objects.create(
            page=self.page_contact_ecom,
            keyword=self.keyword_corporate,
            keyword_type='anchor',
            is_ai_selected=False
        )
        
        # 🔥 Site blog : 2 mots-clés (AI)
        PageKeyword.objects.create(
            page=self.page_home_blog,
            keyword=self.keyword_marketing,
            keyword_type='primary',
            is_ai_selected=True
        )
        PageKeyword.objects.create(
            page=self.page_article1_blog,
            keyword=self.keyword_seo,
            keyword_type='primary',
            is_ai_selected=True
        )
        
        # 🔥 Site corporate : 1 mot-clé (manuel)
        PageKeyword.objects.create(
            page=self.page_home_corporate,
            keyword=self.keyword_corporate,
            keyword_type='primary',
            is_ai_selected=False
        )
    
    # ===== TESTS RELATION 1:1 =====
    
    def test_one_to_one_relationship(self):
        """Test relation 1:1 Brand-Website"""
        # Vérifier que chaque brand a exactement 1 website
        self.assertEqual(self.brand_ecommerce.seo_website, self.website_ecommerce)
        self.assertEqual(self.brand_blog.seo_website, self.website_blog)
        self.assertEqual(self.brand_corporate.seo_website, self.website_corporate)
        
        # Vérifier que chaque website a exactement 1 brand
        self.assertEqual(self.website_ecommerce.brand, self.brand_ecommerce)
        self.assertEqual(self.website_blog.brand, self.brand_blog)
        self.assertEqual(self.website_corporate.brand, self.brand_corporate)
    
    def test_cannot_create_duplicate_website_for_brand(self):
        """Test qu'on ne peut pas créer 2 sites pour 1 brand"""
        from django.db import IntegrityError
        
        with self.assertRaises(IntegrityError):
            Website.objects.create(
                name="Site Duplicate",
                url="https://duplicate.test.com",
                brand=self.brand_ecommerce  # Brand déjà utilisée
            )
    
    # ===== TESTS DE BASE =====
    
    def test_filter_name(self):
        """Test filtre par nom"""
        filter_set = WebsiteFilter({'name': 'E-commerce'})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_ecommerce)
    
    def test_filter_url(self):
        """Test filtre par URL"""
        filter_set = WebsiteFilter({'url': 'blog'})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_blog)
    
    def test_filter_domain_authority_range(self):
        """Test filtre par DA avec range"""
        filter_set = WebsiteFilter({
            'domain_authority_min': 50,
            'domain_authority_max': 70
        })
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_corporate)  # DA = 60
    
    def test_filter_brand_name(self):
        """Test filtre par nom de brand"""
        filter_set = WebsiteFilter({'brand_name': 'Blog'})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_blog)
    
    def test_filter_has_chatgpt_key(self):
        """Test filtre clé ChatGPT"""
        filter_set = WebsiteFilter({'has_chatgpt_key': True})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 2)  # ecommerce + corporate
        
        filter_set = WebsiteFilter({'has_chatgpt_key': False})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)  # blog
        self.assertEqual(results[0], self.website_blog)
    
    def test_filter_has_gemini_key(self):
        """Test filtre clé Gemini"""
        filter_set = WebsiteFilter({'has_gemini_key': True})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 2)  # blog + corporate
    
    def test_filter_search_global(self):
        """Test recherche globale"""
        filter_set = WebsiteFilter({'search': 'Marketing'})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_blog)
    
    # ===== TESTS PAGES CONTENT =====
    
    @pytest.mark.skipif(not HAS_PAGES_CONTENT, reason="Pages content app not available")
    def test_filter_pages_count_exact(self):
        """Test filtre nombre de pages exact"""
        # Site e-commerce = 5 pages
        filter_set = WebsiteFilter({'pages_count_min': 5, 'pages_count_max': 5})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_ecommerce)
    
    @pytest.mark.skipif(not HAS_PAGES_CONTENT, reason="Pages content app not available")
    def test_filter_pages_count_range(self):
        """Test filtre nombre de pages avec range"""
        # Sites avec 3+ pages (ecommerce=5, blog=3)
        filter_set = WebsiteFilter({'pages_count_min': 3})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 2)
        
        # Sites avec exactement 2 pages (corporate)
        filter_set = WebsiteFilter({'pages_count_min': 2, 'pages_count_max': 2})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_corporate)
    
    @pytest.mark.skipif(not HAS_PAGES_CONTENT, reason="Pages content app not available")
    def test_filter_has_pages(self):
        """Test filtre présence de pages"""
        filter_set = WebsiteFilter({'has_pages': True})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 3)  # Tous les sites ont des pages
    
    @pytest.mark.skipif(not HAS_PAGES_CONTENT, reason="Pages content app not available")
    def test_filter_page_types(self):
        """Test filtre types de pages"""
        # Sites avec pages produit (seul ecommerce)
        filter_set = WebsiteFilter({'page_types': 'produit'})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_ecommerce)
        
        # Sites avec pages blog (ecommerce + blog)
        filter_set = WebsiteFilter({'page_types': 'blog'})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 2)
    
    @pytest.mark.skipif(not HAS_PAGES_CONTENT, reason="Pages content app not available")
    def test_filter_has_product_pages(self):
        """Test filtre pages produit"""
        filter_set = WebsiteFilter({'has_product_pages': True})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_ecommerce)
    
    @pytest.mark.skipif(not HAS_PAGES_CONTENT, reason="Pages content app not available")
    def test_filter_meta_description_coverage(self):
        """Test couverture meta description"""
        # Site e-commerce : 3/5 = 0.6
        # Site blog : 2/3 = 0.67
        # Site corporate : 1/2 = 0.5
        filter_set = WebsiteFilter({'meta_description_coverage_min': 0.55})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 2)  # ecommerce + blog
    
    # ===== TESTS WORKFLOW =====
    
    @pytest.mark.skipif(not (HAS_WORKFLOW and HAS_PAGES_CONTENT), reason="Workflow app not available")
    def test_filter_has_published_pages(self):
        """Test filtre pages publiées"""
        filter_set = WebsiteFilter({'has_published_pages': True})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 3)  # Tous les sites ont des pages publiées
    
    @pytest.mark.skipif(not (HAS_WORKFLOW and HAS_PAGES_CONTENT), reason="Workflow app not available")
    def test_filter_published_pages_count(self):
        """Test nombre de pages publiées"""
        # Sites avec 3+ pages publiées (seul ecommerce)
        filter_set = WebsiteFilter({'published_pages_count_min': 3})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_ecommerce)  # 3 pages publiées
    
    @pytest.mark.skipif(not (HAS_WORKFLOW and HAS_PAGES_CONTENT), reason="Workflow app not available")
    def test_filter_publication_ratio(self):
        """Test ratio de publication"""
        # Site e-commerce : 3/5 = 0.6
        # Site blog : 2/3 = 0.67
        # Site corporate : 1/2 = 0.5
        filter_set = WebsiteFilter({'publication_ratio_min': 0.65})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_blog)  # Ratio le plus élevé
    
    # ===== TESTS KEYWORDS =====
    
    @pytest.mark.skipif(not (HAS_KEYWORDS and HAS_PAGES_CONTENT), reason="Keywords app not available")
    def test_filter_has_keywords(self):
        """Test filtre présence de mots-clés"""
        filter_set = WebsiteFilter({'has_keywords': True})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 3)  # Tous les sites ont des mots-clés
    
    @pytest.mark.skipif(not (HAS_KEYWORDS and HAS_PAGES_CONTENT), reason="Keywords app not available")
    def test_filter_total_keywords_count(self):
        """Test nombre total de mots-clés"""
        # Site e-commerce : 5 mots-clés
        filter_set = WebsiteFilter({'total_keywords_count_min': 4})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_ecommerce)
        
        # Sites avec 2+ mots-clés (ecommerce=5, blog=2)
        filter_set = WebsiteFilter({'total_keywords_count_min': 2})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 2)
    
    @pytest.mark.skipif(not (HAS_KEYWORDS and HAS_PAGES_CONTENT), reason="Keywords app not available")
    def test_filter_ai_keywords_ratio(self):
        """Test ratio mots-clés IA"""
        # Site e-commerce : 3/5 = 0.6
        # Site blog : 2/2 = 1.0
        # Site corporate : 0/1 = 0.0
        filter_set = WebsiteFilter({'ai_keywords_ratio_min': 0.9})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_blog)
    
    @pytest.mark.skipif(not (HAS_KEYWORDS and HAS_PAGES_CONTENT), reason="Keywords app not available")
    def test_filter_has_primary_keywords(self):
        """Test filtre mots-clés primaires"""
        filter_set = WebsiteFilter({'has_primary_keywords': True})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 3)  # Tous ont des mots-clés primaires