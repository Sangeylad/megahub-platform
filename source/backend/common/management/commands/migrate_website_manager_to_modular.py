# backend/common/management/commands/migrate_website_manager_to_modular.py

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
import logging

# Anciens modèles
from website_manager.models import Website as OldWebsite, Page as OldPage, PageKeyword as OldPageKeyword

# Nouveaux modèles
from seo_websites_core.models import Website, WebsiteSyncStatus
from seo_pages_content.models import Page, PageTemplate
from seo_pages_hierarchy.models import PageHierarchy, PageBreadcrumb
from seo_pages_keywords.models import PageKeyword
from seo_pages_layout.models import PageLayout, PageSection
from seo_pages_seo.models import PageSEO, PagePerformance
from seo_pages_workflow.models import PageStatus, PageWorkflowHistory, PageScheduling

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Migre les données de website_manager vers la nouvelle architecture modulaire'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulation sans sauvegarder en base',
        )
        parser.add_argument(
            '--brand-id',
            type=int,
            help='Migrer seulement une brand spécifique',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Affichage détaillé',
        )
    
    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.brand_id = options.get('brand_id')
        self.verbose = options['verbose']
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('🔍 MODE DRY-RUN - Aucune sauvegarde'))
        
        self.stdout.write(self.style.SUCCESS('🚀 Début migration website_manager → architecture modulaire'))
        
        try:
            with transaction.atomic():
                # 1. Migrer les websites
                self.migrate_websites()
                
                # 2. Migrer les pages (contenu principal)
                self.migrate_pages_content()
                
                # 3. Migrer la hiérarchie
                self.migrate_pages_hierarchy()
                
                # 4. Migrer les configurations SEO
                self.migrate_pages_seo()
                
                # 5. Migrer le workflow
                self.migrate_pages_workflow()
                
                # 6. Migrer les keywords
                self.migrate_page_keywords()
                
                # 7. Créer les configurations par défaut
                self.create_default_configs()
                
                if self.dry_run:
                    raise Exception("DRY-RUN: Rollback transaction")
                    
        except Exception as e:
            if "DRY-RUN" not in str(e):
                self.stdout.write(self.style.ERROR(f'❌ Erreur: {e}'))
                return
            else:
                self.stdout.write(self.style.SUCCESS('✅ DRY-RUN terminé avec succès'))
                return
        
        self.stdout.write(self.style.SUCCESS('🎉 Migration terminée avec succès !'))
    
    def migrate_websites(self):
        """Migre les websites vers seo_websites_core"""
        self.stdout.write('📊 Migration des websites...')
        
        # Filtre par brand si spécifié
        old_websites = OldWebsite.objects.all()
        if self.brand_id:
            old_websites = old_websites.filter(brand_id=self.brand_id)
        
        migrated_count = 0
        for old_website in old_websites:
            # Vérifier si déjà migré (par nom + brand)
            existing = Website.objects.filter(
                name=old_website.name,
                brand=old_website.brand
            ).first()
            
            if existing:
                if self.verbose:
                    self.stdout.write(f'  ⚠️ Website déjà migré: {old_website.name}')
                continue
            
            # Créer le nouveau website
            new_website = Website(
                name=old_website.name,
                url=old_website.url,
                brand=old_website.brand,
                domain_authority=old_website.domain_authority,
                max_competitor_backlinks=old_website.max_competitor_backlinks,
                max_competitor_kd=old_website.max_competitor_kd,
                created_at=old_website.created_at,
                updated_at=old_website.updated_at
            )
            
            if not self.dry_run:
                new_website.save()
            
            # Créer le statut de sync
            sync_status = WebsiteSyncStatus(
                website=new_website,
                last_openai_sync=old_website.last_openai_sync,
                openai_sync_version=old_website.openai_sync_version,
                created_at=old_website.created_at,
                updated_at=old_website.updated_at
            )
            
            if not self.dry_run:
                sync_status.save()
            
            migrated_count += 1
            if self.verbose:
                self.stdout.write(f'  ✅ Migré: {old_website.name}')
        
        self.stdout.write(f'📊 Websites migrés: {migrated_count}')
    
    def migrate_pages_content(self):
        """Migre le contenu des pages vers seo_pages_content"""
        self.stdout.write('📄 Migration du contenu des pages...')
        
        # Filtre par brand si spécifié
        old_pages = OldPage.objects.select_related('website', 'website__brand')
        if self.brand_id:
            old_pages = old_pages.filter(website__brand_id=self.brand_id)
        
        migrated_count = 0
        self.page_mapping = {}  # Pour traçabilité old_id → new_page
        
        for old_page in old_pages:
            # Trouver le nouveau website
            new_website = Website.objects.filter(
                name=old_page.website.name,
                brand=old_page.website.brand
            ).first()
            
            if not new_website:
                self.stdout.write(f'  ❌ Website non trouvé pour page: {old_page.title}')
                continue
            
            # Vérifier si déjà migré (par title + website)
            existing = Page.objects.filter(
                title=old_page.title,
                website=new_website
            ).first()
            
            if existing:
                self.page_mapping[old_page.id] = existing
                if self.verbose:
                    self.stdout.write(f'  ⚠️ Page déjà migrée: {old_page.title}')
                continue
            
            # Créer la nouvelle page (sans parent pour l'instant)
            new_page = Page(
                title=old_page.title,
                url_path=old_page.url_path,
                meta_description=old_page.meta_description,
                website=new_website,
                search_intent=old_page.search_intent,
                page_type=old_page.page_type,
                created_at=old_page.created_at,
                updated_at=old_page.updated_at
            )
            
            if not self.dry_run:
                new_page.save()
            
            # Stocker le mapping pour la hiérarchie
            self.page_mapping[old_page.id] = new_page
            
            migrated_count += 1
            if self.verbose:
                self.stdout.write(f'  ✅ Migré: {old_page.title}')
        
        self.stdout.write(f'📄 Pages migrées: {migrated_count}')
    
    def migrate_pages_hierarchy(self):
        """Migre la hiérarchie des pages vers seo_pages_hierarchy"""
        self.stdout.write('🌳 Migration de la hiérarchie...')
        
        old_pages = OldPage.objects.filter(parent__isnull=False)
        if self.brand_id:
            old_pages = old_pages.filter(website__brand_id=self.brand_id)
        
        migrated_count = 0
        for old_page in old_pages:
            if old_page.id not in self.page_mapping:
                continue
            
            new_page = self.page_mapping[old_page.id]
            
            # Trouver la page parent
            if old_page.parent and old_page.parent.id in self.page_mapping:
                parent_page = self.page_mapping[old_page.parent.id]
                
                # Créer la relation hiérarchique
                hierarchy = PageHierarchy(
                    page=new_page,
                    parent=parent_page,
                    created_at=old_page.created_at,
                    updated_at=old_page.updated_at
                )
                
                if not self.dry_run:
                    hierarchy.save()
                
                # Créer le cache breadcrumb
                breadcrumb = PageBreadcrumb(
                    page=new_page,
                    created_at=old_page.created_at,
                    updated_at=old_page.updated_at
                )
                
                if not self.dry_run:
                    breadcrumb.save()
                    breadcrumb.regenerate_breadcrumb()
                
                migrated_count += 1
                if self.verbose:
                    self.stdout.write(f'  ✅ Hiérarchie: {new_page.title} → {parent_page.title}')
        
        self.stdout.write(f'🌳 Hiérarchies migrées: {migrated_count}')
    
    def migrate_pages_seo(self):
        """Migre la configuration SEO vers seo_pages_seo"""
        self.stdout.write('🔍 Migration de la configuration SEO...')
        
        migrated_count = 0
        for old_page_id, new_page in self.page_mapping.items():
            old_page = OldPage.objects.get(id=old_page_id)
            
            # PageSEO
            page_seo = PageSEO(
                page=new_page,
                featured_image=old_page.featured_image,
                sitemap_priority=old_page.sitemap_priority,
                sitemap_changefreq=old_page.sitemap_changefreq,
                exclude_from_sitemap=old_page.exclude_from_sitemap,
                created_at=old_page.created_at,
                updated_at=old_page.updated_at
            )
            
            if not self.dry_run:
                page_seo.save()
            
            # PagePerformance
            page_performance = PagePerformance(
                page=new_page,
                last_rendered_at=old_page.last_rendered_at,
                created_at=old_page.created_at,
                updated_at=old_page.updated_at
            )
            
            if not self.dry_run:
                page_performance.save()
            
            migrated_count += 1
        
        self.stdout.write(f'🔍 Configurations SEO migrées: {migrated_count}')
    
    def migrate_pages_workflow(self):
        """Migre le workflow vers seo_pages_workflow"""
        self.stdout.write('🔄 Migration du workflow...')
        
        migrated_count = 0
        for old_page_id, new_page in self.page_mapping.items():
            old_page = OldPage.objects.get(id=old_page_id)
            
            # PageStatus
            page_status = PageStatus(
                page=new_page,
                status=old_page.status,
                status_changed_at=old_page.status_changed_at,
                status_changed_by=old_page.status_changed_by,
                production_notes=old_page.production_notes,
                created_at=old_page.created_at,
                updated_at=old_page.updated_at
            )
            
            if not self.dry_run:
                page_status.save()
            
            # PageScheduling (si schedulé)
            if old_page.scheduled_publish_date:
                page_scheduling = PageScheduling(
                    page=new_page,
                    scheduled_publish_date=old_page.scheduled_publish_date,
                    auto_publish=False,
                    created_at=old_page.created_at,
                    updated_at=old_page.updated_at
                )
                
                if not self.dry_run:
                    page_scheduling.save()
            
            migrated_count += 1
        
        self.stdout.write(f'🔄 Workflow migré: {migrated_count}')
    
    def migrate_page_keywords(self):
        """Migre les associations page-keywords vers seo_pages_keywords"""
        self.stdout.write('🔑 Migration des mots-clés...')
        
        # Import du nouveau modèle Keyword
        from seo_keywords_base.models import Keyword as NewKeyword
        
        old_page_keywords = OldPageKeyword.objects.select_related('page', 'keyword', 'source_cocoon')
        if self.brand_id:
            old_page_keywords = old_page_keywords.filter(page__website__brand_id=self.brand_id)
        
        migrated_count = 0
        errors_count = 0
        keywords_created = 0
        
        for old_pk in old_page_keywords:
            if old_pk.page.id not in self.page_mapping:
                errors_count += 1
                continue
            
            new_page = self.page_mapping[old_pk.page.id]
            
            # 🎯 RÉCUPÉRER LE TEXTE DU KEYWORD DEPUIS L'ANCIEN SYSTÈME
            keyword_text = old_pk.keyword.keyword  # Le texte du mot-clé
            
            # 🎯 TROUVER OU CRÉER LE KEYWORD DANS LE NOUVEAU SYSTÈME
            try:
                new_keyword, created = NewKeyword.objects.get_or_create(
                    keyword=keyword_text,
                    defaults={
                        'volume': old_pk.keyword.volume,
                        'search_intent': old_pk.keyword.search_intent,
                        'cpc': getattr(old_pk.keyword, 'cpc', None),
                        'youtube_videos': getattr(old_pk.keyword, 'youtube_videos', None),
                        'local_pack': getattr(old_pk.keyword, 'local_pack', False),
                        'content_types': getattr(old_pk.keyword, 'content_types', None),
                        'created_at': old_pk.keyword.created_at,
                        'updated_at': old_pk.keyword.updated_at,
                    }
                )
                
                if created:
                    keywords_created += 1
                    if self.verbose:
                        self.stdout.write(f'  ✨ Keyword créé: {keyword_text}')
                        
            except Exception as e:
                self.stdout.write(f'  ❌ Erreur création keyword "{keyword_text}": {e}')
                errors_count += 1
                continue
            
            # Vérifier si la relation existe déjà
            existing = PageKeyword.objects.filter(
                page=new_page,
                keyword=new_keyword  # 🎯 MAINTENANT ON UTILISE LE BON OBJET
            ).first()
            
            if existing:
                if self.verbose:
                    self.stdout.write(f'  ⚠️ Relation déjà migrée: {keyword_text} → {new_page.title}')
                continue
            
            # Créer la nouvelle association
            new_pk = PageKeyword(
                page=new_page,
                keyword=new_keyword,  # 🎯 BON OBJET KEYWORD
                position=old_pk.position,
                keyword_type=old_pk.keyword_type,
                source_cocoon=old_pk.source_cocoon,
                is_ai_selected=old_pk.is_ai_selected,
                notes=old_pk.notes,
                created_at=old_pk.created_at,
                updated_at=old_pk.updated_at
            )
            
            if not self.dry_run:
                try:
                    new_pk.save()
                    migrated_count += 1
                    if self.verbose:
                        self.stdout.write(f'  ✅ Relation migrée: {keyword_text} → {new_page.title}')
                except Exception as e:
                    errors_count += 1
                    self.stdout.write(f'  ❌ Erreur relation: {keyword_text} → {e}')
            else:
                migrated_count += 1
        
        self.stdout.write(f'🔑 Keywords migrés: {migrated_count}, nouveaux keywords: {keywords_created}, erreurs: {errors_count}')


    def migrate_keyword_metrics(self):
        """🆕 BONUS : Migrer aussi les métriques si elles existent"""
        self.stdout.write('📊 Migration des métriques keywords...')
        
        from seo_keywords_base.models import Keyword as NewKeyword
        from seo_keywords_metrics.models import KeywordMetrics
        from keyword_research.models import Keyword as OldKeyword
        
        # Récupérer tous les anciens keywords avec métriques
        old_keywords = OldKeyword.objects.filter(
            # Filtrer ceux qui ont des métriques
            da_min__isnull=False
        )
        
        if self.brand_id:
            # Filtrer par brand si on peut identifier les keywords utilisés
            old_keywords = old_keywords.filter(
                website_manager_page_keywords__page__website__brand_id=self.brand_id
            ).distinct()
        
        metrics_created = 0
        for old_kw in old_keywords:
            try:
                # Trouver le keyword correspondant dans le nouveau système
                new_keyword = NewKeyword.objects.filter(keyword=old_kw.keyword).first()
                if not new_keyword:
                    continue
                    
                # Créer les métriques si elles n'existent pas
                metrics, created = KeywordMetrics.objects.get_or_create(
                    keyword=new_keyword,
                    defaults={
                        'da_min': getattr(old_kw, 'da_min', None),
                        'da_max': getattr(old_kw, 'da_max', None),
                        'da_median': getattr(old_kw, 'da_median', None),
                        'da_q1': getattr(old_kw, 'da_q1', None),
                        'da_q3': getattr(old_kw, 'da_q3', None),
                        'bl_min': getattr(old_kw, 'bl_min', None),
                        'bl_max': getattr(old_kw, 'bl_max', None),
                        'bl_median': getattr(old_kw, 'bl_median', None),
                        'bl_q1': getattr(old_kw, 'bl_q1', None),
                        'bl_q3': getattr(old_kw, 'bl_q3', None),
                        'kdifficulty': getattr(old_kw, 'kdifficulty', None),
                        'created_at': old_kw.created_at,
                        'updated_at': old_kw.updated_at,
                    }
                )
                
                if created:
                    metrics_created += 1
                    if self.verbose:
                        self.stdout.write(f'  ✅ Métriques: {old_kw.keyword}')
                        
            except Exception as e:
                if self.verbose:
                    self.stdout.write(f'  ❌ Erreur métriques "{old_kw.keyword}": {e}')
        
        self.stdout.write(f'📊 Métriques créées: {metrics_created}')
    def create_default_configs(self):
        """Crée les configurations par défaut pour les nouvelles pages"""
        self.stdout.write('⚙️ Création des configurations par défaut...')
        
        layout_count = 0
        for new_page in self.page_mapping.values():
            # PageLayout par défaut
            if not hasattr(new_page, 'layout_config'):
                layout = PageLayout(
                    page=new_page,
                    render_strategy='sections',
                    layout_data={'sections': []},
                    created_at=timezone.now(),
                    updated_at=timezone.now()
                )
                
                if not self.dry_run:
                    layout.save()
                
                layout_count += 1
        
        self.stdout.write(f'⚙️ Configurations créées: {layout_count}')
    
    def log_migration_stats(self):
        """Affiche les statistiques de migration"""
        self.stdout.write('\n📊 STATISTIQUES DE MIGRATION:')
        
        if not self.dry_run:
            new_websites = Website.objects.count()
            new_pages = Page.objects.count()
            new_keywords = PageKeyword.objects.count()
            
            self.stdout.write(f'  - Websites: {new_websites}')
            self.stdout.write(f'  - Pages: {new_pages}')
            self.stdout.write(f'  - Keywords: {new_keywords}')