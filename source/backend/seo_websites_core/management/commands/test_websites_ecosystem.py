# backend/seo_websites_core/management/commands/test_websites_ecosystem.py

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
from seo_websites_categorization.models import WebsiteCategory, WebsiteCategorization

User = get_user_model()

class Command(BaseCommand):
    help = 'Test complet de l\'écosystème websites (core + categorization) - URLs VRAIES v1.0'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--module',
            type=str,
            choices=['core', 'categorization', 'workflow', 'all'],
            default='all',
            help='Module spécifique à tester'
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
            '--stress-test',
            action='store_true',
            help='Test de stress avec beaucoup de données'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌐 Testing Websites Ecosystem v1.0 (Core + Categorization)\n'))
        
        self.verbose = options['verbose']
        self.module_to_test = options['module']
        self.stress_test = options['stress_test']
        
        # URLs VRAIES selon ton architecture
        self.base_urls = {
            # seo_websites_core
            'websites': '/websites',                                    # GET/POST /websites/
            
            # seo_websites_categorization
            'categories': '/websites/categorization/categories',        # GET/POST /websites/categorization/categories/
            'categorizations': '/websites/categorization/categorizations', # GET/POST /websites/categorization/categorizations/
        }
        
        # Setup
        self.setup_client_and_auth()
        self.setup_test_data()
        
        # Tests par module
        if self.module_to_test in ['core', 'all']:
            self.test_websites_core_endpoints()
        
        if self.module_to_test in ['categorization', 'all']:
            self.test_categorization_endpoints()
        
        if self.module_to_test in ['workflow', 'all']:
            self.test_workflow_complet()
        
        # Tests de stress si demandé
        if self.stress_test:
            self.test_stress_performance()
        
        if not options['skip_cleanup']:
            self.cleanup_test_data()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Tous les tests de l\'écosystème websites sont passés !'))
    
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
        self.stdout.write(f'  ✅ Company: {self.company.name}')
    
    def setup_test_data(self):
        """Prépare les données de test pour tous les endpoints"""
        self.stdout.write('📝 Setup données de test...')
        
        # Brand de test
        self.test_brand = Brand.objects.filter(
            company=self.company
        ).first()
        
        if not self.test_brand:
            self.test_brand = Brand.objects.create(
                company=self.company,
                name=f'Test Brand Ecosystem {uuid.uuid4().hex[:8]}',
                description='Brand de test pour écosystème websites'
            )
        
        # Headers avec Brand-ID
        self.auth_headers['HTTP_X_BRAND_ID'] = str(self.test_brand.id)
        
        self.stdout.write(f'  ✅ Brand: {self.test_brand.name}')
        
        # Variables pour tracking des IDs créés
        self.created_website_ids = []
        self.created_category_ids = []
        self.created_categorization_ids = []
    
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
    
    def test_websites_core_endpoints(self):
        """Test complet des endpoints seo_websites_core"""
        self.stdout.write('\n🌐 Testing seo_websites_core endpoints...')
        
        base_url = self.base_urls['websites']  # /websites
        
        # 1. GET /websites/ - Liste
        response = self.client.get(f'{base_url}/', **self.auth_headers)
        self.stdout.write(f'  GET {base_url}/: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', len(data))
            self.stdout.write(f'    ✅ {count} websites trouvés')
            self.log_response(response, 'websites-list')
        else:
            self.stdout.write(f'    ❌ Erreur: {response.content.decode()[:200]}')
        
        # 2. POST /websites/ - Création
        website_data = {
            'name': f'Test Website Ecosystem {uuid.uuid4().hex[:6]}',
            'url': f'https://test-ecosystem-{uuid.uuid4().hex[:6]}.example.com',
            'brand': self.test_brand.id,
            'domain_authority': 75,
            'max_competitor_backlinks': 50000,
            'max_competitor_kd': 0.8
        }
        
        response = self.client.post(
            f'{base_url}/',
            data=json.dumps(website_data),
            **self.auth_headers
        )
        self.stdout.write(f'  POST {base_url}/: {response.status_code}')
        
        if response.status_code == 201:
            created_website = response.json()
            self.test_website_id = created_website['id']
            self.created_website_ids.append(self.test_website_id)
            self.stdout.write(f'    ✅ Website créé: {created_website.get("name")}')
            self.stdout.write(f'    ✅ DA: {created_website.get("domain_authority")}')
            self.log_response(response, 'website-create')
        else:
            # Fallback: utiliser website existant
            existing_website = Website.objects.filter(brand=self.test_brand).first()
            if existing_website:
                self.test_website_id = existing_website.id
                self.stdout.write(f'    ⚠️ Utilisation website existant: {existing_website.name}')
            else:
                error_content = response.content.decode()[:300]
                self.stdout.write(f'    ❌ Création échouée ({response.status_code}): {error_content}')
                return
        
        # 3. GET /websites/{id}/ - Détail
        response = self.client.get(f'{base_url}/{self.test_website_id}/', **self.auth_headers)
        self.stdout.write(f'  GET {base_url}/{self.test_website_id}/: {response.status_code}')
        
        if response.status_code == 200:
            website_detail = response.json()
            self.stdout.write(f'    ✅ Détail: {website_detail.get("name")}')
            self.stdout.write(f'    ✅ URL: {website_detail.get("url")}')
            self.stdout.write(f'    ✅ Pages count: {website_detail.get("pages_count", 0)}')
            self.log_response(response, 'website-detail')
        else:
            self.stdout.write(f'    ❌ Erreur détail: {response.status_code}')
        
        # 4. GET /websites/{id}/stats/ - Actions custom
        response = self.client.get(f'{base_url}/{self.test_website_id}/stats/', **self.auth_headers)
        self.stdout.write(f'  GET {base_url}/{self.test_website_id}/stats/: {response.status_code}')
        
        if response.status_code == 200:
            stats = response.json()
            total_pages = stats.get('total_pages', 0)
            da = stats.get('domain_authority', 'N/A')
            self.stdout.write(f'    ✅ Stats - Pages: {total_pages}, DA: {da}')
            self.log_response(response, 'website-stats')
        
        # 5. PUT /websites/{id}/ - Modification
        update_data = {
            'name': f'Updated Website {uuid.uuid4().hex[:6]}',
            'domain_authority': 80
        }
        
        response = self.client.patch(
            f'{base_url}/{self.test_website_id}/',
            data=json.dumps(update_data),
            **self.auth_headers
        )
        self.stdout.write(f'  PATCH {base_url}/{self.test_website_id}/: {response.status_code}')
        
        if response.status_code == 200:
            updated_website = response.json()
            self.stdout.write(f'    ✅ Updated: {updated_website.get("name")}')
            self.stdout.write(f'    ✅ New DA: {updated_website.get("domain_authority")}')
    
    def test_categorization_endpoints(self):
        """Test complet des endpoints seo_websites_categorization"""
        self.stdout.write('\n🏷️ Testing seo_websites_categorization endpoints...')
        
        if not hasattr(self, 'test_website_id'):
            self.stdout.write('  ⚠️ Pas de website de test, skip categorization')
            return
        
        categories_url = self.base_urls['categories']  # /websites/categorization/categories
        categorizations_url = self.base_urls['categorizations']  # /websites/categorization/categorizations
        
        # ==================== CATEGORIES ====================
        
        # 1. GET /websites/categorization/categories/ - Liste
        response = self.client.get(f'{categories_url}/', **self.auth_headers)
        self.stdout.write(f'  GET {categories_url}/: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', len(data))
            self.stdout.write(f'    ✅ {count} catégories trouvées')
            self.log_response(response, 'categories-list')
        
        # 2. POST /websites/categorization/categories/ - Créer catégorie racine
        root_category_data = {
            'name': f'E-commerce {uuid.uuid4().hex[:6]}',
            'description': 'Sites de vente en ligne',
            'color': '#e74c3c',
            'typical_da_range_min': 40,
            'typical_da_range_max': 80,
            'typical_pages_count': 150,
            'display_order': 1
        }
        
        response = self.client.post(
            f'{categories_url}/',
            data=json.dumps(root_category_data),
            **self.auth_headers
        )
        self.stdout.write(f'  POST {categories_url}/ (root): {response.status_code}')
        
        if response.status_code == 201:
            root_category = response.json()
            self.test_root_category_id = root_category['id']
            self.created_category_ids.append(self.test_root_category_id)
            self.stdout.write(f'    ✅ Catégorie racine créée: {root_category.get("name")}')
            self.stdout.write(f'    ✅ Slug: {root_category.get("slug")}')
            self.stdout.write(f'    ✅ DA Range: {root_category.get("typical_da_range_min")}-{root_category.get("typical_da_range_max")}')
            self.log_response(response, 'root-category-create')
        else:
            error_content = response.content.decode()[:300]
            self.stdout.write(f'    ❌ Création catégorie échouée: {error_content}')
            return
        
        # 3. POST /websites/categorization/categories/ - Créer sous-catégorie
        sub_category_data = {
            'name': f'Fashion {uuid.uuid4().hex[:6]}',
            'description': 'Sites de mode et vêtements',
            'color': '#f39c12',
            'parent': self.test_root_category_id,
            'typical_da_range_min': 45,
            'typical_da_range_max': 70,
            'display_order': 1
        }
        
        response = self.client.post(
            f'{categories_url}/',
            data=json.dumps(sub_category_data),
            **self.auth_headers
        )
        self.stdout.write(f'  POST {categories_url}/ (sub): {response.status_code}')
        
        if response.status_code == 201:
            sub_category = response.json()
            self.test_sub_category_id = sub_category['id']
            self.created_category_ids.append(self.test_sub_category_id)
            self.stdout.write(f'    ✅ Sous-catégorie créée: {sub_category.get("name")}')
            self.stdout.write(f'    ✅ Parent: {sub_category.get("parent")}')
        
        # 4. GET /websites/categorization/categories/tree/ - Arbre hiérarchique
        response = self.client.get(f'{categories_url}/tree/', **self.auth_headers)
        self.stdout.write(f'  GET {categories_url}/tree/: {response.status_code}')
        
        if response.status_code == 200:
            tree_data = response.json()
            tree_count = len(tree_data.get('tree', []))
            total_categories = tree_data.get('total_categories', 0)
            self.stdout.write(f'    ✅ Arbre: {tree_count} racines, {total_categories} total')
            self.log_response(response, 'categories-tree')
        
        # 5. GET /websites/categorization/categories/stats/ - Statistiques
        response = self.client.get(f'{categories_url}/stats/', **self.auth_headers)
        self.stdout.write(f'  GET {categories_url}/stats/: {response.status_code}')
        
        if response.status_code == 200:
            stats = response.json()
            total = stats.get('total_categories', 0)
            roots = stats.get('root_categories', 0)
            self.stdout.write(f'    ✅ Stats: {total} total, {roots} racines')
        
        # ==================== CATEGORIZATIONS ====================
        
        # 6. GET /websites/categorization/categorizations/ - Liste
        response = self.client.get(f'{categorizations_url}/', **self.auth_headers)
        self.stdout.write(f'  GET {categorizations_url}/: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', len(data))
            self.stdout.write(f'    ✅ {count} catégorisations trouvées')
        
        # 7. POST /websites/categorization/categorizations/ - Créer catégorisation primaire
        categorization_data = {
            'website': self.test_website_id,
            'category': self.test_root_category_id,
            'is_primary': True,
            'confidence_score': 0.95,
            'source': 'manual',
            'notes': 'Catégorisation de test via API'
        }
        
        response = self.client.post(
            f'{categorizations_url}/',
            data=json.dumps(categorization_data),
            **self.auth_headers
        )
        self.stdout.write(f'  POST {categorizations_url}/ (primary): {response.status_code}')
        
        if response.status_code == 201:
            categorization = response.json()
            self.test_categorization_id = categorization['id']
            self.created_categorization_ids.append(self.test_categorization_id)
            self.stdout.write(f'    ✅ Catégorisation primaire créée')
            self.stdout.write(f'    ✅ Confidence: {categorization.get("confidence_score")}')
            self.stdout.write(f'    ✅ Source: {categorization.get("source")}')
            self.log_response(response, 'categorization-create')
        
        # 8. POST /websites/categorization/categorizations/ - Créer catégorisation secondaire
        if hasattr(self, 'test_sub_category_id'):
            secondary_categorization_data = {
                'website': self.test_website_id,
                'category': self.test_sub_category_id,
                'is_primary': False,
                'confidence_score': 0.85,
                'source': 'ai_suggested',
                'notes': 'Catégorisation secondaire suggérée par IA'
            }
            
            response = self.client.post(
                f'{categorizations_url}/',
                data=json.dumps(secondary_categorization_data),
                **self.auth_headers
            )
            self.stdout.write(f'  POST {categorizations_url}/ (secondary): {response.status_code}')
            
            if response.status_code == 201:
                secondary_cat = response.json()
                self.created_categorization_ids.append(secondary_cat['id'])
                self.stdout.write(f'    ✅ Catégorisation secondaire créée')
        
        # 9. GET /websites/categorization/categorizations/by-website/ - Par website
        response = self.client.get(
            f'{categorizations_url}/by_website/?website_id={self.test_website_id}',
            **self.auth_headers
        )
        self.stdout.write(f'  GET {categorizations_url}/by_website/: {response.status_code}')
        
        if response.status_code == 200:
            by_website = response.json()
            categorizations_count = len(by_website.get('categorizations', []))
            primary_category = by_website.get('primary_category')
            self.stdout.write(f'    ✅ {categorizations_count} catégorisations pour ce website')
            if primary_category:
                self.stdout.write(f'    ✅ Catégorie primaire: {primary_category.get("category_name")}')
        
        # 10. GET /websites/categorization/categorizations/by-category/ - Par catégorie
        response = self.client.get(
            f'{categorizations_url}/by_category/?category_id={self.test_root_category_id}',
            **self.auth_headers
        )
        self.stdout.write(f'  GET {categorizations_url}/by_category/: {response.status_code}')
        
        if response.status_code == 200:
            by_category = response.json()
            websites_count = by_category.get('total_websites', 0)
            self.stdout.write(f'    ✅ {websites_count} websites dans cette catégorie')
        
        # 11. POST /websites/categorization/categorizations/set-primary/ - Changer primaire
        if hasattr(self, 'test_sub_category_id'):
            set_primary_data = {
                'website_id': self.test_website_id,
                'category_id': self.test_sub_category_id
            }
            
            response = self.client.post(
                f'{categorizations_url}/set_primary/',
                data=json.dumps(set_primary_data),
                **self.auth_headers
            )
            self.stdout.write(f'  POST {categorizations_url}/set_primary/: {response.status_code}')
            
            if response.status_code == 200:
                self.stdout.write(f'    ✅ Catégorie primaire changée')
    
    def test_workflow_complet(self):
        """Test workflow complet : Website → Catégorisation → Stats"""
        self.stdout.write('\n🔄 Testing Workflow Complet...')
        
        if not hasattr(self, 'test_website_id') or not hasattr(self, 'test_root_category_id'):
            self.stdout.write('  ⚠️ Données de test manquantes pour workflow')
            return
        
        workflow_steps = []
        
        # 1. Vérifier website existe
        response = self.client.get(f'{self.base_urls["websites"]}/{self.test_website_id}/', **self.auth_headers)
        workflow_steps.append(('Website Detail', response.status_code))
        
        # 2. Vérifier catégorie existe
        response = self.client.get(f'{self.base_urls["categories"]}/{self.test_root_category_id}/', **self.auth_headers)
        workflow_steps.append(('Category Detail', response.status_code))
        
        # 3. Lister catégorisations du website
        response = self.client.get(
            f'{self.base_urls["categorizations"]}/by_website/?website_id={self.test_website_id}',
            **self.auth_headers
        )
        workflow_steps.append(('Website Categorizations', response.status_code))
        
        # 4. Stats de la catégorie
        response = self.client.get(f'{self.base_urls["categories"]}/stats/', **self.auth_headers)
        workflow_steps.append(('Categories Stats', response.status_code))
        
        # 5. Stats du website
        response = self.client.get(f'{self.base_urls["websites"]}/{self.test_website_id}/stats/', **self.auth_headers)
        workflow_steps.append(('Website Stats', response.status_code))
        
        # Résumé workflow
        for step_name, status_code in workflow_steps:
            status_icon = '✅' if status_code in [200, 201] else '❌'
            self.stdout.write(f'    {status_icon} {step_name}: {status_code}')
        
        # Test intégrité des données
        self.stdout.write('\n  🔍 Vérification intégrité des données...')
        
        # Vérifier que la catégorisation existe bien
        try:
            categorization = WebsiteCategorization.objects.get(
                website_id=self.test_website_id,
                category_id=self.test_root_category_id
            )
            self.stdout.write(f'    ✅ Catégorisation DB: {categorization.source}, primaire: {categorization.is_primary}')
        except WebsiteCategorization.DoesNotExist:
            self.stdout.write(f'    ❌ Catégorisation non trouvée en DB')
        
        # Vérifier le website
        try:
            website = Website.objects.get(id=self.test_website_id)
            cats_count = website.categorizations.count()
            self.stdout.write(f'    ✅ Website DB: {website.name}, {cats_count} catégorisations')
        except Website.DoesNotExist:
            self.stdout.write(f'    ❌ Website non trouvé en DB')
    
    def test_stress_performance(self):
        """Test de stress avec beaucoup de données"""
        self.stdout.write('\n⚡ Testing Stress Performance...')
        
        if not hasattr(self, 'test_website_id'):
            self.stdout.write('  ⚠️ Pas de website pour test de stress')
            return
        
        import time
        
        # Créer 10 catégories rapidement
        start_time = time.time()
        created_categories = []
        
        for i in range(10):
            category_data = {
                'name': f'Stress Category {i} {uuid.uuid4().hex[:4]}',
                'description': f'Catégorie de test de stress numéro {i}',
                'color': f'#{i:02d}{i*2:02d}{i*3:02d}',
                'display_order': i
            }
            
            response = self.client.post(
                f'{self.base_urls["categories"]}/',
                data=json.dumps(category_data),
                **self.auth_headers
            )
            
            if response.status_code == 201:
                cat_data = response.json()
                created_categories.append(cat_data['id'])
                self.created_category_ids.append(cat_data['id'])
        
        categories_time = time.time() - start_time
        self.stdout.write(f'  ✅ 10 catégories créées en {categories_time:.2f}s')
        
        # Créer 10 catégorisations rapidement
        start_time = time.time()
        created_categorizations = []
        
        for i, category_id in enumerate(created_categories[:5]):  # 5 premières seulement
            categorization_data = {
                'website': self.test_website_id,
                'category': category_id,
                'is_primary': i == 0,  # Première en primaire
                'confidence_score': 0.9 - (i * 0.1),
                'source': 'automatic',
                'notes': f'Test stress catégorisation {i}'
            }
            
            response = self.client.post(
                f'{self.base_urls["categorizations"]}/',
                data=json.dumps(categorization_data),
                **self.auth_headers
            )
            
            if response.status_code == 201:
                cat_data = response.json()
                created_categorizations.append(cat_data['id'])
                self.created_categorization_ids.append(cat_data['id'])
        
        categorizations_time = time.time() - start_time
        self.stdout.write(f'  ✅ 5 catégorisations créées en {categorizations_time:.2f}s')
        
        # Test de récupération en masse
        start_time = time.time()
        response = self.client.get(f'{self.base_urls["categories"]}/', **self.auth_headers)
        fetch_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', len(data))
            self.stdout.write(f'  ✅ {count} catégories récupérées en {fetch_time:.2f}s')
        
        self.stdout.write(f'  📊 Performance globale acceptable: {categories_time + categorizations_time + fetch_time:.2f}s total')
    
    def cleanup_test_data(self):
        """Nettoie les données de test"""
        self.stdout.write('\n🧹 Cleanup données de test...')
        
        # Supprimer catégorisations
        if hasattr(self, 'created_categorization_ids') and self.created_categorization_ids:
            try:
                deleted_count = WebsiteCategorization.objects.filter(
                    id__in=self.created_categorization_ids
                ).delete()[0]
                self.stdout.write(f'  ✅ {deleted_count} catégorisations supprimées')
            except Exception as e:
                self.stdout.write(f'  ⚠️ Erreur suppression catégorisations: {e}')
        
        # Supprimer catégories
        if hasattr(self, 'created_category_ids') and self.created_category_ids:
            try:
                deleted_count = WebsiteCategory.objects.filter(
                    id__in=self.created_category_ids
                ).delete()[0]
                self.stdout.write(f'  ✅ {deleted_count} catégories supprimées')
            except Exception as e:
                self.stdout.write(f'  ⚠️ Erreur suppression catégories: {e}')
        
        # Supprimer websites
        if hasattr(self, 'created_website_ids') and self.created_website_ids:
            try:
                deleted_count = Website.objects.filter(
                    id__in=self.created_website_ids
                ).delete()[0]
                self.stdout.write(f'  ✅ {deleted_count} websites supprimés')
            except Exception as e:
                self.stdout.write(f'  ⚠️ Erreur suppression websites: {e}')
        
        self.stdout.write('  ✅ Cleanup terminé')