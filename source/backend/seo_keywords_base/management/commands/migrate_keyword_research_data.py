# backend/seo_keywords_base/management/commands/migrate_keyword_research_data.py

from django.core.management.base import BaseCommand
from django.db import transaction
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Migre toutes les données de keyword_research vers les 5 nouvelles apps SEO'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche ce qui serait migré sans effectuer la migration'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Taille des batches pour la migration (défaut: 1000)'
        )
    
    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.batch_size = options['batch_size']
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('🧪 MODE DRY-RUN - Aucune modification effectuée'))
        
        try:
            # Vérifier que l'ancienne app existe encore
            old_app = apps.get_app_config('keyword_research')
            self.stdout.write(f"✅ App source trouvée: {old_app.name}")
        except LookupError:
            self.stdout.write(self.style.ERROR('❌ App keyword_research introuvable'))
            return
        
        # Vérifier les nouvelles apps
        new_apps = [
            'seo_keywords_base',
            'seo_keywords_metrics', 
            'seo_keywords_cocoons',
            'seo_keywords_ppa',
            'seo_keywords_content_types'
        ]
        
        for app_name in new_apps:
            try:
                apps.get_app_config(app_name)
                self.stdout.write(f"✅ App cible trouvée: {app_name}")
            except LookupError:
                self.stdout.write(self.style.ERROR(f'❌ App {app_name} introuvable'))
                return
        
        if not self.dry_run:
            with transaction.atomic():
                self._migrate_all_data()
        else:
            self._analyze_migration()
    
    def _analyze_migration(self):
        """Analyse ce qui serait migré en mode dry-run"""
        from keyword_research.models import (
            Keyword, ContentType, KeywordContentType,
            SemanticCocoon, CocoonCategory, CocoonKeyword,
            PPA, KeywordPPA
        )
        
        # Compter les données source
        keywords_count = Keyword.objects.count()
        content_types_count = ContentType.objects.count()
        cocoons_count = SemanticCocoon.objects.count()
        categories_count = CocoonCategory.objects.count()
        ppas_count = PPA.objects.count()
        
        self.stdout.write(f"📊 ANALYSE DES DONNÉES À MIGRER:")
        self.stdout.write(f"   • Keywords: {keywords_count}")
        self.stdout.write(f"   • ContentTypes: {content_types_count}")
        self.stdout.write(f"   • SemanticCocoons: {cocoons_count}")
        self.stdout.write(f"   • CocoonCategories: {categories_count}")
        self.stdout.write(f"   • PPAs: {ppas_count}")
        
        # Analyser les métriques
        keywords_with_metrics = Keyword.objects.exclude(
            da_min__isnull=True, da_max__isnull=True, 
            bl_min__isnull=True, bl_max__isnull=True,
            kdifficulty__isnull=True
        ).count()
        
        self.stdout.write(f"   • Keywords avec métriques: {keywords_with_metrics}")
        
        # Analyser les associations
        keyword_content_associations = KeywordContentType.objects.count()
        cocoon_keyword_associations = CocoonKeyword.objects.count()
        keyword_ppa_associations = KeywordPPA.objects.count()
        
        self.stdout.write(f"   • Associations Keyword-ContentType: {keyword_content_associations}")
        self.stdout.write(f"   • Associations Cocoon-Keyword: {cocoon_keyword_associations}")
        self.stdout.write(f"   • Associations Keyword-PPA: {keyword_ppa_associations}")
    
    def _migrate_all_data(self):
        """Migration complète des données"""
        
        self.stdout.write(self.style.SUCCESS('🚀 DÉBUT DE LA MIGRATION'))
        
        # Ordre de migration (pour respecter les FK)
        migration_steps = [
            ('Keywords Base', self._migrate_keywords_base),
            ('Content Types', self._migrate_content_types),
            ('Keywords Metrics', self._migrate_keywords_metrics),
            ('Cocoon Categories', self._migrate_cocoon_categories),
            ('Semantic Cocoons', self._migrate_semantic_cocoons),
            ('PPAs', self._migrate_ppas),
            ('Keyword-ContentType Associations', self._migrate_keyword_content_type_associations),
            ('Cocoon-Keyword Associations', self._migrate_cocoon_keyword_associations),
            ('Keyword-PPA Associations', self._migrate_keyword_ppa_associations),
        ]
        
        for step_name, migration_func in migration_steps:
            self.stdout.write(f'\n📋 {step_name}...')
            try:
                count = migration_func()
                self.stdout.write(
                    self.style.SUCCESS(f'   ✅ {count} enregistrements migrés')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Erreur: {str(e)}')
                )
                raise
        
        self.stdout.write(self.style.SUCCESS('\n🎉 MIGRATION TERMINÉE AVEC SUCCÈS'))
    
    def _migrate_keywords_base(self):
        """Migre les keywords (données de base uniquement)"""
        from keyword_research.models import Keyword as OldKeyword
        from seo_keywords_base.models import Keyword as NewKeyword
        
        old_keywords = OldKeyword.objects.all()
        new_keywords = []
        
        for old_kw in old_keywords.iterator(chunk_size=self.batch_size):
            new_kw = NewKeyword(
                id=old_kw.id,  # Préserver les IDs pour les FK
                keyword=old_kw.keyword,
                volume=old_kw.volume,
                search_intent=old_kw.search_intent,
                cpc=old_kw.cpc,
                youtube_videos=old_kw.youtube_videos,
                local_pack=old_kw.local_pack,
                search_results=old_kw.search_results,
                content_types=old_kw.content_types,  # Legacy field
                created_at=old_kw.created_at,
                updated_at=old_kw.updated_at,
            )
            new_keywords.append(new_kw)
            
            if len(new_keywords) >= self.batch_size:
                NewKeyword.objects.bulk_create(new_keywords, ignore_conflicts=True)
                new_keywords = []
        
        if new_keywords:
            NewKeyword.objects.bulk_create(new_keywords, ignore_conflicts=True)
        
        return old_keywords.count()
    
    def _migrate_keywords_metrics(self):
        """Migre les métriques SEO des keywords"""
        from keyword_research.models import Keyword as OldKeyword
        from seo_keywords_metrics.models import KeywordMetrics
        from seo_keywords_base.models import Keyword as NewKeyword
        
        # Seulement les keywords qui ont des métriques
        old_keywords_with_metrics = OldKeyword.objects.exclude(
            da_min__isnull=True, da_max__isnull=True, 
            bl_min__isnull=True, bl_max__isnull=True,
            kdifficulty__isnull=True
        )
        
        metrics_to_create = []
        
        for old_kw in old_keywords_with_metrics.iterator(chunk_size=self.batch_size):
            try:
                new_keyword = NewKeyword.objects.get(id=old_kw.id)
                
                metrics = KeywordMetrics(
                    keyword=new_keyword,
                    da_min=old_kw.da_min,
                    da_max=old_kw.da_max,
                    da_median=old_kw.da_median,
                    da_q1=old_kw.da_q1,
                    da_q3=old_kw.da_q3,
                    bl_min=old_kw.bl_min,
                    bl_max=old_kw.bl_max,
                    bl_median=old_kw.bl_median,
                    bl_q1=old_kw.bl_q1,
                    bl_q3=old_kw.bl_q3,
                    kdifficulty=old_kw.kdifficulty,
                    created_at=old_kw.created_at,
                    updated_at=old_kw.updated_at,
                )
                metrics_to_create.append(metrics)
                
                if len(metrics_to_create) >= self.batch_size:
                    KeywordMetrics.objects.bulk_create(metrics_to_create, ignore_conflicts=True)
                    metrics_to_create = []
                    
            except NewKeyword.DoesNotExist:
                logger.warning(f"Keyword {old_kw.id} non trouvé dans nouvelle app")
                continue
        
        if metrics_to_create:
            KeywordMetrics.objects.bulk_create(metrics_to_create, ignore_conflicts=True)
        
        return old_keywords_with_metrics.count()
    
    def _migrate_content_types(self):
        """Migre les types de contenu"""
        from keyword_research.models import ContentType as OldContentType
        from seo_keywords_content_types.models import ContentType as NewContentType
        
        old_content_types = OldContentType.objects.all()
        new_content_types = []
        
        for old_ct in old_content_types:
            new_ct = NewContentType(
                id=old_ct.id,
                name=old_ct.name,
                description=old_ct.description,
                created_at=old_ct.created_at,
                updated_at=old_ct.updated_at,
            )
            new_content_types.append(new_ct)
        
        NewContentType.objects.bulk_create(new_content_types, ignore_conflicts=True)
        return len(new_content_types)
    
    def _migrate_cocoon_categories(self):
        """Migre les catégories de cocons"""
        from keyword_research.models import CocoonCategory as OldCategory
        from seo_keywords_cocoons.models import CocoonCategory as NewCategory
        
        old_categories = OldCategory.objects.all()
        new_categories = []
        
        for old_cat in old_categories:
            new_cat = NewCategory(
                id=old_cat.id,
                name=old_cat.name,
                description=old_cat.description,
                color=old_cat.color,
                created_at=old_cat.created_at,
                updated_at=old_cat.updated_at,
            )
            new_categories.append(new_cat)
        
        NewCategory.objects.bulk_create(new_categories, ignore_conflicts=True)
        return len(new_categories)
    
    def _migrate_semantic_cocoons(self):
        """Migre les cocons sémantiques"""
        from keyword_research.models import SemanticCocoon as OldCocoon
        from seo_keywords_cocoons.models import SemanticCocoon as NewCocoon
        
        old_cocoons = OldCocoon.objects.all()
        
        for old_cocoon in old_cocoons:
            new_cocoon = NewCocoon.objects.create(
                id=old_cocoon.id,
                name=old_cocoon.name,
                description=old_cocoon.description,
                slug=old_cocoon.slug,
                openai_file_id=old_cocoon.openai_file_id,
                openai_vector_store_id=old_cocoon.openai_vector_store_id,
                openai_storage_type=old_cocoon.openai_storage_type,
                openai_file_version=old_cocoon.openai_file_version,
                last_pushed_at=old_cocoon.last_pushed_at,
                created_at=old_cocoon.created_at,
                updated_at=old_cocoon.updated_at,
            )
            
            # Migrer les relations ManyToMany avec les catégories
            category_ids = list(old_cocoon.categories.values_list('id', flat=True))
            new_cocoon.categories.set(category_ids)
        
        return old_cocoons.count()
    
    def _migrate_ppas(self):
        """Migre les questions PPA"""
        from keyword_research.models import PPA as OldPPA
        from seo_keywords_ppa.models import PPA as NewPPA
        
        old_ppas = OldPPA.objects.all()
        new_ppas = []
        
        for old_ppa in old_ppas:
            new_ppa = NewPPA(
                id=old_ppa.id,
                question=old_ppa.question,
                created_at=old_ppa.created_at,
                updated_at=old_ppa.updated_at,
            )
            new_ppas.append(new_ppa)
        
        NewPPA.objects.bulk_create(new_ppas, ignore_conflicts=True)
        return len(new_ppas)
    
    def _migrate_keyword_content_type_associations(self):
        """Migre les associations Keyword-ContentType"""
        from keyword_research.models import KeywordContentType as OldAssoc
        from seo_keywords_content_types.models import KeywordContentType as NewAssoc
        from seo_keywords_base.models import Keyword as NewKeyword
        from seo_keywords_content_types.models import ContentType as NewContentType
        
        old_associations = OldAssoc.objects.all()
        new_associations = []
        
        for old_assoc in old_associations.iterator(chunk_size=self.batch_size):
            try:
                new_keyword = NewKeyword.objects.get(id=old_assoc.keyword_id)
                new_content_type = NewContentType.objects.get(id=old_assoc.content_type_id)
                
                new_assoc = NewAssoc(
                    keyword=new_keyword,
                    content_type=new_content_type,
                    priority=old_assoc.priority,
                    created_at=old_assoc.created_at,
                    updated_at=old_assoc.updated_at,
                )
                new_associations.append(new_assoc)
                
                if len(new_associations) >= self.batch_size:
                    NewAssoc.objects.bulk_create(new_associations, ignore_conflicts=True)
                    new_associations = []
                    
            except (NewKeyword.DoesNotExist, NewContentType.DoesNotExist) as e:
                logger.warning(f"Association ignorée: {str(e)}")
                continue
        
        if new_associations:
            NewAssoc.objects.bulk_create(new_associations, ignore_conflicts=True)
        
        return old_associations.count()
    
    def _migrate_cocoon_keyword_associations(self):
        """Migre les associations Cocoon-Keyword"""
        from keyword_research.models import CocoonKeyword as OldAssoc
        from seo_keywords_cocoons.models import CocoonKeyword as NewAssoc
        from seo_keywords_base.models import Keyword as NewKeyword
        from seo_keywords_cocoons.models import SemanticCocoon as NewCocoon
        
        old_associations = OldAssoc.objects.all()
        new_associations = []
        
        for old_assoc in old_associations.iterator(chunk_size=self.batch_size):
            try:
                new_keyword = NewKeyword.objects.get(id=old_assoc.keyword_id)
                new_cocoon = NewCocoon.objects.get(id=old_assoc.cocoon_id)
                
                new_assoc = NewAssoc(
                    keyword=new_keyword,
                    cocoon=new_cocoon,
                    created_at=old_assoc.created_at,
                    updated_at=old_assoc.updated_at,
                )
                new_associations.append(new_assoc)
                
                if len(new_associations) >= self.batch_size:
                    NewAssoc.objects.bulk_create(new_associations, ignore_conflicts=True)
                    new_associations = []
                    
            except (NewKeyword.DoesNotExist, NewCocoon.DoesNotExist) as e:
                logger.warning(f"Association ignorée: {str(e)}")
                continue
        
        if new_associations:
            NewAssoc.objects.bulk_create(new_associations, ignore_conflicts=True)
        
        return old_associations.count()
    
    def _migrate_keyword_ppa_associations(self):
        """Migre les associations Keyword-PPA"""
        from keyword_research.models import KeywordPPA as OldAssoc
        from seo_keywords_ppa.models import KeywordPPA as NewAssoc
        from seo_keywords_base.models import Keyword as NewKeyword
        from seo_keywords_ppa.models import PPA as NewPPA
        
        old_associations = OldAssoc.objects.all()
        new_associations = []
        
        for old_assoc in old_associations.iterator(chunk_size=self.batch_size):
            try:
                new_keyword = NewKeyword.objects.get(id=old_assoc.keyword_id)
                new_ppa = NewPPA.objects.get(id=old_assoc.ppa_id)
                
                new_assoc = NewAssoc(
                    keyword=new_keyword,
                    ppa=new_ppa,
                    position=old_assoc.position,
                    created_at=old_assoc.created_at,
                    updated_at=old_assoc.updated_at,
                )
                new_associations.append(new_assoc)
                
                if len(new_associations) >= self.batch_size:
                    NewAssoc.objects.bulk_create(new_associations, ignore_conflicts=True)
                    new_associations = []
                    
            except (NewKeyword.DoesNotExist, NewPPA.DoesNotExist) as e:
                logger.warning(f"Association ignorée: {str(e)}")
                continue
        
        if new_associations:
            NewAssoc.objects.bulk_create(new_associations, ignore_conflicts=True)
        
        return old_associations.count()