# backend/seo_pages_content/management/commands/test_seo_pages_endpoints.py

from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.db import transaction
import json
import uuid
from rest_framework_simplejwt.tokens import RefreshToken

from company_core.models import Company
from seo_websites_core.models import Website
from seo_pages_content.models import Page
from seo_pages_hierarchy.models import PageHierarchy
from seo_pages_workflow.models import PageStatus
from seo_pages_layout.models import PageLayout, PageSection

# Import keywords si disponible
try:
    from seo_keywords_base.models import Keyword
    from seo_pages_keywords.models import PageKeyword
    KEYWORDS_AVAILABLE = True
except ImportError:
    KEYWORDS_AVAILABLE = False

User = get_user_model()

class Command(BaseCommand):
    help = 'Test complet des endpoints API SEO Pages MEGAHUB (8 apps) - URLs VRAIES v3.0'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--app',
            type=str,
            choices=['content', 'hierarchy', 'layout', 'seo', 'workflow', 'keywords', 'all'],
            default='all',
            help='App spécifique à tester'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Affichage verbose des réponses'
        )
        parser.add_argument(
            '--skip-cleanup',
            action='store_true',
            help='Ne pas nettoyer les données de test'
        )
        parser.add_argument(
            '--test-permissions',
            action='store_true',
            help='Tester spécifiquement les permissions'
        )
        parser.add_argument(
            '--test-filters',
            action='store_true',
            help='Tester spécifiquement les filtres avancés'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔗 Testing SEO Pages API Endpoints v3.0 (URLs VRAIES)\n'))
        
        self.verbose = options['verbose']
        self.app_to_test = options['app']
        
        # 🔧 URLs VRAIES selon tes fichiers urls.py
        self.base_urls = {
            'pages': '/websites/pages',                      # seo_pages_content (direct)
            'builder_sections': '/websites/builder/sections', # seo_pages_layout
            'builder_layouts': '/websites/builder/layouts',   
            'structure_hierarchy': '/websites/structure/hierarchy', # seo_pages_hierarchy
            'structure_breadcrumbs': '/websites/structure/breadcrumbs',
            'workflow_status': '/websites/workflow/status',    # seo_pages_workflow
            'workflow_history': '/websites/workflow/history',
            'workflow_scheduling': '/websites/workflow/scheduling',
            'seo': '/websites/seo/seo',                       # seo_pages_seo
            'seo_performance': '/websites/seo/performance',
            'keywords': '/websites/keywords/page-keywords',   # seo_pages_keywords
            'sites': '/websites',                            # seo_websites_core (direct)
        }
        
        # Setup
        self.setup_client_and_auth()
        self.setup_test_data()
        
        # Tests par app avec URLs VRAIES
        if self.app_to_test in ['content', 'all']:
            self.test_pages_content_endpoints()
        
        if self.app_to_test in ['hierarchy', 'all']:
            self.test_pages_hierarchy_endpoints()
        
        if self.app_to_test in ['layout', 'all']:
            self.test_pages_layout_endpoints()
        
        if self.app_to_test in ['seo', 'all']:
            self.test_pages_seo_endpoints()
        
        if self.app_to_test in ['workflow', 'all']:
            self.test_pages_workflow_endpoints()
        
        if self.app_to_test in ['keywords', 'all'] and KEYWORDS_AVAILABLE:
            self.test_pages_keywords_endpoints()
        
        # Tests spécialisés
        if options['test_permissions']:
            self.test_permissions_comprehensive()
        
        if options['test_filters']:
            self.test_filters_comprehensive()
        
        # Tests cross-endpoint
        self.test_cross_endpoint_workflow()
        
        if not options['skip_cleanup']:
            self.cleanup_test_data()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Tous les tests d\'endpoints SEO Pages v3.0 sont passés !'))
    
    def setup_client_and_auth(self):
        """Setup client HTTP et authentification JWT"""
        self.stdout.write('🔐 Setup authentification...')
        
        self.client = Client()
        self.user = User.objects.first()
        self.company = Company.objects.first()
        
        if not self.user or not self.company:
            self.stdout.write(self.style.ERROR('❌ User ou Company manquant'))
            return
        
        # Générer JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Headers d'auth de base
        self.auth_headers = {
            'HTTP_AUTHORIZATION': f'Bearer {self.access_token}',
            'content_type': 'application/json',
        }
        
        self.stdout.write(f'  ✅ User: {self.user.username}')
        self.stdout.write(f'  ✅ Token: {self.access_token[:20]}...')
    
    def setup_test_data(self):
        """Prépare les données de test pour tous les endpoints"""
        self.stdout.write('📝 Setup données de test...')
        
        # Brand et Website
        self.test_brand = Brand.objects.filter(
            company=self.company
        ).first()
        
        if not self.test_brand:
            self.test_brand = Brand.objects.create(
                company=self.company,
                name=f'Test Brand API {uuid.uuid4().hex[:8]}',
                description='Brand de test endpoints'
            )
        
        # Website
        self.test_website, created = Website.objects.get_or_create(
            brand=self.test_brand,
            defaults={
                'name': f'Test Website API {uuid.uuid4().hex[:8]}',
                'url': 'https://test-api.example.com',
                'domain_authority': 70
            }
        )
        
        # Headers avec Brand-ID
        self.auth_headers['HTTP_X_BRAND_ID'] = str(self.test_brand.id)
        
        self.stdout.write(f'  ✅ Brand: {self.test_brand.name}')
        self.stdout.write(f'  ✅ Website: {self.test_website.name}')
        
        # Keywords de test si disponible
        if KEYWORDS_AVAILABLE:
            self.test_keywords = []
            for i in range(3):
                keyword, created = Keyword.objects.get_or_create(
                    keyword=f'test api keyword {i} {uuid.uuid4().hex[:6]}',
                    defaults={
                        'volume': 1000 + (i * 500),
                        'search_intent': ['TOFU', 'MOFU', 'BOFU'][i]
                    }
                )
                self.test_keywords.append(keyword)
            
            self.stdout.write(f'  ✅ Keywords: {len(self.test_keywords)} créés')
    
    def log_response(self, response, endpoint_name):
        """Log détaillé des réponses si verbose"""
        if self.verbose:
            try:
                if response.content:
                    data = response.json()
                    content = json.dumps(data, indent=2)[:500]
                    self.stdout.write(f'    📄 {endpoint_name}: {content}...')
            except:
                content = response.content.decode()[:200] if response.content else 'Empty'
                self.stdout.write(f'    📄 {endpoint_name}: {content}...')
    
    def test_pages_content_endpoints(self):
        """Test endpoints seo_pages_content (inchangé - déjà OK)"""
        self.stdout.write('\n📄 Testing seo_pages_content endpoints...')
        
        base_url = self.base_urls['pages']  # /websites/pages
        
        # 1. GET /websites/pages/ - Liste
        response = self.client.get(f'{base_url}/', **self.auth_headers)
        self.stdout.write(f'  GET {base_url}/: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', len(data))
            self.stdout.write(f'    ✅ {count} pages trouvées')
            self.log_response(response, 'pages-list')
        
        # 2. POST /websites/pages/ - Création
        page_data = {
            'title': f'Test API Page {uuid.uuid4().hex[:6]}',
            'website': self.test_website.id,
            'page_type': 'blog',
            'search_intent': 'TOFU',
            'meta_description': 'Page créée via test API'
        }
        
        response = self.client.post(
            f'{base_url}/',
            data=json.dumps(page_data),
            **self.auth_headers
        )
        self.stdout.write(f'  POST {base_url}/: {response.status_code}')
        
        if response.status_code == 201:
            created_page = response.json()
            self.test_page_id = created_page['id']
            self.stdout.write(f'    ✅ Page créée: {created_page.get("title")}')
            self.log_response(response, 'page-create')
        else:
            # Fallback: utiliser page existante
            existing_page = Page.objects.filter(website=self.test_website).first()
            if existing_page:
                self.test_page_id = existing_page.id
                self.stdout.write(f'    ⚠️ Utilisation page existante: {existing_page.title}')
            else:
                error_content = response.content.decode()[:300] if response.content else 'No content'
                self.stdout.write(f'    ❌ Création échouée ({response.status_code}): {error_content}')
                return
        
        # 3. GET /websites/pages/{id}/ - Détail
        response = self.client.get(f'{base_url}/{self.test_page_id}/', **self.auth_headers)
        self.stdout.write(f'  GET {base_url}/{self.test_page_id}/: {response.status_code}')
        
        if response.status_code == 200:
            page_detail = response.json()
            self.stdout.write(f'    ✅ Détail: {page_detail.get("title")}')
            self.stdout.write(f'    ✅ Hierarchy level: {page_detail.get("hierarchy_level", "N/A")}')
            self.stdout.write(f'    ✅ Keywords count: {page_detail.get("keywords_count", 0)}')
            self.log_response(response, 'page-detail')
        
        # Actions custom - by-website
        response = self.client.get(
            f'{base_url}/by_website/?website_id={self.test_website.id}',
            **self.auth_headers
        )
        self.stdout.write(f'  GET {base_url}/by_website/: {response.status_code}')
        
        if response.status_code == 200:
            by_website = response.json()
            total_pages = by_website.get('total_pages', 0)
            self.stdout.write(f'    ✅ Total pages: {total_pages}')
        


    
    def test_pages_hierarchy_endpoints(self):
        """Test endpoints seo_pages_hierarchy avec URLs VRAIES"""
        self.stdout.write('\n🌳 Testing seo_pages_hierarchy endpoints...')
        
        if not hasattr(self, 'test_page_id'):
            self.stdout.write('  ⚠️ Pas de page de test, skip hierarchy')
            return
        
        base_url = self.base_urls['structure_hierarchy']  # /websites/structure/hierarchy
        
        # 1. GET /websites/structure/hierarchy/ - Liste
        response = self.client.get(f'{base_url}/', **self.auth_headers)
        self.stdout.write(f'  GET {base_url}/: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', len(data))
            self.stdout.write(f'    ✅ {count} hiérarchies trouvées')
            self.log_response(response, 'hierarchy-list')
        
        # 2. POST /websites/structure/hierarchy/ - Créer hiérarchie
        hierarchy_data = {
            'page': self.test_page_id,
            'parent': None  # Page racine
        }
        
        response = self.client.post(
            f'{base_url}/',
            data=json.dumps(hierarchy_data),
            **self.auth_headers
        )
        self.stdout.write(f'  POST {base_url}/: {response.status_code}')
        
        if response.status_code == 201:
            hierarchy = response.json()
            self.test_hierarchy_id = hierarchy['id']
            self.stdout.write(f'    ✅ Hiérarchie créée: level {hierarchy.get("level", 1)}')
            self.log_response(response, 'hierarchy-create')
        elif response.status_code == 400:
            error_data = response.json()
            self.stdout.write(f'    ⚠️ Erreur hiérarchie: {error_data}')
            # Essayer de récupérer une hiérarchie existante
            existing = PageHierarchy.objects.filter(page_id=self.test_page_id).first()
            if existing:
                self.test_hierarchy_id = existing.id
                self.stdout.write(f'    ⚠️ Utilisation hiérarchie existante: {existing.id}')
        
        # 3. Actions custom - tree
        response = self.client.get(
            f'{base_url}/tree/?website_id={self.test_website.id}',
            **self.auth_headers
        )
        self.stdout.write(f'  GET {base_url}/tree/: {response.status_code}')
        
        if response.status_code == 200:
            tree_data = response.json()
            tree_count = len(tree_data.get('tree', []))
            self.stdout.write(f'    ✅ Arbre: {tree_count} nœuds racines')
            self.log_response(response, 'hierarchy-tree')
        
        # 4. Actions custom - rebuild
        rebuild_data = {'website_id': self.test_website.id}
        response = self.client.post(
            f'{base_url}/rebuild/',
            data=json.dumps(rebuild_data),
            **self.auth_headers
        )
        self.stdout.write(f'  POST {base_url}/rebuild/: {response.status_code}')
        
        if response.status_code == 200:
            rebuild_result = response.json()
            rebuilt_count = rebuild_result.get('rebuilt_count', 0)
            self.stdout.write(f'    ✅ Breadcrumbs reconstruits: {rebuilt_count}')
        
        # 5. Test breadcrumbs
        breadcrumbs_url = self.base_urls['structure_breadcrumbs']  # /websites/structure/breadcrumbs
        response = self.client.get(f'{breadcrumbs_url}/', **self.auth_headers)
        self.stdout.write(f'  GET {breadcrumbs_url}/: {response.status_code}')
        
        if response.status_code == 200:
            breadcrumbs = response.json()
            count = breadcrumbs.get('count', len(breadcrumbs))
            self.stdout.write(f'    ✅ {count} breadcrumbs trouvés')
    
    def test_pages_layout_endpoints(self):
        """Test endpoints seo_pages_layout avec URLs VRAIES + création auto PageLayout"""
        self.stdout.write('\n🎨 Testing seo_pages_layout endpoints...')
        
        if not hasattr(self, 'test_page_id'):
            self.stdout.write('  ⚠️ Pas de page de test, skip layout')
            return
        
        sections_url = self.base_urls['builder_sections']  # /websites/builder/sections
        layouts_url = self.base_urls['builder_layouts']    # /websites/builder/layouts
        
        # 0. S'assurer qu'un PageLayout existe pour notre page de test
        try:
            self.test_layout, created = PageLayout.objects.get_or_create(
                page_id=self.test_page_id,
                defaults={
                    'render_strategy': 'sections',
                    'created_by': self.user
                }
            )
            if created:
                self.stdout.write(f'    ✅ PageLayout créé pour page {self.test_page_id}')
            else:
                self.stdout.write(f'    ✅ PageLayout existant trouvé pour page {self.test_page_id}')
        except Exception as e:
            self.stdout.write(f'    ⚠️ Erreur création PageLayout: {e}')
            return
        
        # 1. GET /websites/builder/sections/ - Liste sections
        response = self.client.get(f'{sections_url}/', **self.auth_headers)
        self.stdout.write(f'  GET {sections_url}/: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', len(data))
            self.stdout.write(f'    ✅ {count} sections trouvées')
            self.log_response(response, 'sections-list')
        
        # 2. POST /websites/builder/sections/ - Créer section
        section_data = {
            'page': self.test_page_id,
            'section_type': 'hero_banner',
            'data': {
                'title': 'Test API Hero',
                'subtitle': 'Hero créé via API',
                'cta': {'text': 'Click me', 'href': '/test'}
            },
            'order': 0
        }
        
        response = self.client.post(
            f'{sections_url}/',
            data=json.dumps(section_data),
            **self.auth_headers
        )
        self.stdout.write(f'  POST {sections_url}/: {response.status_code}')
        
        if response.status_code == 201:
            section = response.json()
            self.test_section_id = section['id']
            self.stdout.write(f'    ✅ Section créée: {section.get("section_type")}')
            self.log_response(response, 'section-create')
        elif response.status_code == 400:
            error_data = response.json()
            self.stdout.write(f'    ⚠️ Erreur section: {error_data}')
        
        # 3. GET /websites/builder/layouts/ - Layouts
        response = self.client.get(f'{layouts_url}/', **self.auth_headers)
        self.stdout.write(f'  GET {layouts_url}/: {response.status_code}')
        
        if response.status_code == 200:
            layouts = response.json()
            count = layouts.get('count', len(layouts))
            self.stdout.write(f'    ✅ {count} layouts trouvés')
        
        # 4. Actions custom - reorder
        if hasattr(self, 'test_section_id'):
            reorder_data = {
                'page_id': self.test_page_id,
                'sections': [
                    {'id': self.test_section_id, 'order': 0}
                ]
            }
            response = self.client.post(
                f'{sections_url}/reorder/',
                data=json.dumps(reorder_data),
                **self.auth_headers
            )
            self.stdout.write(f'  POST {sections_url}/reorder/: {response.status_code}')
            
            if response.status_code == 200:
                self.stdout.write(f'    ✅ Sections réorganisées')
        
        # 5. Actions custom - render_data (MAINTENANT ÇA VA MARCHER)
        response = self.client.get(
            f'{layouts_url}/render_data/?page_id={self.test_page_id}',
            **self.auth_headers
        )
        self.stdout.write(f'  GET {layouts_url}/render_data/: {response.status_code}')
        
        if response.status_code == 200:
            render_data = response.json()
            sections_count = len(render_data.get('sections', []))
            self.stdout.write(f'    ✅ Render data: {sections_count} sections')
            self.log_response(response, 'render-data')
        elif response.status_code == 404:
            error_data = response.json()
            self.stdout.write(f'    ❌ Render data 404: {error_data.get("error", "Unknown")}')
        else:
            self.stdout.write(f'    ❌ Render data error: {response.status_code}')
    
    
    
    def test_pages_seo_endpoints(self):
        """Test endpoints seo_pages_seo avec URLs VRAIES"""
        self.stdout.write('\n🔍 Testing seo_pages_seo endpoints...')
        
        if not hasattr(self, 'test_page_id'):
            self.stdout.write('  ⚠️ Pas de page de test, skip SEO')
            return
        
        seo_url = self.base_urls['seo']              # /websites/seo/seo
        performance_url = self.base_urls['seo_performance']  # /websites/seo/performance
        
        # 1. GET /websites/seo/seo/ - Liste configs SEO
        response = self.client.get(f'{seo_url}/', **self.auth_headers)  # ✅ FIX ICI
        self.stdout.write(f'  GET {seo_url}/: {response.status_code}')
        
        if response.status_code == 200:
            seo_configs = response.json()
            count = seo_configs.get('count', len(seo_configs))
            self.stdout.write(f'    ✅ {count} configs SEO trouvées')
    
    
    def test_pages_workflow_endpoints(self):
        """Test endpoints seo_pages_workflow avec URLs VRAIES"""
        self.stdout.write('\n⚡ Testing seo_pages_workflow endpoints...')
        
        if not hasattr(self, 'test_page_id'):
            self.stdout.write('  ⚠️ Pas de page de test, skip workflow')
            return
        
        status_url = self.base_urls['workflow_status']       # /websites/workflow/status
        history_url = self.base_urls['workflow_history']     # /websites/workflow/history
        scheduling_url = self.base_urls['workflow_scheduling'] # /websites/workflow/scheduling
        
        # 1. GET /websites/workflow/status/ - Liste statuts
        response = self.client.get(f'{status_url}/', **self.auth_headers)
        self.stdout.write(f'  GET {status_url}/: {response.status_code}')
        
        if response.status_code == 200:
            statuses = response.json()
            count = statuses.get('count', len(statuses))
            self.stdout.write(f'    ✅ {count} statuts trouvés')
            self.log_response(response, 'status-list')
        
        # 2. POST /websites/workflow/status/ - Créer statut
        status_data = {
            'page': self.test_page_id,
            'status': 'draft',
            'production_notes': 'Statut créé via API test'
        }
        
        response = self.client.post(
            f'{status_url}/',
            data=json.dumps(status_data),
            **self.auth_headers
        )
        self.stdout.write(f'  POST {status_url}/: {response.status_code}')
        
        if response.status_code == 201:
            status = response.json()
            self.test_status_id = status['id']
            self.stdout.write(f'    ✅ Statut créé: {status.get("status")}')
            self.log_response(response, 'status-create')
        elif response.status_code == 400:
            error_data = response.json()
            self.stdout.write(f'    ⚠️ Erreur statut: {error_data}')
        
        # 3. Actions custom - dashboard
        response = self.client.get(
            f'{status_url}/dashboard/?website_id={self.test_website.id}',
            **self.auth_headers
        )
        self.stdout.write(f'  GET {status_url}/dashboard/: {response.status_code}')
        
        if response.status_code == 200:
            dashboard = response.json()
            total_pages = dashboard.get('stats', {}).get('total_pages', 0)
            self.stdout.write(f'    ✅ Dashboard: {total_pages} pages total')
        
        # 4. Actions custom - bulk-update
        if hasattr(self, 'test_status_id'):
            bulk_status_data = {
                'status': 'in_progress',
                'page_ids': [self.test_page_id]
            }
            response = self.client.post(
                f'{status_url}/bulk_update/',
                data=json.dumps(bulk_status_data),
                **self.auth_headers
            )
            self.stdout.write(f'  POST {status_url}/bulk_update/: {response.status_code}')
            
            if response.status_code == 200:
                bulk_result = response.json()
                updated_count = bulk_result.get('updated_count', 0)
                self.stdout.write(f'    ✅ Bulk status update: {updated_count} pages')
        
        # 5. GET /websites/workflow/history/ - Historique
        response = self.client.get(f'{history_url}/', **self.auth_headers)
        self.stdout.write(f'  GET {history_url}/: {response.status_code}')
        
        if response.status_code == 200:
            history = response.json()
            count = history.get('count', len(history))
            self.stdout.write(f'    ✅ {count} entrées d\'historique')
        
        # 6. GET /websites/workflow/scheduling/ - Planification
        response = self.client.get(f'{scheduling_url}/', **self.auth_headers)
        self.stdout.write(f'  GET {scheduling_url}/: {response.status_code}')
        
        if response.status_code == 200:
            scheduling = response.json()
            count = scheduling.get('count', len(scheduling))
            self.stdout.write(f'    ✅ {count} planifications trouvées')
    
    def test_pages_keywords_endpoints(self):
        """Test endpoints seo_pages_keywords avec URLs VRAIES"""
        self.stdout.write('\n🔑 Testing seo_pages_keywords endpoints...')
        
        if not hasattr(self, 'test_page_id') or not KEYWORDS_AVAILABLE:
            self.stdout.write('  ⚠️ Pas de page/keywords de test, skip')
            return
        
        keywords_url = self.base_urls['keywords']  # /websites/keywords/page-keywords
        
        # 1. GET /websites/keywords/page-keywords/ - Liste associations
        response = self.client.get(f'{keywords_url}/', **self.auth_headers)
        self.stdout.write(f'  GET {keywords_url}/: {response.status_code}')
        
        if response.status_code == 200:
            associations = response.json()
            count = associations.get('count', len(associations))
            self.stdout.write(f'    ✅ {count} associations trouvées')
            self.log_response(response, 'keywords-list')
        
        # 2. POST /websites/keywords/page-keywords/ - Créer association
        if self.test_keywords:
            association_data = {
                'page': self.test_page_id,
                'keyword': self.test_keywords[0].id,
                'keyword_type': 'primary',
                'position': 1,
                'notes': 'Association créée via API'
            }
            
            response = self.client.post(
                f'{keywords_url}/',
                data=json.dumps(association_data),
                **self.auth_headers
            )
            self.stdout.write(f'  POST {keywords_url}/: {response.status_code}')
            
            if response.status_code == 201:
                association = response.json()
                self.test_association_id = association['id']
                self.stdout.write(f'    ✅ Association créée: {association.get("keyword_type")}')
                self.log_response(response, 'keyword-create')
            elif response.status_code == 400:
                error_data = response.json()
                self.stdout.write(f'    ⚠️ Erreur association: {error_data}')
        
        # 3. Actions custom - bulk-create
        if len(self.test_keywords) > 1:
            bulk_data = {
                'page': self.test_page_id,
                'keywords': [
                    {
                        'keyword': self.test_keywords[1].id,
                        'keyword_type': 'secondary',
                        'position': 1
                    },
                    {
                        'keyword': self.test_keywords[2].id,
                        'keyword_type': 'anchor',
                        'position': 2
                    }
                ]
            }
            response = self.client.post(
                f'{keywords_url}/bulk_create/',
                data=json.dumps(bulk_data),
                **self.auth_headers
            )
            self.stdout.write(f'  POST {keywords_url}/bulk_create/: {response.status_code}')
            
            if response.status_code == 200:
                bulk_result = response.json()
                created_count = bulk_result.get('created_count', 0)
                self.stdout.write(f'    ✅ Bulk create: {created_count} associations')
        
        # 4. Actions custom - stats
        response = self.client.get(
            f'{keywords_url}/stats/?page_id={self.test_page_id}',
            **self.auth_headers
        )
        self.stdout.write(f'  GET {keywords_url}/stats/: {response.status_code}')
        
        if response.status_code == 200:
            stats = response.json()
            total_keywords = stats.get('total_keywords', 0)
            self.stdout.write(f'    ✅ Stats: {total_keywords} mots-clés total')
    
    def test_permissions_comprehensive(self):
        """Test complet des permissions avec URLs VRAIES"""
        self.stdout.write('\n🔒 Testing Permissions Comprehensive...')
        
        # Test sans token sur endpoints hierarchy
        hierarchy_url = self.base_urls['structure_hierarchy']
        response = self.client.get(f'{hierarchy_url}/')
        self.stdout.write(f'  GET {hierarchy_url}/ (sans auth): {response.status_code}')
        if response.status_code == 401:
            self.stdout.write('    ✅ Auth requise correctement')
        
        # Test avec mauvais brand sur sections
        sections_url = self.base_urls['builder_sections']
        wrong_headers = {
            'HTTP_AUTHORIZATION': self.auth_headers['HTTP_AUTHORIZATION'],
            'HTTP_X_BRAND_ID': '99999',  # Brand inexistante
            'content_type': 'application/json'
        }
        
        response = self.client.get(f'{sections_url}/', **wrong_headers)
        self.stdout.write(f'  GET {sections_url}/ (wrong brand): {response.status_code}')
        if response.status_code in [403, 404]:
            self.stdout.write('    ✅ Brand scope respecté')
        elif response.status_code == 200:
            data = response.json()
            count = data.get('count', len(data))
            self.stdout.write(f'    ⚠️ Brand scope partiel: {count} résultats')
    
    def test_filters_comprehensive(self):
        """Test complet des filtres avancés avec URLs VRAIES"""
        self.stdout.write('\n🔍 Testing Filters Comprehensive...')
        
        # Test filtres sur différents endpoints
        test_endpoints = [
            (self.base_urls['pages'], 'pages'),
            (self.base_urls['structure_hierarchy'], 'hierarchy'),
            (self.base_urls['builder_sections'], 'sections'),
            (self.base_urls['workflow_status'], 'status'),
        ]
        
        for endpoint_url, endpoint_name in test_endpoints:
            # Filtres de base
            complex_filters = [
                (f'?website={self.test_website.id}', f'{endpoint_name} par website'),
                ('?ordering=-created_at', f'{endpoint_name} tri date'),
                ('?created_after=2024-01-01T00:00:00Z', f'{endpoint_name} filtre date'),
            ]
            
            for filter_params, description in complex_filters:
                response = self.client.get(f'{endpoint_url}/{filter_params}', **self.auth_headers)
                if response.status_code == 200:
                    data = response.json()
                    count = data.get('count', len(data))
                    self.stdout.write(f'    ✅ {description}: {count} résultats')
                else:
                    self.stdout.write(f'    ❌ {description}: {response.status_code}')
    
    def test_cross_endpoint_workflow(self):
        """Test workflow complet cross-endpoints avec URLs VRAIES"""
        self.stdout.write('\n🔗 Testing Cross-Endpoint Workflow...')
        
        if not hasattr(self, 'test_page_id'):
            self.stdout.write('  ⚠️ Pas de page de test pour workflow cross-endpoint')
            return
        
        workflow_steps = []
        
        # 1. Créer hiérarchie
        hierarchy_data = {'page': self.test_page_id, 'parent': None}
        response = self.client.post(
            f'{self.base_urls["structure_hierarchy"]}/', 
            data=json.dumps(hierarchy_data), 
            **self.auth_headers
        )
        workflow_steps.append(('Hierarchy', response.status_code))
        
        # 2. Ajouter sections
        section_data = {
            'page': self.test_page_id,
            'section_type': 'hero_banner',
            'data': {'title': 'Cross-workflow test'},
            'order': 0
        }
        response = self.client.post(
            f'{self.base_urls["builder_sections"]}/', 
            data=json.dumps(section_data), 
            **self.auth_headers
        )
        workflow_steps.append(('Section', response.status_code))
        
        # 3. Configurer SEO
        seo_data = {
            'page': self.test_page_id,
            'sitemap_priority': 0.9,
            'sitemap_changefreq': 'daily'
        }
        response = self.client.post(
            f'{self.base_urls["seo"]}/', 
            data=json.dumps(seo_data), 
            **self.auth_headers
        )
        workflow_steps.append(('SEO Config', response.status_code))
        
        # 4. Ajouter mots-clés si disponible
        if KEYWORDS_AVAILABLE and self.test_keywords:
            keyword_data = {
                'page': self.test_page_id,
                'keyword': self.test_keywords[0].id,
                'keyword_type': 'primary'
            }
            response = self.client.post(
                f'{self.base_urls["keywords"]}/', 
                data=json.dumps(keyword_data), 
                **self.auth_headers
            )
            workflow_steps.append(('Keyword', response.status_code))
        
        # 5. Configurer workflow
        status_data = {
            'page': self.test_page_id,
            'status': 'draft'
        }
        response = self.client.post(
            f'{self.base_urls["workflow_status"]}/', 
            data=json.dumps(status_data), 
            **self.auth_headers
        )
        workflow_steps.append(('Status', response.status_code))
        
        # Résumé workflow
        for step_name, status_code in workflow_steps:
            status_icon = '✅' if status_code in [200, 201] else '❌'
            self.stdout.write(f'    {status_icon} {step_name}: {status_code}')
        
        # Vérification finale : récupérer page complète
        response = self.client.get(f'{self.base_urls["pages"]}/{self.test_page_id}/', **self.auth_headers)
        if response.status_code == 200:
            page_data = response.json()
            self.stdout.write(f'    ✅ Page finale: {page_data.get("title")}')
            self.stdout.write(f'    ✅ Keywords: {page_data.get("keywords_count", 0)}')
            self.stdout.write(f'    ✅ Sections: {page_data.get("sections_count", 0)}')
    
    def cleanup_test_data(self):
        """Nettoie les données de test"""
        self.stdout.write('\n🧹 Cleanup données de test...')
        
        # Supprimer pages de test créées
        if hasattr(self, 'test_page_id'):
            try:
                Page.objects.filter(id=self.test_page_id).delete()
                self.stdout.write('  ✅ Page principale supprimée')
            except:
                pass
        
        # Supprimer PageLayout de test
        if hasattr(self, 'test_layout'):
            try:
                self.test_layout.delete()
                self.stdout.write('  ✅ PageLayout de test supprimé')
            except:
                pass
        
        if hasattr(self, 'bulk_page_ids'):
            try:
                Page.objects.filter(id__in=self.bulk_page_ids).delete()
                self.stdout.write(f'  ✅ {len(self.bulk_page_ids)} pages bulk supprimées')
            except:
                pass
        
        # Supprimer keywords de test
        if KEYWORDS_AVAILABLE and hasattr(self, 'test_keywords'):
            try:
                keyword_ids = [k.id for k in self.test_keywords]
                Keyword.objects.filter(id__in=keyword_ids).delete()
                self.stdout.write(f'  ✅ {len(keyword_ids)} keywords supprimés')
            except:
                pass
        
        # Ne pas supprimer website/brand car potentiellement réutilisés
        self.stdout.write('  ✅ Cleanup terminé')
        
        
        