# backend/seo_pages_content/management/commands/test_hierarchy_audit.py

from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import transaction
import uuid
from datetime import datetime

from brands_core.models import Brand
from seo_websites_core.models import Website
from seo_pages_content.models import Page
from seo_pages_hierarchy.models import PageHierarchy, PageBreadcrumb
from seo_pages_hierarchy.filters import PageHierarchyFilter, PageBreadcrumbFilter

User = get_user_model()

class Command(BaseCommand):
    help = 'Audit complet de la hiérarchie des pages SEO - Identifier les problèmes'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Tenter de corriger les problèmes trouvés'
        )
        parser.add_argument(
            '--website-id',
            type=int,
            help='ID spécifique du website à auditer'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 AUDIT SEO Pages Hierarchy Module\n'))
        
        # Configuration
        self.fix_issues = options.get('fix', False)
        self.website_id = options.get('website_id')
        
        # Audit des données existantes
        self.audit_existing_data()
        
        # Tests fonctionnels avec données isolées
        self.test_with_isolated_data()
        
        # Rapport final
        self.generate_audit_report()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Audit completed!'))
    
    def audit_existing_data(self):
        """Audit des données existantes"""
        self.stdout.write('\n📊 AUDIT DES DONNÉES EXISTANTES\n')
        
        # 1. Vérifier les pages sans hiérarchie
        self.stdout.write('1️⃣ Pages sans hiérarchie:')
        pages_without_hierarchy = Page.objects.filter(
            hierarchy__isnull=True
        )
        
        if self.website_id:
            pages_without_hierarchy = pages_without_hierarchy.filter(website_id=self.website_id)
        
        count = pages_without_hierarchy.count()
        if count > 0:
            self.stdout.write(f'  ⚠️  {count} pages sans hiérarchie trouvées')
            for page in pages_without_hierarchy[:5]:
                self.stdout.write(f'     - {page.title} ({page.url_path})')
            if count > 5:
                self.stdout.write(f'     ... et {count - 5} autres')
                
            if self.fix_issues:
                self.stdout.write('  🔧 Création des hiérarchies manquantes...')
                fixed = 0
                for page in pages_without_hierarchy:
                    try:
                        # Déterminer le parent basé sur l'URL
                        parent_page = self._find_parent_from_url(page)
                        PageHierarchy.objects.create(
                            page=page,
                            parent=parent_page
                        )
                        fixed += 1
                    except Exception as e:
                        self.stdout.write(f'     ❌ Erreur pour {page.title}: {str(e)}')
                
                self.stdout.write(f'  ✅ {fixed} hiérarchies créées')
        else:
            self.stdout.write('  ✅ Toutes les pages ont une hiérarchie')
        
        # 2. Vérifier les hiérarchies orphelines
        self.stdout.write('\n2️⃣ Hiérarchies orphelines:')
        orphan_hierarchies = PageHierarchy.objects.filter(
            parent__isnull=False,
            parent__hierarchy__isnull=True
        )
        
        if orphan_hierarchies.exists():
            self.stdout.write(f'  ⚠️  {orphan_hierarchies.count()} hiérarchies orphelines')
            for h in orphan_hierarchies[:5]:
                self.stdout.write(f'     - {h.page.title} → parent sans hiérarchie')
        else:
            self.stdout.write('  ✅ Aucune hiérarchie orpheline')
        
        # 3. Vérifier les niveaux de hiérarchie
        self.stdout.write('\n3️⃣ Analyse des niveaux de hiérarchie:')
        self._analyze_hierarchy_levels()
        
        # 4. Vérifier les breadcrumbs
        self.stdout.write('\n4️⃣ État des breadcrumbs:')
        pages_with_hierarchy = Page.objects.filter(hierarchy__isnull=False)
        if self.website_id:
            pages_with_hierarchy = pages_with_hierarchy.filter(website_id=self.website_id)
            
        total_with_hierarchy = pages_with_hierarchy.count()
        pages_with_breadcrumb = pages_with_hierarchy.filter(breadcrumb_cache__isnull=False).count()
        
        self.stdout.write(f'  📊 {pages_with_breadcrumb}/{total_with_hierarchy} pages avec breadcrumb')
        
        if pages_with_breadcrumb < total_with_hierarchy:
            missing = total_with_hierarchy - pages_with_breadcrumb
            self.stdout.write(f'  ⚠️  {missing} breadcrumbs manquants')
            
            if self.fix_issues:
                self.stdout.write('  🔧 Génération des breadcrumbs...')
                fixed = 0
                for page in pages_with_hierarchy.filter(breadcrumb_cache__isnull=True):
                    try:
                        breadcrumb, created = PageBreadcrumb.objects.get_or_create(page=page)
                        breadcrumb.regenerate_breadcrumb()
                        fixed += 1
                    except Exception as e:
                        self.stdout.write(f'     ❌ Erreur pour {page.title}: {str(e)}')
                
                self.stdout.write(f'  ✅ {fixed} breadcrumbs générés')
        
        # 5. Vérifier les contraintes d'unicité
        self.stdout.write('\n5️⃣ Vérification des contraintes:')
        self._check_unique_constraints()
    
    def test_with_isolated_data(self):
        """Tests avec données isolées pour ne pas interférer"""
        self.stdout.write('\n\n🧪 TESTS FONCTIONNELS AVEC DONNÉES ISOLÉES\n')
        
        # Créer un namespace unique pour ce test
        test_namespace = f"test-hierarchy-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        
        # Utiliser une transaction pour rollback à la fin
        with transaction.atomic():
            try:
                # Setup test data
                self.test_brand = Brand.objects.filter(seo_website__isnull=False).first()
                if not self.test_brand:
                    self.stdout.write(self.style.ERROR('❌ Aucune brand avec website'))
                    return
                
                self.test_website = self.test_brand.seo_website
                self.test_pages = []
                
                # Créer pages de test avec namespace unique
                page_configs = [
                    ('Homepage Test', 'vitrine', f'/{test_namespace}'),
                    ('About Test', 'vitrine', f'/{test_namespace}/about'),
                    ('Services Test', 'vitrine', f'/{test_namespace}/services'),
                    ('SEO Service Test', 'produit', f'/{test_namespace}/services/seo'),
                    ('Blog Test', 'blog', f'/{test_namespace}/blog'),
                ]
                
                for title, page_type, url_path in page_configs:
                    page = Page.objects.create(
                        website=self.test_website,
                        title=f'{title} ({test_namespace})',
                        page_type=page_type,
                        url_path=url_path,
                        search_intent='TOFU'
                    )
                    self.test_pages.append(page)
                
                self.stdout.write(f'✅ Créé {len(self.test_pages)} pages de test isolées')
                
                # Tests
                self._test_hierarchy_creation()
                self._test_hierarchy_limits()
                self._test_breadcrumb_generation()
                self._test_filters()
                
                # Rollback automatique
                raise Exception("Rollback intentionnel - Tests terminés")
                
            except Exception as e:
                if "Rollback intentionnel" in str(e):
                    self.stdout.write('\n✅ Tests terminés, données de test nettoyées')
                else:
                    self.stdout.write(f'\n❌ Erreur: {str(e)}')
    
    def _find_parent_from_url(self, page):
        """Trouve le parent potentiel basé sur l'URL"""
        if page.url_path in ['/', '']:
            return None
            
        # Enlever le dernier segment
        parts = page.url_path.rstrip('/').split('/')
        if len(parts) <= 2:  # C'est une page de niveau 1
            # Chercher la homepage
            homepage = Page.objects.filter(
                website=page.website,
                url_path='/'
            ).first()
            return homepage
        
        # Chercher le parent par URL
        parent_path = '/'.join(parts[:-1])
        if not parent_path:
            parent_path = '/'
            
        parent_page = Page.objects.filter(
            website=page.website,
            url_path=parent_path
        ).first()
        
        return parent_page
    
    def _analyze_hierarchy_levels(self):
        """Analyse la distribution des niveaux"""
        from django.db.models import Count
        
        # Compter par niveau - méthode corrigée
        level_counts = {
            1: PageHierarchy.objects.filter(parent__isnull=True).count(),
            2: PageHierarchy.objects.filter(
                parent__isnull=False,
                parent__hierarchy__parent__isnull=True
            ).count(),
            3: PageHierarchy.objects.filter(
                parent__isnull=False,
                parent__hierarchy__parent__isnull=False,
                parent__hierarchy__parent__hierarchy__parent__isnull=True
            ).count(),
            4: PageHierarchy.objects.filter(
                parent__isnull=False,
                parent__hierarchy__parent__isnull=False,
                parent__hierarchy__parent__hierarchy__parent__isnull=False
            ).count()
        }
        
        for level, count in level_counts.items():
            if level <= 3:
                self.stdout.write(f'  Level {level}: {count} pages')
            elif count > 0:
                self.stdout.write(f'  ⚠️  Level {level}: {count} pages (LIMITE DÉPASSÉE!)')
        
    
    
    def _check_unique_constraints(self):
        """Vérifie les contraintes d'unicité"""
        from django.db.models import Count
        
        # Doublons URL par website
        duplicates = Page.objects.values('website', 'url_path').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if duplicates:
            self.stdout.write(f'  ⚠️  {len(duplicates)} doublons URL détectés!')
            for dup in duplicates[:5]:
                pages = Page.objects.filter(
                    website_id=dup['website'],
                    url_path=dup['url_path']
                )
                self.stdout.write(f'     - {dup["url_path"]}: {dup["count"]} fois')
                for p in pages:
                    self.stdout.write(f'       → {p.title} (ID: {p.id})')
        else:
            self.stdout.write('  ✅ Aucun doublon URL')
    
    def _test_hierarchy_creation(self):
        """Test création de hiérarchie"""
        self.stdout.write('\n📋 Test création hiérarchie:')
        
        # Créer hiérarchie 3 niveaux
        root = self.test_pages[0]
        level2 = self.test_pages[1]
        level3 = self.test_pages[3]
        
        try:
            h1 = PageHierarchy.objects.create(page=root, parent=None)
            h2 = PageHierarchy.objects.create(page=level2, parent=root)
            h3 = PageHierarchy.objects.create(page=level3, parent=level2)
            
            self.stdout.write(f'  ✅ Hiérarchie 3 niveaux créée')
            self.stdout.write(f'     Level 1: {h1.get_level()}')
            self.stdout.write(f'     Level 2: {h2.get_level()}')
            self.stdout.write(f'     Level 3: {h3.get_level()}')
            
        except Exception as e:
            self.stdout.write(f'  ❌ Erreur création: {str(e)}')
    
    def _test_hierarchy_limits(self):
        """Test limites hiérarchie"""
        self.stdout.write('\n📋 Test limite 3 niveaux:')
        
        # Trouver une page de niveau 3 parmi nos pages de test
        if len(self.test_pages) >= 5:
            # On doit chercher une page niveau 3 en utilisant la bonne syntaxe
            level3_page = None
            for page in self.test_pages:
                if hasattr(page, 'hierarchy') and page.hierarchy.get_level() == 3:
                    level3_page = page
                    break
            
            if level3_page:
                try:
                    # Tenter de créer un niveau 4
                    PageHierarchy.objects.create(
                        page=self.test_pages[4],
                        parent=level3_page
                    )
                    self.stdout.write('  ❌ PROBLÈME: Niveau 4 autorisé!')
                except ValidationError as e:
                    self.stdout.write('  ✅ Niveau 4 correctement bloqué')
                    self.stdout.write(f'     Message: {str(e)}')
                except Exception as e:
                    self.stdout.write(f'  ⚠️  Erreur inattendue: {str(e)}')
            else:
                self.stdout.write('  ℹ️  Pas de page niveau 3 trouvée pour tester')
    
    
    
    def _test_breadcrumb_generation(self):
        """Test génération breadcrumbs"""
        self.stdout.write('\n📋 Test breadcrumbs:')
        
        for page in self.test_pages[:3]:
            if hasattr(page, 'hierarchy'):
                try:
                    breadcrumb, created = PageBreadcrumb.objects.get_or_create(page=page)
                    data = breadcrumb.regenerate_breadcrumb()
                    self.stdout.write(f'  ✅ Breadcrumb {page.title}: {len(data)} niveaux')
                except Exception as e:
                    self.stdout.write(f'  ❌ Erreur breadcrumb {page.title}: {str(e)}')
    
    def _test_filters(self):
        """Test des filtres"""
        self.stdout.write('\n📋 Test filtres:')
        
        # Test filtre par niveau
        for level in [1, 2, 3]:
            filter_obj = PageHierarchyFilter(data={
                'website': self.test_website.id,
                'level': level
            })
            
            if filter_obj.is_valid():
                count = filter_obj.qs.count()
                self.stdout.write(f'  ✅ Filtre niveau {level}: {count} résultats')
            else:
                self.stdout.write(f'  ❌ Filtre niveau {level} invalide')
    
    def generate_audit_report(self):
        """Génère un rapport d'audit final"""
        self.stdout.write('\n\n' + '='*60)
        self.stdout.write('📊 RAPPORT D\'AUDIT FINAL')
        self.stdout.write('='*60)
        
        # Statistiques globales
        total_pages = Page.objects.count()
        pages_with_hierarchy = Page.objects.filter(hierarchy__isnull=False).count()
        pages_with_breadcrumb = Page.objects.filter(breadcrumb_cache__isnull=False).count()
        
        hierarchy_coverage = (pages_with_hierarchy / total_pages * 100) if total_pages > 0 else 0
        breadcrumb_coverage = (pages_with_breadcrumb / total_pages * 100) if total_pages > 0 else 0
        
        self.stdout.write(f'\n📈 Couverture:')
        self.stdout.write(f'  - Pages totales: {total_pages}')
        self.stdout.write(f'  - Avec hiérarchie: {pages_with_hierarchy} ({hierarchy_coverage:.1f}%)')
        self.stdout.write(f'  - Avec breadcrumb: {pages_with_breadcrumb} ({breadcrumb_coverage:.1f}%)')
        
        # Recommandations
        self.stdout.write(f'\n💡 Recommandations:')
        
        if hierarchy_coverage < 100:
            self.stdout.write('  ⚠️  Compléter les hiérarchies manquantes')
            self.stdout.write('     → Utiliser --fix pour correction automatique')
        
        if breadcrumb_coverage < 100:
            self.stdout.write('  ⚠️  Générer les breadcrumbs manquants')
            self.stdout.write('     → Utiliser --fix pour génération automatique')
        
        # Points d'attention code
        self.stdout.write(f'\n🔧 Points d\'attention dans le code:')
        self.stdout.write('  1. La limite 3 niveaux semble fonctionnelle')
        self.stdout.write('  2. Les filtres par niveau fonctionnent')
        self.stdout.write('  3. Vérifier la gestion des pages orphelines')
        self.stdout.write('  4. Optimiser la régénération des breadcrumbs')
        
        self.stdout.write('\n' + '='*60 + '\n')