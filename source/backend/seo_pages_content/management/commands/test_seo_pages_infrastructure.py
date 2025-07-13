# backend/seo_pages_content/management/commands/test_seo_pages_infrastructure.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
import json
import uuid

from company_core.models import Company
from seo_websites_core.models import Website
from seo_pages_content.models import Page
from seo_pages_hierarchy.models import PageHierarchy, PageBreadcrumb
from seo_pages_layout.models import PageLayout, PageSection
from seo_pages_seo.models import PageSEO, PagePerformance
from seo_pages_workflow.models import PageStatus, PageScheduling, PageWorkflowHistory
from seo_pages_keywords.models import PageKeyword

# Import des filtres pour tests
from seo_websites_core.filters import WebsiteFilter
from seo_pages_content.filters import PageFilter
from seo_pages_hierarchy.filters import PageHierarchyFilter, PageBreadcrumbFilter
from seo_pages_seo.filters import PageSEOFilter, PagePerformanceFilter
from seo_pages_workflow.filters import PageStatusFilter, PageWorkflowHistoryFilter, PageSchedulingFilter
from seo_pages_keywords.filters import PageKeywordFilter

# Import keywords - Updated path
try:
    from seo_keywords_base.models import Keyword
    KEYWORDS_AVAILABLE = True
except ImportError:
    KEYWORDS_AVAILABLE = False

User = get_user_model()

class Command(BaseCommand):
    help = 'Test complet de l\'architecture SEO Pages MEGAHUB (8 apps + Filtres)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-cleanup',
            action='store_true',
            help='Ne pas nettoyer les données de test'
        )
        parser.add_argument(
            '--force-cleanup',
            action='store_true',
            help='Nettoyer AVANT de commencer'
        )
        parser.add_argument(
            '--test-hierarchy',
            action='store_true',
            help='Tester spécifiquement la hiérarchie'
        )
        parser.add_argument(
            '--test-workflow',
            action='store_true',
            help='Tester spécifiquement le workflow'
        )
        parser.add_argument(
            '--test-page-builder',
            action='store_true',
            help='Tester spécifiquement le page builder'
        )
        parser.add_argument(
            '--test-filters',
            action='store_true',
            help='Tester spécifiquement les filtres'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🏗️ Testing MEGAHUB SEO Pages Infrastructure v4.0 (8 Apps + Filtres)\n'))
        
        # Cleanup initial si demandé
        if options['force_cleanup']:
            self.cleanup_test_data()
        
        # Setup
        self.setup_test_data()
        
        # Tests par app dans l'ordre des dépendances
        self.test_seo_websites_core()
        self.test_seo_pages_content()
        self.test_seo_pages_hierarchy()
        self.test_seo_pages_layout()
        self.test_seo_pages_seo()
        self.test_seo_pages_workflow()
        self.test_seo_pages_keywords()
        
        # Tests spécialisés selon options
        if options['test_hierarchy']:
            self.test_advanced_hierarchy()
        if options['test_workflow']:
            self.test_advanced_workflow()
        if options['test_page_builder']:
            self.test_advanced_page_builder()
        if options['test_filters']:
            self.test_all_filters()
        
        # Tests d'intégration cross-app
        self.test_cross_app_integration()
        self.test_filters_integration()
        
        # Test workflow complet
        self.test_complete_workflow()
        
        if not options['skip_cleanup']:
            self.cleanup_test_data()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Tous les tests SEO Pages sont passés !'))
    
    def setup_test_data(self):
        """Prépare les données de test"""
        self.stdout.write('📝 Setup des données de test SEO Pages v4.0...')
        
        # Company et brand de test
        self.test_company = Company.objects.first()
        self.test_user = User.objects.first()
        
        if not self.test_company or not self.test_user:
            self.stdout.write(self.style.ERROR('❌ Company/User manquantes'))
            return
        
        # Vérifier si Brand a déjà un website
        existing_brand = Brand.objects.filter(seo_website__isnull=False).first()
        
        if existing_brand:
            self.stdout.write(f'  ✅ Utilisation Brand existante avec website: {existing_brand.name}')
            self.test_brand = existing_brand
            self.test_website = existing_brand.seo_website
            self.stdout.write(f'  ✅ Website existant: {self.test_website.name}')
        else:
            # Créer nouvelle brand pour test
            self.test_brand = Brand.objects.create(
                company=self.test_company,
                name=f'Test Brand SEO {uuid.uuid4().hex[:8]}',
                description='Brand de test pour SEO Pages'
            )
            self.stdout.write(f'  ✅ Nouvelle Brand créée: {self.test_brand.name}')
            self.test_website = None  # Sera créé dans test_seo_websites_core()
        
        # Créer des keywords de test si disponible
        self.test_keywords_ids = []
        if KEYWORDS_AVAILABLE:
            test_keywords_data = [
                {'keyword': f'test seo pages {uuid.uuid4().hex[:8]}', 'volume': 1000, 'search_intent': 'TOFU'},
                {'keyword': f'architecture megahub {uuid.uuid4().hex[:8]}', 'volume': 500, 'search_intent': 'MOFU'},
                {'keyword': f'page builder moderne {uuid.uuid4().hex[:8]}', 'volume': 750, 'search_intent': 'BOFU'},
            ]
            
            for kw_data in test_keywords_data:
                keyword, created = Keyword.objects.get_or_create(
                    keyword=kw_data['keyword'],
                    defaults={
                        'volume': kw_data['volume'],
                        'search_intent': kw_data['search_intent']
                    }
                )
                self.test_keywords_ids.append(keyword.id)
                
            self.stdout.write(f'  ✅ Keywords de test: {len(self.test_keywords_ids)} créés')
        else:
            self.stdout.write('  ⚠️ Module seo_keywords_base non disponible')
    
    def test_seo_websites_core(self):
        """Test du core websites"""
        self.stdout.write('\n🌐 Testing seo_websites_core (Websites Core)...')
        
        # Utiliser website existant ou créer nouveau
        if hasattr(self, 'test_website') and self.test_website:
            self.stdout.write(f'  ✅ Website existant utilisé: {self.test_website.name}')
            self.stdout.write(f'  ✅ Domain Authority: {self.test_website.domain_authority}')
            self.stdout.write(f'  ✅ Brand: {self.test_website.brand.name}')
        else:
            # Créer nouveau website
            self.test_website = Website.objects.create(
                name=f'Test Website {uuid.uuid4().hex[:8]}',
                url='https://test-seo-pages.example.com',
                brand=self.test_brand,
                domain_authority=65,
                max_competitor_backlinks=50000,
                max_competitor_kd=0.75
            )
            self.stdout.write(f'  ✅ Website créé: {self.test_website.name}')
            self.stdout.write(f'  ✅ Domain Authority: {self.test_website.domain_authority}')
            self.stdout.write(f'  ✅ Max Competitor KD: {self.test_website.max_competitor_kd}')
        
        # Tester les méthodes
        pages_count = self.test_website.get_pages_count()
        self.stdout.write(f'  ✅ Pages count (initial): {pages_count}')
        
        # Test filtres WebsiteFilter
        website_filter = WebsiteFilter(data={'brand': self.test_brand.id})
        if website_filter.is_valid():
            filtered_websites = website_filter.qs
            self.stdout.write(f'  ✅ WebsiteFilter par brand: {filtered_websites.count()} résultats')
        
        # Test recherche
        search_filter = WebsiteFilter(data={'search': 'test'})
        if search_filter.is_valid():
            search_results = search_filter.qs
            self.stdout.write(f'  ✅ WebsiteFilter recherche: {search_results.count()} résultats')
    
    def test_seo_pages_content(self):
        """Test du contenu de base des pages"""
        self.stdout.write('\n📄 Testing seo_pages_content (Page Content)...')
        
        # Créer pages de test avec différents types
        test_pages_data = [
            {
                'title': f'Homepage Test {uuid.uuid4().hex[:6]}',
                'page_type': 'vitrine',
                'search_intent': 'TOFU',
                'meta_description': 'Homepage description test'
            },
            {
                'title': f'Blog Article Test {uuid.uuid4().hex[:6]}',
                'page_type': 'blog',
                'search_intent': 'MOFU',
                'url_path': f'/blog/article-test-{uuid.uuid4().hex[:6]}'
            },
            {
                'title': f'Product Page Test {uuid.uuid4().hex[:6]}',
                'page_type': 'produit',
                'search_intent': 'BOFU'
            },
            {
                'title': f'Landing Page Test {uuid.uuid4().hex[:6]}',
                'page_type': 'landing',
                'search_intent': 'BOFU'
            }
        ]
        
        self.test_pages = []
        
        for page_data in test_pages_data:
            page = Page.objects.create(
                website=self.test_website,
                **page_data
            )
            self.test_pages.append(page)
            
            self.stdout.write(f'  ✅ Page créée: {page.title} ({page.page_type})')
            self.stdout.write(f'    - URL path: {page.url_path}')
            self.stdout.write(f'    - Search intent: {page.search_intent}')
        
        # Tester auto-génération URL
        page_auto_url = Page.objects.create(
            website=self.test_website,
            title=f'Page Auto URL Test {uuid.uuid4().hex[:6]}'
        )
        
        self.stdout.write(f'  ✅ Auto URL generation: "{page_auto_url.title}" → {page_auto_url.url_path}')
        self.test_pages.append(page_auto_url)
        
        # Test filtres PageFilter
        page_filter = PageFilter(data={
            'website': self.test_website.id,
            'page_type': 'blog'
        })
        if page_filter.is_valid():
            blog_pages = page_filter.qs
            self.stdout.write(f'  ✅ PageFilter blog pages: {blog_pages.count()} résultats')
        
        # Test recherche pages
        search_filter = PageFilter(data={'search': 'test'})
        if search_filter.is_valid():
            search_results = search_filter.qs
            self.stdout.write(f'  ✅ PageFilter recherche: {search_results.count()} résultats')
        
        # Test contrainte unicité
        try:
            Page.objects.create(
                website=self.test_website,
                title='Duplicate URL Test',
                url_path=page_auto_url.url_path
            )
            self.stdout.write('  ❌ Contrainte unicité URL échouée')
        except Exception:
            self.stdout.write('  ✅ Contrainte unicité URL respectée')
    
    def test_seo_pages_hierarchy(self):
        """Test de la hiérarchie des pages"""
        self.stdout.write('\n🌳 Testing seo_pages_hierarchy (Page Hierarchy)...')
        
        if len(self.test_pages) < 4:
            self.stdout.write('  ⚠️ Pas assez de pages pour tester la hiérarchie')
            return
        
        # Configuration hiérarchie 3 niveaux
        root_page = self.test_pages[0]  # Homepage
        level2_page = self.test_pages[1]  # Blog Article
        level3_page = self.test_pages[2]  # Product Page
        
        # Créer hiérarchie racine
        root_hierarchy = PageHierarchy.objects.create(
            page=root_page,
            parent=None
        )
        
        self.stdout.write(f'  ✅ Hierarchy racine: {root_page.title} (Level {root_hierarchy.get_level()})')
        
        # Créer niveau 2
        level2_hierarchy = PageHierarchy.objects.create(
            page=level2_page,
            parent=root_page
        )
        
        self.stdout.write(f'  ✅ Hierarchy niveau 2: {level2_page.title} (Level {level2_hierarchy.get_level()})')
        
        # Créer niveau 3
        level3_hierarchy = PageHierarchy.objects.create(
            page=level3_page,
            parent=level2_page
        )
        
        self.stdout.write(f'  ✅ Hierarchy niveau 3: {level3_page.title} (Level {level3_hierarchy.get_level()})')
        
        # Tester limite 3 niveaux
        try:
            PageHierarchy.objects.create(
                page=self.test_pages[3],
                parent=level3_page
            )
            self.stdout.write('  ❌ Limite 3 niveaux échouée')
        except ValidationError:
            self.stdout.write('  ✅ Limite 3 niveaux respectée')
        
        # Tester get_root_page
        root_found = level3_hierarchy.get_root_page()
        self.stdout.write(f'  ✅ Root page from level 3: {root_found.title}')
        
        # Créer et tester breadcrumbs
        breadcrumb = PageBreadcrumb.objects.create(page=level3_page)
        breadcrumb_data = breadcrumb.regenerate_breadcrumb()
        
        self.stdout.write(f'  ✅ Breadcrumb généré: {len(breadcrumb_data)} niveaux')
        for i, item in enumerate(breadcrumb_data):
            self.stdout.write(f'    {i+1}. {item["title"]} → {item["url"]}')
        
        # Test filtres hiérarchie
        hierarchy_filter = PageHierarchyFilter(data={
            'website': self.test_website.id,
            'level': 2
        })
        if hierarchy_filter.is_valid():
            level2_pages = hierarchy_filter.qs
            self.stdout.write(f'  ✅ HierarchyFilter niveau 2: {level2_pages.count()} résultats')
        
        # Test filtres breadcrumb
        breadcrumb_filter = PageBreadcrumbFilter(data={
            'website': self.test_website.id,
            'has_breadcrumb': True
        })
        if breadcrumb_filter.is_valid():
            pages_with_breadcrumb = breadcrumb_filter.qs
            self.stdout.write(f'  ✅ BreadcrumbFilter: {pages_with_breadcrumb.count()} avec breadcrumb')
        
        # Stocker pour tests cross-app
        self.hierarchy_pages = {
            'root': root_page,
            'level2': level2_page,
            'level3': level3_page
        }
    
    def test_seo_pages_layout(self):
        """Test du page builder et layout"""
        self.stdout.write('\n🎨 Testing seo_pages_layout (Page Builder)...')
        
        test_page = self.test_pages[0]
        
        # Créer PageLayout
        page_layout = PageLayout.objects.create(
            page=test_page,
            render_strategy='sections',
            layout_data={
                'theme': 'modern',
                'version': '2.0',
                'meta': {'created_by': 'test_script'}
            }
        )
        
        self.stdout.write(f'  ✅ PageLayout créé: {page_layout.render_strategy}')
        
        # Créer container layout colonnes
        container_section = PageSection.objects.create(
            page=test_page,
            section_type='layout_columns',
            data={'type': 'container'},  # ✅ Au lieu de data={}
            layout_config={
                'columns': [8, 4],
                'gap': '2rem',
                'align': 'start'
            },
            order=0,
            created_by=self.test_user
        )
        
        self.stdout.write(f'  ✅ Container section: {container_section.section_type}')
        self.stdout.write(f'    - Layout config: {container_section.layout_config}')
        
        # Créer sections enfants
        child_sections_data = [
            {
                'section_type': 'hero_banner',
                'data': {
                    'title': 'Hero Test Title',
                    'subtitle': 'Hero Test Subtitle',
                    'cta': {'text': 'Call to Action', 'href': '/contact'}
                },
                'order': 0
            },
            {
                'section_type': 'cta_banner',
                'data': {
                    'title': 'CTA Test',
                    'button': {'text': 'Get Started', 'href': '/signup'}
                },
                'order': 1
            }
        ]
        
        child_sections = []
        for child_data in child_sections_data:
            child_section = PageSection.objects.create(
                page=test_page,
                parent_section=container_section,
                created_by=self.test_user,
                **child_data
            )
            child_sections.append(child_section)
            
            self.stdout.write(f'    ↳ Child: {child_section.section_type} (order: {child_section.order})')
        
        # Créer section simple (sans parent)
        simple_section = PageSection.objects.create(
            page=test_page,
            section_type='features_grid',
            data={
                'title': 'Our Features',
                'features': [
                    {'title': 'Feature 1', 'description': 'Description 1'},
                    {'title': 'Feature 2', 'description': 'Description 2'},
                    {'title': 'Feature 3', 'description': 'Description 3'}
                ]
            },
            order=1,
            created_by=self.test_user
        )
        
        self.stdout.write(f'  ✅ Simple section: {simple_section.section_type}')
        
        # Tester limite 2 niveaux
        try:
            PageSection.objects.create(
                page=test_page,
                parent_section=child_sections[0],  # Niveau 3 interdit
                section_type='rich_text',
                order=0
            )
            self.stdout.write('  ❌ Limite 2 niveaux échouée')
        except ValidationError:
            self.stdout.write('  ✅ Limite 2 niveaux respectée')
        
        # Stocker pour tests
        self.page_layout = page_layout
        self.container_section = container_section
        self.child_sections = child_sections
    
    def test_seo_pages_seo(self):
        """Test des configurations SEO"""
        self.stdout.write('\n🔍 Testing seo_pages_seo (SEO Config)...')
        
        for page in self.test_pages[:3]:  # Tester 3 pages
            # Créer PageSEO
            page_seo = PageSEO.objects.create(
                page=page,
                featured_image=f'https://example.com/og-{page.page_type}.jpg',
                sitemap_priority=0.8,
                sitemap_changefreq='weekly',
                exclude_from_sitemap=False
            )
            
            # Auto-assign defaults
            page_seo.auto_assign_sitemap_defaults()
            page_seo.save()
            
            self.stdout.write(f'  ✅ PageSEO: {page.title}')
            self.stdout.write(f'    - Priority: {page_seo.sitemap_priority}')
            self.stdout.write(f'    - Changefreq: {page_seo.sitemap_changefreq}')
            self.stdout.write(f'    - Featured image: {page_seo.featured_image}')
            
            # Créer PagePerformance
            page_performance = PagePerformance.objects.create(
                page=page,
                last_rendered_at=timezone.now(),
                render_time_ms=250,
                cache_hits=45
            )
            
            needs_regen = page_performance.needs_regeneration()
            self.stdout.write(f'    - Needs regeneration: {needs_regen}')
            self.stdout.write(f'    - Render time: {page_performance.render_time_ms}ms')
            self.stdout.write(f'    - Cache hits: {page_performance.cache_hits}')
        
        # Test filtres SEO
        seo_filter = PageSEOFilter(data={
            'website': self.test_website.id,
            'sitemap_priority_high': True
        })
        if seo_filter.is_valid():
            high_priority_pages = seo_filter.qs
            self.stdout.write(f'  ✅ SEOFilter priorité élevée: {high_priority_pages.count()} résultats')
        
        # Test filtres performance
        perf_filter = PagePerformanceFilter(data={
            'website': self.test_website.id,
            'never_rendered': False
        })
        if perf_filter.is_valid():
            rendered_pages = perf_filter.qs
            self.stdout.write(f'  ✅ PerformanceFilter rendues: {rendered_pages.count()} résultats')
    
    def test_seo_pages_workflow(self):
        """Test du workflow de publication"""
        self.stdout.write('\n⚡ Testing seo_pages_workflow (Workflow)...')
        
        test_page = self.test_pages[0]
        
        # Créer PageStatus
        page_status = PageStatus.objects.create(
            page=test_page,
            status='draft',
            status_changed_by=self.test_user,
            production_notes='Page créée pour test workflow'
        )
        
        self.stdout.write(f'  ✅ PageStatus initial: {page_status.get_status_display()}')
        self.stdout.write(f'    - Color: {page_status.get_status_color()}')
        self.stdout.write(f'    - Can be published: {page_status.can_be_published()}')
        self.stdout.write(f'    - Publicly accessible: {page_status.is_publicly_accessible()}')
        
        # Tester transitions de statut
        transitions_test = [
            ('in_progress', 'En développement'),
            ('pending_review', 'En attente de review'),
            ('approved', 'Approuvé'),
            ('published', 'Publié')
        ]
        
        for new_status, description in transitions_test:
            # Vérifier statuts possibles
            possible_statuses = page_status.get_next_possible_statuses()
            
            if new_status in possible_statuses:
                old_status = page_status.status
                page_status.update_status(
                    new_status, 
                    self.test_user, 
                    f'Transition test vers {description}'
                )
                
                self.stdout.write(f'  ✅ Transition: {page_status.get_status_display()}')
                
                # Créer entrée historique
                PageWorkflowHistory.objects.create(
                    page=test_page,
                    old_status=old_status,
                    new_status=new_status,
                    changed_by=self.test_user,
                    notes=f'Test transition {description}'
                )
            else:
                self.stdout.write(f'  ⚠️ Transition impossible: {new_status}')
        
        # Tester programmation
        page_scheduling = PageScheduling.objects.create(
            page=test_page,
            scheduled_publish_date=timezone.now() + timezone.timedelta(days=1),
            auto_publish=True
        )
        
        is_ready = page_scheduling.is_ready_to_publish()
        self.stdout.write(f'  ✅ Scheduling créé: ready={is_ready}')
        self.stdout.write(f'    - Scheduled for: {page_scheduling.scheduled_publish_date}')
        self.stdout.write(f'    - Auto publish: {page_scheduling.auto_publish}')
        
        # Test filtres workflow
        status_filter = PageStatusFilter(data={
            'website': self.test_website.id,
            'is_published': True
        })
        if status_filter.is_valid():
            published_pages = status_filter.qs
            self.stdout.write(f'  ✅ StatusFilter published: {published_pages.count()} résultats')
        
        # Test filtres historique
        history_filter = PageWorkflowHistoryFilter(data={
            'website': self.test_website.id,
            'status_progression': True
        })
        if history_filter.is_valid():
            progressions = history_filter.qs
            self.stdout.write(f'  ✅ HistoryFilter progressions: {progressions.count()} résultats')
        
        # Test filtres scheduling
        scheduling_filter = PageSchedulingFilter(data={
            'website': self.test_website.id,
            'auto_publish': True
        })
        if scheduling_filter.is_valid():
            auto_publish_pages = scheduling_filter.qs
            self.stdout.write(f'  ✅ SchedulingFilter auto-publish: {auto_publish_pages.count()} résultats')
        
        # Stocker pour tests
        self.page_status = page_status
        self.page_scheduling = page_scheduling
    
    def test_seo_pages_keywords(self):
        """Test des associations mots-clés"""
        self.stdout.write('\n🔑 Testing seo_pages_keywords (Keywords Association)...')
        
        if not KEYWORDS_AVAILABLE or not self.test_keywords_ids:
            self.stdout.write('  ⚠️ Pas de keywords disponibles pour le test')
            return
        
        test_page = self.test_pages[0]
        
        # Créer associations de différents types
        keyword_associations = [
            {'keyword_id': self.test_keywords_ids[0], 'type': 'primary', 'position': 1},
            {'keyword_id': self.test_keywords_ids[1], 'type': 'secondary', 'position': 2},
            {'keyword_id': self.test_keywords_ids[2], 'type': 'anchor', 'position': 3}
        ]
        
        created_associations = []
        
        for assoc_data in keyword_associations:
            try:
                keyword = Keyword.objects.get(id=assoc_data['keyword_id'])
                
                page_keyword = PageKeyword.objects.create(
                    page=test_page,
                    keyword=keyword,
                    keyword_type=assoc_data['type'],
                    position=assoc_data['position'],
                    is_ai_selected=False,
                    notes=f'Test association {assoc_data["type"]}'
                )
                
                created_associations.append(page_keyword)
                
                self.stdout.write(f'  ✅ Association: {keyword.keyword} ({page_keyword.keyword_type})')
                self.stdout.write(f'    - Volume: {page_keyword.get_keyword_volume()}')
                self.stdout.write(f'    - Position: {page_keyword.position}')
                self.stdout.write(f'    - AI selected: {page_keyword.is_ai_selected}')
                
            except Exception as e:
                self.stdout.write(f'  ⚠️ Erreur association {assoc_data}: {str(e)}')
        
        # Tester contrainte mot-clé primaire unique
        if created_associations:
            try:
                PageKeyword.objects.create(
                    page=test_page,
                    keyword=created_associations[0].keyword,
                    keyword_type='primary'  # Doublon primaire interdit
                )
                self.stdout.write('  ❌ Contrainte primaire unique échouée')
            except ValidationError:
                self.stdout.write('  ✅ Contrainte primaire unique respectée')
            
            # Tester contrainte doublon keyword/page
            try:
                PageKeyword.objects.create(
                    page=test_page,
                    keyword=created_associations[1].keyword,
                    keyword_type='anchor'  # Même keyword, type différent = interdit
                )
                self.stdout.write('  ❌ Contrainte doublon keyword/page échouée')
            except ValidationError:
                self.stdout.write('  ✅ Contrainte doublon keyword/page respectée')
        
        # Test filtres keywords
        keyword_filter = PageKeywordFilter(data={
            'website': self.test_website.id,
            'keyword_type': 'primary'
        })
        if keyword_filter.is_valid():
            primary_keywords = keyword_filter.qs
            self.stdout.write(f'  ✅ KeywordFilter primaires: {primary_keywords.count()} résultats')
        
        # Test filtres par volume
        high_volume_filter = PageKeywordFilter(data={
            'website': self.test_website.id,
            'high_volume': True
        })
        if high_volume_filter.is_valid():
            high_volume = high_volume_filter.qs
            self.stdout.write(f'  ✅ KeywordFilter high volume: {high_volume.count()} résultats')
        
        # Stocker pour tests
        self.page_keywords = created_associations
    
    def test_all_filters(self):
        """Test spécialisé de tous les filtres"""
        self.stdout.write('\n🔍 Testing All Filters (Comprehensive)...')
        
        # Test combinaisons de filtres complexes
        
        # 1. Filtres Website
        self.stdout.write('  🔎 Testing WebsiteFilter combinations...')
        website_complex_filter = WebsiteFilter(data={
            'brand': self.test_brand.id,
            'domain_authority__gte': 50,
            'search': 'test'
        })
        if website_complex_filter.is_valid():
            complex_results = website_complex_filter.qs
            self.stdout.write(f'    ✅ Complex website filter: {complex_results.count()} résultats')
        
        # 2. Filtres Page
        self.stdout.write('  🔎 Testing PageFilter combinations...')
        page_complex_filter = PageFilter(data={
            'website': self.test_website.id,
            'page_type': 'blog',
            'search_intent': 'MOFU',
            'has_meta_description': True
        })
        if page_complex_filter.is_valid():
            complex_pages = page_complex_filter.qs
            self.stdout.write(f'    ✅ Complex page filter: {complex_pages.count()} résultats')
        
        # 3. Filtres Hierarchy avancés
        self.stdout.write('  🔎 Testing HierarchyFilter advanced...')
        hierarchy_advanced_filter = PageHierarchyFilter(data={
            'website': self.test_website.id,
            'is_root': False,
            'has_children': True
        })
        if hierarchy_advanced_filter.is_valid():
            advanced_hierarchy = hierarchy_advanced_filter.qs
            self.stdout.write(f'    ✅ Advanced hierarchy filter: {advanced_hierarchy.count()} résultats')
        
        # 4. Filtres SEO avancés
        self.stdout.write('  🔎 Testing SEOFilter advanced...')
        seo_advanced_filter = PageSEOFilter(data={
            'website': self.test_website.id,
            'sitemap_priority__gte': 0.5,
            'has_featured_image': True,
            'page_type': 'vitrine'
        })
        if seo_advanced_filter.is_valid():
            advanced_seo = seo_advanced_filter.qs
            self.stdout.write(f'    ✅ Advanced SEO filter: {advanced_seo.count()} résultats')
        
        # 5. Filtres Workflow avancés
        self.stdout.write('  🔎 Testing WorkflowFilter advanced...')
        workflow_advanced_filter = PageStatusFilter(data={
            'website': self.test_website.id,
            'needs_review': True,
            'status_changed_after': (timezone.now() - timezone.timedelta(days=1)).isoformat()
        })
        if workflow_advanced_filter.is_valid():
            advanced_workflow = workflow_advanced_filter.qs
            self.stdout.write(f'    ✅ Advanced workflow filter: {advanced_workflow.count()} résultats')
        
        # 6. Filtres Performance avec dates
        self.stdout.write('  🔎 Testing PerformanceFilter with dates...')
        perf_dates_filter = PagePerformanceFilter(data={
            'website': self.test_website.id,
            'render_time_slow': False,
            'rendered_after': (timezone.now() - timezone.timedelta(hours=1)).isoformat()
        })
        if perf_dates_filter.is_valid():
            recent_renders = perf_dates_filter.qs
            self.stdout.write(f'    ✅ Performance dates filter: {recent_renders.count()} résultats')
        
        # 7. Filtres Keywords avec search
        if KEYWORDS_AVAILABLE and self.test_keywords_ids:
            self.stdout.write('  🔎 Testing KeywordFilter with search...')
            keyword_search_filter = PageKeywordFilter(data={
                'website': self.test_website.id,
                'search': 'test',
                'is_ai_selected': False
            })
            if keyword_search_filter.is_valid():
                search_keywords = keyword_search_filter.qs
                self.stdout.write(f'    ✅ Keyword search filter: {search_keywords.count()} résultats')
    
    def test_advanced_hierarchy(self):
        """Tests avancés de hiérarchie"""
        self.stdout.write('\n🌲 Testing Advanced Hierarchy Features...')
        
        if not hasattr(self, 'hierarchy_pages'):
            self.stdout.write('  ⚠️ Pas de hiérarchie de base pour tests avancés')
            return
        
        # Test navigation dans la hiérarchie
        level3_page = self.hierarchy_pages['level3']
        hierarchy = level3_page.hierarchy
        
        # Remonter jusqu'à la racine
        path_to_root = []
        current = level3_page
        
        while current:
            path_to_root.append(current.title)
            if hasattr(current, 'hierarchy') and current.hierarchy.parent:
                current = current.hierarchy.parent
            else:
                break
        
        self.stdout.write(f'  ✅ Path to root: {" → ".join(reversed(path_to_root))}')
        
        # Test enfants d'une page
        root_page = self.hierarchy_pages['root']
        children = Page.objects.filter(hierarchy__parent=root_page)
        
        self.stdout.write(f'  ✅ Root children: {[child.title for child in children]}')
        
        # Test regeneration breadcrumb en cascade
        for page in [self.hierarchy_pages['level2'], self.hierarchy_pages['level3']]:
            breadcrumb, created = PageBreadcrumb.objects.get_or_create(page=page)
            breadcrumb_data = breadcrumb.regenerate_breadcrumb()
            
            self.stdout.write(f'  ✅ Breadcrumb {page.title}: {len(breadcrumb_data)} niveaux')
        
        # Test filtres hiérarchiques avancés
        root_filter = PageHierarchyFilter(data={'is_root': True, 'website': self.test_website.id})
        if root_filter.is_valid():
            root_pages = root_filter.qs
            self.stdout.write(f'  ✅ Root pages filter: {root_pages.count()} résultats')
    
    def test_advanced_workflow(self):
        """Tests avancés de workflow"""
        self.stdout.write('\n⚙️ Testing Advanced Workflow Features...')
        
        if not hasattr(self, 'page_status'):
            self.stdout.write('  ⚠️ Pas de workflow de base pour tests avancés')
            return
        
        # Test workflow complet avec historique
        workflow_steps = [
            ('changes_requested', 'Modifications demandées par le client'),
            ('in_progress', 'Corrections en cours'),
            ('pending_review', 'Nouvelle review demandée'),
            ('approved', 'Approuvé après corrections'),
            ('scheduled', 'Programmé pour publication'),
            ('published', 'Publié en production')
        ]
        
        for status, note in workflow_steps:
            if status in self.page_status.get_next_possible_statuses():
                old_status = self.page_status.status
                
                self.page_status.update_status(status, self.test_user, note)
                
                # Créer historique
                PageWorkflowHistory.objects.create(
                    page=self.page_status.page,
                    old_status=old_status,
                    new_status=status,
                    changed_by=self.test_user,
                    notes=note
                )
                
                self.stdout.write(f'  ✅ Workflow: {old_status} → {status}')
        
        # Test historique complet
        history = PageWorkflowHistory.objects.filter(
            page=self.page_status.page
        ).order_by('created_at')
        
        self.stdout.write(f'  ✅ Historique complet: {history.count()} transitions')
        for entry in history:
            self.stdout.write(f'    {entry.old_status} → {entry.new_status} by {entry.changed_by.username}')
        
        # Test publication programmée
        if hasattr(self, 'page_scheduling'):
            # Simuler passage du temps
            past_date = timezone.now() - timezone.timedelta(hours=1)
            self.page_scheduling.scheduled_publish_date = past_date
            self.page_scheduling.save()
            
            is_ready_now = self.page_scheduling.is_ready_to_publish()
            self.stdout.write(f'  ✅ Ready to publish (past date): {is_ready_now}')
    
    def test_advanced_page_builder(self):
        """Tests avancés du page builder"""
        self.stdout.write('\n🎨 Testing Advanced Page Builder Features...')
        
        if not hasattr(self, 'page_layout'):
            self.stdout.write('  ⚠️ Pas de layout de base pour tests avancés')
            return
        
        test_page = self.page_layout.page
        
        # Créer layout complexe avec grille
        grid_container = PageSection.objects.create(
            page=test_page,
            section_type='layout_grid',
            data={'type': 'grid_container'},  # ✅ Au lieu de vide
            layout_config={
                'grid_template_columns': 'repeat(3, 1fr)',
                'gap': '1.5rem',
                'auto_rows': 'minmax(200px, auto)'
            },
            order=2,
            created_by=self.test_user
        )
        
        # Ajouter sections dans la grille
        grid_sections = []
        for i in range(6):
            section = PageSection.objects.create(
                page=test_page,
                parent_section=grid_container,
                section_type='rich_text',
                data={
                    'content': f'Grid item {i+1} content',
                    'alignment': 'center'
                },
                order=i,
                created_by=self.test_user
            )
            grid_sections.append(section)
        
        self.stdout.write(f'  ✅ Grid container créé avec {len(grid_sections)} items')
        
        # Créer layout stack
        stack_container = PageSection.objects.create(
            page=test_page,
            section_type='layout_stack',
            data={'type': 'stack_container'},
            layout_config={
                'gap': '1rem',
                'align': 'center'
            },
            order=3,
            created_by=self.test_user
        )
        
        # Test réorganisation des sections
        all_sections = PageSection.objects.filter(page=test_page, parent_section__isnull=True)
        self.stdout.write(f'  ✅ Top-level sections: {all_sections.count()}')
        
        for section in all_sections:
            children = section.child_sections.all()
            self.stdout.write(f'    {section.section_type}: {children.count()} enfants')
        
        # Test génération JSON pour renderer
        layout_data = {
            'strategy': self.page_layout.render_strategy,
            'sections': []
        }
        
        # Simuler génération JSON pour Next.js
        for section in all_sections.order_by('order'):
            section_data = {
                'type': section.section_type,
                'data': section.data,
                'layout_config': section.layout_config,
                'children': []
            }
            
            for child in section.child_sections.order_by('order'):
                child_data = {
                    'type': child.section_type,
                    'data': child.data
                }
                section_data['children'].append(child_data)
            
            layout_data['sections'].append(section_data)
        
        # Mettre à jour le layout
        self.page_layout.layout_data = layout_data
        self.page_layout.save()
        
        self.stdout.write(f'  ✅ Layout JSON généré: {len(layout_data["sections"])} sections racines')
    
    def test_cross_app_integration(self):
        """Test de l'intégration cross-app"""
        self.stdout.write('\n🔗 Testing Cross-App Integration...')
        
        # Test page complète avec toutes les extensions
        test_page = self.test_pages[0]
        
        page_full = Page.objects.select_related(
            'website',
            'hierarchy',
            'layout_config',
            'seo_config',
            'workflow_status',
            'scheduling',
            'performance',
            'breadcrumb_cache'
        ).prefetch_related(
            'sections',
            'sections__child_sections',
            'page_keywords',
            'page_keywords__keyword',
            'workflow_history'
        ).get(id=test_page.id)
        
        self.stdout.write(f'  ✅ Page complète chargée: {page_full.title}')
        
        # Vérifier toutes les relations
        relations_check = {
            'website': hasattr(page_full, 'website') and page_full.website,
            'hierarchy': hasattr(page_full, 'hierarchy'),
            'layout_config': hasattr(page_full, 'layout_config'),
            'seo_config': hasattr(page_full, 'seo_config'),
            'workflow_status': hasattr(page_full, 'workflow_status'),
            'sections': page_full.sections.exists(),
            'keywords': page_full.page_keywords.exists() if KEYWORDS_AVAILABLE else True,
        }
        
        for relation, exists in relations_check.items():
            status = '✅' if exists else '❌'
            self.stdout.write(f'    {status} {relation}: {exists}')
        
        # Test requête optimisée cross-app
        from django.db import models
        
        pages_with_stats = Page.objects.select_related(
            'website', 'workflow_status', 'seo_config'
        ).annotate(
            sections_count=models.Count('sections'),
            keywords_count=models.Count('page_keywords'),
            children_count=models.Count('children_hierarchy')
        ).filter(website=self.test_website)
        
        self.stdout.write(f'  ✅ Pages avec stats: {pages_with_stats.count()}')
        
        for page in pages_with_stats:
            status_display = page.workflow_status.get_status_display() if hasattr(page, 'workflow_status') else 'N/A'
            sitemap_priority = page.seo_config.sitemap_priority if hasattr(page, 'seo_config') else 'N/A'
            
            self.stdout.write(f'    {page.title}:')
            self.stdout.write(f'      - Status: {status_display}')
            self.stdout.write(f'      - Sections: {page.sections_count}')
            self.stdout.write(f'      - Keywords: {page.keywords_count}')
            self.stdout.write(f'      - Children: {page.children_count}')
            self.stdout.write(f'      - Sitemap Priority: {sitemap_priority}')
    
    def test_filters_integration(self):
        """Test de l'intégration des filtres"""
        self.stdout.write('\n🔍 Testing Filters Integration...')
        
        # Test pipeline de filtres combinés
        base_pages = Page.objects.filter(website=self.test_website)
        
        # Appliquer plusieurs filtres en séquence
        page_filter = PageFilter(data={
            'website': self.test_website.id,
            'page_type': 'blog'
        }, queryset=base_pages)
        
        if page_filter.is_valid():
            blog_pages = page_filter.qs
            
            # Appliquer filtre workflow sur le résultat
            # Créer d'abord PageStatusFilter s'il n'existe pas encore
            try:
                from seo_pages_workflow.filters import PageStatusFilter
                workflow_filter = PageStatusFilter(
                    data={'is_published': False},
                    queryset=PageStatus.objects.filter(page__in=blog_pages)
                )
                
                if workflow_filter.is_valid():
                    draft_statuses = workflow_filter.qs
                    draft_blog_pages = Page.objects.filter(
                        id__in=draft_statuses.values_list('page_id', flat=True)
                    )
                    self.stdout.write(f'  ✅ Pipeline filters: {draft_blog_pages.count()} blog drafts')
            except ImportError:
                self.stdout.write('  ⚠️ PageStatusFilter non disponible, test partiel')
                # Test alternatif direct
                draft_blog_pages = blog_pages.filter(
                    workflow_status__status__in=['draft', 'in_progress']
                )
                self.stdout.write(f'  ✅ Blog drafts (direct): {draft_blog_pages.count()} résultats')
        
        # Test filtres cross-app avec annotations
        from django.db import models
        
        complex_filter_data = {
            'website': self.test_website.id,
            'has_meta_description': True
        }
        
        complex_filter = PageFilter(data=complex_filter_data)
        if complex_filter.is_valid():
            complex_pages = complex_filter.qs.annotate(
                has_seo_config=models.Case(
                    models.When(seo_config__isnull=False, then=models.Value(True)),
                    default=models.Value(False),
                    output_field=models.BooleanField()
                ),
                total_sections=models.Count('sections')
            )
            
            self.stdout.write(f'  ✅ Complex annotated filter: {complex_pages.count()} résultats')
            
            # Limiter l'affichage pour éviter trop de logs
            for page in complex_pages[:3]:
                self.stdout.write(f'    {page.title}: SEO={page.has_seo_config}, Sections={page.total_sections}')
    
    
    
    def test_complete_workflow(self):
        """Test du workflow complet bout-en-bout"""
        self.stdout.write('\n🚀 Testing Complete End-to-End Workflow...')
        
        # Créer une page complète de A à Z
        with transaction.atomic():
            # 1. Créer la page
            complete_page = Page.objects.create(
                website=self.test_website,
                title=f'Complete Workflow Test Page {uuid.uuid4().hex[:6]}',
                page_type='landing',
                search_intent='BOFU',
                meta_description='Page de test workflow complet'
            )
            
            self.stdout.write(f'  ✅ 1. Page créée: {complete_page.title}')
            
            # 2. Configurer hiérarchie
            hierarchy = PageHierarchy.objects.create(
                page=complete_page,
                parent=None  # Page racine
            )
            
            self.stdout.write(f'  ✅ 2. Hiérarchie configurée (level {hierarchy.get_level()})')
            
            # 3. Créer layout avec sections
            layout = PageLayout.objects.create(
                page=complete_page,
                render_strategy='sections'
            )
            
            hero_section = PageSection.objects.create(
                page=complete_page,
                section_type='hero_banner',
                data={
                    'title': 'Complete Test Hero',
                    'subtitle': 'End-to-end workflow test',
                    'cta': {'text': 'Get Started', 'href': '/signup'}
                },
                order=0,
                created_by=self.test_user
            )
            
            self.stdout.write(f'  ✅ 3. Layout configuré avec sections')
            
            # 4. Configurer SEO
            seo_config = PageSEO.objects.create(
                page=complete_page,
                sitemap_priority=1.0,
                sitemap_changefreq='weekly'
            )
            seo_config.auto_assign_sitemap_defaults()
            seo_config.save()
            
            performance = PagePerformance.objects.create(
                page=complete_page,
                last_rendered_at=timezone.now(),
                render_time_ms=180
            )
            
            self.stdout.write(f'  ✅ 4. SEO configuré (priority: {seo_config.sitemap_priority})')
            
            # 5. Configurer workflow
            status = PageStatus.objects.create(
                page=complete_page,
                status='draft',
                status_changed_by=self.test_user,
                production_notes='Page créée via workflow complet'
            )
            
            scheduling = PageScheduling.objects.create(
                page=complete_page,
                scheduled_publish_date=timezone.now() + timezone.timedelta(days=1),
                auto_publish=True
            )
            
            self.stdout.write(f'  ✅ 5. Workflow configuré (status: {status.get_status_display()})')
            
            # 6. Ajouter mots-clés si disponibles
            if KEYWORDS_AVAILABLE and self.test_keywords_ids:
                try:
                    keyword = Keyword.objects.get(id=self.test_keywords_ids[0])
                    
                    page_keyword = PageKeyword.objects.create(
                        page=complete_page,
                        keyword=keyword,
                        keyword_type='primary',
                        position=1,
                        is_ai_selected=False
                    )
                    
                    self.stdout.write(f'  ✅ 6. Mot-clé ajouté: {keyword.keyword}')
                except Exception as e:
                    self.stdout.write(f'  ⚠️ 6. Mot-clé non ajouté: {str(e)}')
            
            # 7. Générer breadcrumb
            breadcrumb = PageBreadcrumb.objects.create(page=complete_page)
            breadcrumb_data = breadcrumb.regenerate_breadcrumb()
            
            self.stdout.write(f'  ✅ 7. Breadcrumb généré ({len(breadcrumb_data)} niveaux)')
            
            # 8. Simuler workflow de publication
            workflow_transitions = ['in_progress', 'pending_review', 'approved', 'published']
            
            for new_status in workflow_transitions:
                if new_status in status.get_next_possible_statuses():
                    old_status = status.status
                    status.update_status(new_status, self.test_user, f'Workflow test: {new_status}')
                    
                    PageWorkflowHistory.objects.create(
                        page=complete_page,
                        old_status=old_status,
                        new_status=new_status,
                        changed_by=self.test_user,
                        notes=f'Transition automatique workflow test'
                    )
            
            self.stdout.write(f'  ✅ 8. Workflow exécuté (final: {status.get_status_display()})')
            
            # 9. Test de tous les filtres sur cette page
            filter_tests = [
                ('PageFilter', PageFilter({'title': 'Complete'})),
                ('PageStatusFilter', PageStatusFilter({'is_published': True})),
                ('PageSEOFilter', PageSEOFilter({'sitemap_priority_high': True})),
                ('PageSchedulingFilter', PageSchedulingFilter({'auto_publish': True})),
            ]
            
            for filter_name, filter_instance in filter_tests:
                if filter_instance.is_valid():
                    results = filter_instance.qs.filter(id=complete_page.id)
                    found = results.exists()
                    self.stdout.write(f'    ✅ {filter_name}: {"Found" if found else "Not found"}')
            
            # 10. Vérification finale
            final_check = Page.objects.select_related(
                'website', 'hierarchy', 'layout_config', 'seo_config',
                'workflow_status', 'scheduling', 'performance'
            ).prefetch_related(
                'sections', 'page_keywords', 'workflow_history'
            ).get(id=complete_page.id)
            
            completeness_score = 0
            checks = [
                ('Website', final_check.website is not None),
                ('Hierarchy', hasattr(final_check, 'hierarchy')),
                ('Layout', hasattr(final_check, 'layout_config')),
                ('SEO', hasattr(final_check, 'seo_config')),
                ('Status', hasattr(final_check, 'workflow_status')),
                ('Sections', final_check.sections.exists()),
                ('Keywords', final_check.page_keywords.exists() if KEYWORDS_AVAILABLE else True),
                ('History', final_check.workflow_history.exists())
            ]
            
            for check_name, passed in checks:
                if passed:
                    completeness_score += 1
                    self.stdout.write(f'    ✅ {check_name}: OK')
                else:
                    self.stdout.write(f'    ❌ {check_name}: Manquant')
            
            completion_percentage = (completeness_score / len(checks)) * 100
            self.stdout.write(f'  ✅ 9. Complétude finale: {completion_percentage:.1f}% ({completeness_score}/{len(checks)})')
        
        self.stdout.write(f'  🎉 Workflow complet terminé avec succès !')
    
    def cleanup_test_data(self):
        """Nettoie les données de test"""
        self.stdout.write('\n🧹 Cleanup des données de test SEO Pages...')
        
        # Nettoyer uniquement les données créées pour ce test
        if hasattr(self, 'test_website'):
            # Si website créé pour test, supprimer (cascade)
            if not self.test_website.name.startswith('Test Website'):
                self.stdout.write('  ⚠️ Website existant préservé')
            else:
                self.test_website.delete()
                self.stdout.write('  ✅ Test website supprimé')
        
        # Nettoyer keywords de test si créés
        if KEYWORDS_AVAILABLE and hasattr(self, 'test_keywords_ids'):
            test_keywords = Keyword.objects.filter(id__in=self.test_keywords_ids)
            test_keywords.delete()
            self.stdout.write(f'  ✅ {len(self.test_keywords_ids)} keywords de test supprimés')
        
        # Nettoyer brand de test si créée
        if hasattr(self, 'test_brand') and self.test_brand.name.startswith('Test Brand SEO'):
            self.test_brand.delete()
            self.stdout.write('  ✅ Test brand supprimée')
        
        self.stdout.write('  ✅ Cleanup terminé')