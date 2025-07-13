# backend/seo_websites_core/tests/test_website_filters.py

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

# 🔥 FIX: Nom d'app correct
try:
    from seo_websites_categorization.models import WebsiteCategory, WebsiteCategorization
    HAS_CATEGORIZATION = True
except ImportError:
    HAS_CATEGORIZATION = False

User = get_user_model()


class WebsiteFilterTestCase(TestCase):
    """Tests complets pour WebsiteFilter cross-app avec relation 1:1 Brand-Website"""
    
    def setUp(self):
        """Setup data pour tests - 1 Brand = 1 Website"""
        # Setup identique à ton original...
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
        
        # Setup cross-app data conditionnel
        self._setup_pages_content()
        self._setup_workflow_data()
        self._setup_keywords_data()
        self._setup_seo_data()
        self._setup_layout_data()
        self._setup_categorization_data()

    # Ton _setup_pages_content() reste identique...
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

    def _setup_seo_data(self):
        """Setup SEO si app disponible"""
        if not (HAS_SEO and HAS_PAGES_CONTENT):
            return
        
        # 🔥 Site e-commerce : 4 configs SEO avec featured images
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
        PageSEO.objects.create(
            page=self.page_produit2_ecom,
            featured_image="https://example.com/product2.jpg",  # 🔥 AJOUT
            sitemap_priority=0.7,
            sitemap_changefreq='monthly',
            exclude_from_sitemap=False
        )
        PageSEO.objects.create(
            page=self.page_contact_ecom,
            sitemap_priority=0.3,
            sitemap_changefreq='yearly',
            exclude_from_sitemap=True
        )
        
        # 🔥 Site blog : 2 configs SEO avec featured images
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
        
        # 🔥 Site corporate : 1 config SEO sans featured image
        PageSEO.objects.create(
            page=self.page_home_corporate,
            sitemap_priority=0.8,
            sitemap_changefreq='monthly',
            exclude_from_sitemap=False
        )

    def _setup_layout_data(self):
        """Setup layout si app disponible"""
        if not (HAS_LAYOUT and HAS_PAGES_CONTENT):
            return
        
        # 🔥 Site e-commerce : page builder sur 3 pages
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
        PageLayout.objects.create(
            page=self.page_blog_ecom,
            render_strategy='markdown',
            layout_data={'template': 'blog_post'}
        )
        
        # 🔥 Sections avec types validés
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
        PageSection.objects.create(
            page=self.page_produit1_ecom,
            section_type='hero_banner',
            data={'product_info': 'Premium'},
            order=1,
            created_by=self.user
        )
        PageSection.objects.create(
            page=self.page_produit1_ecom,
            section_type='cta_banner',
            data={'cta_text': 'Acheter maintenant'},
            order=2,
            created_by=self.user
        )
        
        # 🔥 Site blog : 1 page avec layout
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
        """Setup categorization si app disponible"""
        if not HAS_CATEGORIZATION:
            return
        
        # 🔥 Catégories avec des ranges cohérents avec tes websites
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
        
        # 🔥 Catégorisation des 3 websites
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

    # ===== TOUS TES TESTS DE BASE RESTENT IDENTIQUES =====
    
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

    def test_filter_name(self):
        """Test filtre par nom"""
        filter_set = WebsiteFilter({'name': 'E-commerce'})
        results = list(filter_set.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_ecommerce)

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

    # ===== TESTS CROSS-APP CORRIGÉS =====

    @pytest.mark.skipif(not (HAS_SEO and HAS_PAGES_CONTENT), reason="SEO app not available")
    def test_filter_has_featured_images(self):
        """Test filtre images featured"""
        filter_set = WebsiteFilter({'has_featured_images': True})
        results = list(filter_set.qs)
        
        # Debug pour voir ce qui se passe
        print(f"\n=== DEBUG featured images ===")
        for website in Website.objects.all():
            pages_with_images = website.pages.filter(
                page_seo__featured_image__isnull=False
            ).exclude(page_seo__featured_image='').count()
            print(f"{website.name}: {pages_with_images} pages avec images")
        
        # Site ecommerce : 3 pages avec images (home, produit1, produit2)
        # Site blog : 2 pages avec images (home, article1)
        # Site corporate : 0 pages avec images
        self.assertEqual(len(results), 2)  # ecommerce + blog

    @pytest.mark.skipif(not HAS_CATEGORIZATION, reason="Categorization app not available")
    def test_filter_has_primary_category(self):
        """Test filtre catégorie principale"""
        filter_set = WebsiteFilter({'has_primary_category': True})
        results = list(filter_set.qs)
        
        # Debug
        print(f"\n=== DEBUG primary category ===")
        for website in Website.objects.all():
            has_primary = WebsiteCategorization.objects.filter(
                website=website, 
                is_primary=True
            ).exists()
            print(f"{website.name}: has_primary = {has_primary}")
        
        self.assertEqual(len(results), 3)  # Tous ont une catégorie principale

    @pytest.mark.skipif(not HAS_CATEGORIZATION, reason="Categorization app not available")
    def test_filter_categorization_source(self):
        """Test source de catégorisation"""
        filter_set = WebsiteFilter({'categorization_source': 'manual'})
        results = list(filter_set.qs)
        
        # Debug
        print(f"\n=== DEBUG categorization source ===")
        for website in Website.objects.all():
            categorizations = WebsiteCategorization.objects.filter(website=website)
            for cat in categorizations:
                print(f"{website.name}: source = {cat.source}")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_ecommerce)

    @pytest.mark.skipif(not HAS_CATEGORIZATION, reason="Categorization app not available")
    def test_filter_performance_vs_category(self):
        """Test performance vs catégorie"""
        filter_set = WebsiteFilter({'performance_vs_category': 'typical'})
        results = list(filter_set.qs)
        
        # Debug
        print(f"\n=== DEBUG performance vs category ===")
        for website in Website.objects.all():
            try:
                categorization = WebsiteCategorization.objects.get(
                    website=website, 
                    is_primary=True
                )
                da_in_range = (categorization.category.typical_da_range_min <= 
                              website.domain_authority <= 
                              categorization.category.typical_da_range_max)
                print(f"{website.name}: DA {website.domain_authority} in range [{categorization.category.typical_da_range_min}-{categorization.category.typical_da_range_max}] = {da_in_range}")
            except WebsiteCategorization.DoesNotExist:
                print(f"{website.name}: No primary categorization")
        
        # Tous les sites sont dans la norme de leur catégorie
        self.assertGreaterEqual(len(results), 3)

    @pytest.mark.skipif(not (HAS_LAYOUT and HAS_PAGES_CONTENT), reason="Layout app not available")
    def test_filter_popular_section_types(self):
        """Test types de sections populaires"""
        # 🔥 Test avec UN SEUL type pour éviter la confusion
        filter_set = WebsiteFilter({'popular_section_types': 'hero_banner'})
        results = list(filter_set.qs)
        
        # Debug
        print(f"\n=== DEBUG section types ===")
        for website in Website.objects.all():
            hero_count = PageSection.objects.filter(
                page__website=website,
                section_type='hero_banner'
            ).count()
            print(f"{website.name}: {hero_count} hero_banner sections")
        
        # Ecommerce : 2 hero_banner, Blog : 1 hero_banner
        self.assertEqual(len(results), 2)  # ecommerce + blog

    # ===== TESTS COMBINÉS CORRIGÉS =====

    @pytest.mark.skipif(not (HAS_KEYWORDS and HAS_SEO and HAS_PAGES_CONTENT), reason="Apps not available")
    def test_filter_combined_keywords_seo(self):
        """Test filtres combinés keywords + SEO"""
        filter_set = WebsiteFilter({
            'has_keywords': True,
            'has_primary_keywords': True,
            'has_featured_images': True,
            'avg_sitemap_priority_min': 0.7
        })
        results = list(filter_set.qs)
        
        # Debug chaque condition
        print(f"\n=== DEBUG combined keywords+seo ===")
        for website in Website.objects.all():
            has_kw = website.pages.filter(page_keywords__isnull=False).exists()
            has_primary = website.pages.filter(
                page_keywords__keyword_type='primary'
            ).exists()
            has_images = website.pages.filter(
                page_seo__featured_image__isnull=False
            ).exclude(page_seo__featured_image='').exists()
            
            # Calcul avg sitemap priority
            from django.db.models import Avg
            avg_priority = website.pages.filter(
                page_seo__isnull=False
            ).aggregate(
                avg_priority=Avg('page_seo__sitemap_priority')
            )['avg_priority'] or 0
            
            print(f"{website.name}: has_kw={has_kw}, has_primary={has_primary}, has_images={has_images}, avg_priority={avg_priority:.2f}")
        
        self.assertEqual(len(results), 2)  # ecommerce + blog

    @pytest.mark.skipif(not (HAS_LAYOUT and HAS_CATEGORIZATION), reason="Apps not available")
    def test_filter_combined_layout_category(self):
        """Test filtres combinés layout + catégorie"""
        filter_set = WebsiteFilter({
            'has_page_builder': True,
            'has_primary_category': True,
            'categorization_source': 'manual'
        })
        results = list(filter_set.qs)
        
        # Debug
        print(f"\n=== DEBUG combined layout+category ===")
        for website in Website.objects.all():
            has_builder = website.pages.filter(page_layout__isnull=False).exists()
            has_primary_cat = WebsiteCategorization.objects.filter(
                website=website, 
                is_primary=True
            ).exists()
            is_manual = WebsiteCategorization.objects.filter(
                website=website,
                source='manual'
            ).exists()
            print(f"{website.name}: has_builder={has_builder}, has_primary_cat={has_primary_cat}, is_manual={is_manual}")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.website_ecommerce)

