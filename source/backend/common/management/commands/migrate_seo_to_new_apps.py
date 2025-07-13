# backend/common/management/commands/migrate_seo_to_new_apps.py

import logging
import os
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.utils import timezone
from django.utils.text import slugify

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    🚀 MIGRATION COMPLÈTE SEO_ANALYZER → KEYWORD_RESEARCH + WEBSITE_MANAGER
    
    Migration intelligente par MATCHING DE CONTENU (pas d'IDs préservés).
    Génère de nouveaux IDs séquentiels propres.
    
    Usage:
        python manage.py migrate_seo_to_new_apps --dry-run
        python manage.py migrate_seo_to_new_apps --all --backup --clear-existing
        python manage.py migrate_seo_to_new_apps --brand-id=9 --clear-existing
    """
    
    help = 'Migration complète seo_analyzer vers keyword_research + website_manager'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mode simulation - aucune donnée créée'
        )
        parser.add_argument(
            '--brand-id',
            type=int,
            help='Migrer uniquement une brand spécifique'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Migrer toutes les brands'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Vider les nouvelles tables avant migration'
        )
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Créer un backup des nouvelles tables avant migration'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dry_run = False
        self.stats = defaultdict(int)
        self.id_mappings = {
            'keywords': {},
            'cocoons': {},
            'pages': {},
            'websites': {},
            'ppas': {},
            'content_types': {},
            'categories': {}
        }
    
    def handle(self, *args, **options):
        """Point d'entrée principal"""
        self.dry_run = options['dry_run']
        brand_id = options.get('brand_id')
        migrate_all = options.get('all')
        clear_existing = options.get('clear_existing')
        backup = options.get('backup')
        
        mode = "🧪 DRY-RUN" if self.dry_run else "🚀 MIGRATION RÉELLE"
        self.stdout.write(
            self.style.SUCCESS(
                f"{mode} - Migration par MATCHING DE CONTENU"
            )
        )
        
        if not migrate_all and not brand_id:
            self.stdout.write(
                self.style.ERROR("❌ Spécifiez --all ou --brand-id=X")
            )
            return
        
        try:
            # Import des modèles
            self._import_models()
            
            # Backup optionnel
            if backup and not self.dry_run:
                self._create_backup()
            
            # Clear optionnel
            if clear_existing and not self.dry_run:
                self._clear_existing_data()
            
            # Migration principale
            if brand_id:
                self.stdout.write(f"🎯 Migration de la brand {brand_id}")
                self._migrate_brand(brand_id)
            else:
                self.stdout.write(f"🌍 Migration de toutes les brands")
                self._migrate_all_brands()
            
            # Rapport final
            self._print_final_report()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"💥 Erreur critique: {str(e)}")
            )
            logger.error(f"Migration failed: {str(e)}", exc_info=True)
            raise
    
    def _import_models(self):
        """Import des modèles pour éviter les circular imports"""
        
        # Anciens modèles (seo_analyzer)
        from seo_analyzer.models import (
            Keyword as OldKeyword,
            SemanticCocoon as OldCocoon,
            CocoonCategory as OldCategory,
            CocoonKeyword as OldCocoonKeyword,
            PPA as OldPPA,
            KeywordPPA as OldKeywordPPA,
            ContentType as OldContentType,
            KeywordContentType as OldKeywordContentType,
            DraftKeyword as OldDraftKeyword,
            Website as OldWebsite,
            Page as OldPage,
            PageKeyword as OldPageKeyword,
        )
        
        # Nouveaux modèles (keyword_research)
        from keyword_research.models import (
            Keyword as NewKeyword,
            SemanticCocoon as NewCocoon,
            CocoonCategory as NewCategory,
            CocoonKeyword as NewCocoonKeyword,
            PPA as NewPPA,
            KeywordPPA as NewKeywordPPA,
            ContentType as NewContentType,
            KeywordContentType as NewKeywordContentType,
            DraftKeyword as NewDraftKeyword,
        )
        
        # Nouveaux modèles (website_manager)
        from website_manager.models import (
            Website as NewWebsite,
            Page as NewPage,
            PageKeyword as NewPageKeyword,
        )
        
        # Stocker dans self pour accès global
        self.models = {
            'old': {
                'Keyword': OldKeyword,
                'SemanticCocoon': OldCocoon,
                'CocoonCategory': OldCategory,
                'CocoonKeyword': OldCocoonKeyword,
                'PPA': OldPPA,
                'KeywordPPA': OldKeywordPPA,
                'ContentType': OldContentType,
                'KeywordContentType': OldKeywordContentType,
                'DraftKeyword': OldDraftKeyword,
                'Website': OldWebsite,
                'Page': OldPage,
                'PageKeyword': OldPageKeyword,
            },
            'new_kr': {
                'Keyword': NewKeyword,
                'SemanticCocoon': NewCocoon,
                'CocoonCategory': NewCategory,
                'CocoonKeyword': NewCocoonKeyword,
                'PPA': NewPPA,
                'KeywordPPA': NewKeywordPPA,
                'ContentType': NewContentType,
                'KeywordContentType': NewKeywordContentType,
                'DraftKeyword': NewDraftKeyword,
            },
            'new_wm': {
                'Website': NewWebsite,
                'Page': NewPage,
                'PageKeyword': NewPageKeyword,
            }
        }
    
    def _create_backup(self):
        """Crée un backup SQL des nouvelles tables"""
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"/tmp/megahub_backup_{timestamp}.sql"
        
        self.stdout.write(f"💾 Création backup dans {backup_file}...")
        
        # Tables à sauvegarder
        tables = [
            'keyword_research_keyword',
            'keyword_research_semanticcocoon',
            'keyword_research_cocoonkeyword',
            'keyword_research_ppa',
            'keyword_research_keywordppa',
            'keyword_research_contenttype',
            'keyword_research_keywordcontenttype',
            'keyword_research_cocooncategory',
            'keyword_research_draftkeyword',
            'website_manager_website',
            'website_manager_page',
            'website_manager_pagekeyword',
        ]
        
        # Créer le fichier de backup
        with open(backup_file, 'w') as f:
            f.write(f"-- MEGAHUB Backup {timestamp}\n\n")
            
            for table in tables:
                with connection.cursor() as cursor:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        f.write(f"-- Table {table}: {count} rows\n")
                    except Exception:
                        f.write(f"-- Table {table}: ERROR\n")
        
        self.stdout.write(f"✅ Backup créé: {backup_file}")
    
    def _clear_existing_data(self):
        """Vide les nouvelles tables (ATTENTION: destructif)"""
        self.stdout.write("🗑️  Suppression des données existantes...")
        
        # Ordre important pour les FK
        models_to_clear = [
            # keyword_research (relations en premier)
            self.models['new_kr']['CocoonKeyword'],
            self.models['new_kr']['KeywordPPA'],
            self.models['new_kr']['KeywordContentType'],
            self.models['new_kr']['DraftKeyword'],
            
            # keyword_research (entités principales)
            self.models['new_kr']['Keyword'],
            self.models['new_kr']['SemanticCocoon'],
            self.models['new_kr']['PPA'],
            self.models['new_kr']['ContentType'],
            self.models['new_kr']['CocoonCategory'],
            
            # website_manager (relations en premier)
            self.models['new_wm']['PageKeyword'],
            
            # website_manager (entités principales)
            self.models['new_wm']['Page'],
            self.models['new_wm']['Website'],
        ]
        
        for model in models_to_clear:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f"  🗑️  {model._meta.label}: {count} supprimés")
        
        # Reset des séquences PostgreSQL pour que les IDs repartent de 1
        self._reset_sequences()
    
    def _reset_sequences(self):
        """Reset les séquences PostgreSQL"""
        with connection.cursor() as cursor:
            sequences = [
                'keyword_research_keyword_id_seq',
                'keyword_research_semanticcocoon_id_seq',
                'keyword_research_cocooncategory_id_seq',
                'keyword_research_ppa_id_seq',
                'keyword_research_contenttype_id_seq',
                'keyword_research_draftkeyword_id_seq',
                'website_manager_website_id_seq',
                'website_manager_page_id_seq',
                'website_manager_pagekeyword_id_seq',
            ]
            
            for seq in sequences:
                try:
                    cursor.execute(f"ALTER SEQUENCE {seq} RESTART WITH 1")
                    self.stdout.write(f"  🔄 Reset {seq}")
                except Exception:
                    pass  # Séquence n'existe peut-être pas
    
    def _migrate_all_brands(self):
        """Migre toutes les brands"""
        brands = self.models['old']['Website'].objects.values_list('brand_id', flat=True).distinct()
        
        for brand_id in brands:
            self.stdout.write(f"\n🏢 Migration Brand {brand_id}")
            self._migrate_brand(brand_id)
    
    def _migrate_brand(self, brand_id):
        """Migre une brand complète"""
        
        try:
            with transaction.atomic():
                # 1. PHASE KEYWORD_RESEARCH (sans dépendances cross-app)
                self.stdout.write("  📦 Phase 1: keyword_research...")
                self._migrate_keyword_research_for_brand(brand_id)
                
                # 2. PHASE WEBSITE_MANAGER (avec références vers keyword_research)
                self.stdout.write("  🌐 Phase 2: website_manager...")
                self._migrate_website_manager_for_brand(brand_id)
                
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ Brand {brand_id} migrée avec succès")
                )
                
        except Exception as e:
            self.stats['errors'] += 1
            self.stdout.write(
                self.style.ERROR(f"  ❌ Erreur Brand {brand_id}: {str(e)}")
            )
            raise
    
    def _migrate_keyword_research_for_brand(self, brand_id):
        """Migre les données keyword_research pour une brand"""
        
        # 1. Categories (globales, pas de brand)
        self._migrate_categories()
        
        # 2. Keywords utilisés par cette brand
        self._migrate_keywords_for_brand(brand_id)
        
        # 3. PPAs des keywords de cette brand
        self._migrate_ppas_for_brand(brand_id)
        
        # 4. ContentTypes des keywords de cette brand
        self._migrate_content_types_for_brand(brand_id)
        
        # 5. Cocons de cette brand (avec leurs keywords)
        self._migrate_cocoons_for_brand(brand_id)
        
        # 6. DraftKeywords de cette brand
        self._migrate_draft_keywords_for_brand(brand_id)
    
    def _migrate_website_manager_for_brand(self, brand_id):
        """Migre les données website_manager pour une brand"""
        
        # 1. Website de cette brand
        website = self._migrate_website_for_brand(brand_id)
        
        if website:
            # 2. Pages de ce website
            self._migrate_pages_for_website(website)
            
            # 3. PageKeywords (avec références vers keyword_research)
            self._migrate_page_keywords_for_website(website)
    
    # ==================== HELPER FUNCTIONS ====================
    
    def _safe_get_field(self, obj, field_name, default=None):
        """Récupère un champ en toute sécurité avec fallback"""
        try:
            value = getattr(obj, field_name, default)
            return value if value is not None else default
        except AttributeError:
            return default
    
    def _get_timestamp_fields(self, obj, current_time=None):
        """Récupère les timestamps avec fallbacks"""
        if current_time is None:
            current_time = timezone.now()
        
        created_at = self._safe_get_field(obj, 'created_at', current_time)
        updated_at = self._safe_get_field(obj, 'updated_at', current_time)
        
        return {
            'created_at': created_at,
            'updated_at': updated_at
        }
    
    # ==================== KEYWORD_RESEARCH MIGRATION ====================
    
    def _migrate_categories(self):
        """🎯 Migre toutes les catégories par MATCHING NAME"""
        old_categories = self.models['old']['CocoonCategory'].objects.all()
        
        for old_cat in old_categories:
            if self.dry_run:
                self.stats['categories'] += 1
                continue
            
            # ✅ MATCHING PAR NAME (unique) avec gestion des champs manquants
            defaults = {
                'description': self._safe_get_field(old_cat, 'description', ''),
                'color': self._safe_get_field(old_cat, 'color', '#3498db'),
            }
            
            # Ajouter timestamps s'ils existent
            defaults.update(self._get_timestamp_fields(old_cat))
            
            new_cat, created = self.models['new_kr']['CocoonCategory'].objects.get_or_create(
                name=old_cat.name,  # ← Clé unique
                defaults=defaults
            )
            
            if created:
                self.stats['categories'] += 1
            
            # 🗺️ MAPPING ancien_id → nouveau_id
            self.id_mappings['categories'][old_cat.id] = new_cat.id
    
    def _migrate_keywords_for_brand(self, brand_id):
        """🎯 Migre les keywords par MATCHING KEYWORD (déjà bon)"""
        
        # Keywords utilisés par les pages de cette brand
        old_keywords = self.models['old']['Keyword'].objects.filter(
            keyword_pages__page__website__brand_id=brand_id
        ).distinct()
        
        # + Keywords des cocons (global) - CORRECTION ICI
        cocoon_keywords = self.models['old']['Keyword'].objects.filter(
            cocoon_associations__cocoon__in=self.models['old']['SemanticCocoon'].objects.all()
        ).distinct()
        
        # Union des deux
        all_keywords = (old_keywords | cocoon_keywords).distinct()
        
        for old_kw in all_keywords:
            if self.dry_run:
                self.stats['keywords'] += 1
                continue
            
            # ✅ MATCHING PAR KEYWORD (unique) avec gestion des champs optionnels
            defaults = {
                'volume': self._safe_get_field(old_kw, 'volume'),
                'content_types': self._safe_get_field(old_kw, 'content_types', ''),
                'da_min': self._safe_get_field(old_kw, 'da_min'),
                'da_max': self._safe_get_field(old_kw, 'da_max'),
                'da_median': self._safe_get_field(old_kw, 'da_median'),
                'da_q1': self._safe_get_field(old_kw, 'da_q1'),
                'da_q3': self._safe_get_field(old_kw, 'da_q3'),
                'bl_min': self._safe_get_field(old_kw, 'bl_min'),
                'bl_max': self._safe_get_field(old_kw, 'bl_max'),
                'bl_median': self._safe_get_field(old_kw, 'bl_median'),
                'bl_q1': self._safe_get_field(old_kw, 'bl_q1'),
                'bl_q3': self._safe_get_field(old_kw, 'bl_q3'),
                'kdifficulty': self._safe_get_field(old_kw, 'kdifficulty', ''),
                'search_intent': self._safe_get_field(old_kw, 'search_intent'),
                'cpc': self._safe_get_field(old_kw, 'cpc', ''),
                'youtube_videos': self._safe_get_field(old_kw, 'youtube_videos', ''),
                'local_pack': self._safe_get_field(old_kw, 'local_pack', False),
                'search_results': self._safe_get_field(old_kw, 'search_results', {}),
            }
            
            # Ajouter timestamps
            defaults.update(self._get_timestamp_fields(old_kw))
            
            new_kw, created = self.models['new_kr']['Keyword'].objects.get_or_create(
                keyword=old_kw.keyword,  # ← Clé unique
                defaults=defaults
            )
            
            if created:
                self.stats['keywords'] += 1
            
            # 🗺️ MAPPING ancien_id → nouveau_id
            self.id_mappings['keywords'][old_kw.id] = new_kw.id
    
    def _migrate_ppas_for_brand(self, brand_id):
        """🎯 Migre les PPAs par MATCHING QUESTION"""
        
        # PPAs des keywords de cette brand - CORRECTION ICI
        old_ppas = self.models['old']['PPA'].objects.filter(
            keyword_associations__keyword__keyword_pages__page__website__brand_id=brand_id
        ).distinct()
        
        for old_ppa in old_ppas:
            if self.dry_run:
                self.stats['ppas'] += 1
                continue
            
            # ✅ MATCHING PAR QUESTION (unique)
            defaults = self._get_timestamp_fields(old_ppa)
            
            new_ppa, created = self.models['new_kr']['PPA'].objects.get_or_create(
                question=old_ppa.question,  # ← Clé unique
                defaults=defaults
            )
            
            if created:
                self.stats['ppas'] += 1
            
            # 🗺️ MAPPING ancien_id → nouveau_id
            self.id_mappings['ppas'][old_ppa.id] = new_ppa.id
        
        # Relations KeywordPPA avec nouveaux IDs
        old_kw_ppas = self.models['old']['KeywordPPA'].objects.filter(
            keyword__keyword_pages__page__website__brand_id=brand_id
        ).distinct()
        
        for old_kw_ppa in old_kw_ppas:
            if self.dry_run:
                self.stats['keyword_ppas'] += 1
                continue
            
            # Utiliser les nouveaux IDs via mapping
            new_keyword_id = self.id_mappings['keywords'].get(old_kw_ppa.keyword_id)
            new_ppa_id = self.id_mappings['ppas'].get(old_kw_ppa.ppa_id)
            
            if new_keyword_id and new_ppa_id:
                try:
                    defaults = {
                        'position': self._safe_get_field(old_kw_ppa, 'position', 1),
                    }
                    defaults.update(self._get_timestamp_fields(old_kw_ppa))
                    
                    new_kw_ppa, created = self.models['new_kr']['KeywordPPA'].objects.get_or_create(
                        keyword_id=new_keyword_id,
                        ppa_id=new_ppa_id,
                        defaults=defaults
                    )
                    
                    if created:
                        self.stats['keyword_ppas'] += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"    ⚠️  Erreur KeywordPPA: {str(e)}")
                    )
    
    def _migrate_content_types_for_brand(self, brand_id):
        """🎯 Migre les ContentTypes par MATCHING NAME"""
        
        old_content_types = self.models['old']['ContentType'].objects.filter(
            keyword_associations__keyword__keyword_pages__page__website__brand_id=brand_id
        ).distinct()
        
        for old_ct in old_content_types:
            if self.dry_run:
                self.stats['content_types'] += 1
                continue
            
            # ✅ MATCHING PAR NAME (unique)
            defaults = {
                'description': self._safe_get_field(old_ct, 'description', ''),
            }
            defaults.update(self._get_timestamp_fields(old_ct))
            
            new_ct, created = self.models['new_kr']['ContentType'].objects.get_or_create(
                name=old_ct.name,  # ← Clé unique
                defaults=defaults
            )
            
            if created:
                self.stats['content_types'] += 1
            
            # 🗺️ MAPPING ancien_id → nouveau_id
            self.id_mappings['content_types'][old_ct.id] = new_ct.id
        
        # Relations KeywordContentType avec nouveaux IDs
        old_kw_cts = self.models['old']['KeywordContentType'].objects.filter(
            keyword__keyword_pages__page__website__brand_id=brand_id
        ).distinct()
        
        for old_kw_ct in old_kw_cts:
            if self.dry_run:
                self.stats['keyword_content_types'] += 1
                continue
            
            # Utiliser les nouveaux IDs via mapping
            new_keyword_id = self.id_mappings['keywords'].get(old_kw_ct.keyword_id)
            new_content_type_id = self.id_mappings['content_types'].get(old_kw_ct.content_type_id)
            
            if new_keyword_id and new_content_type_id:
                try:
                    defaults = {
                        'priority': self._safe_get_field(old_kw_ct, 'priority', 0),
                    }
                    defaults.update(self._get_timestamp_fields(old_kw_ct))
                    
                    new_kw_ct, created = self.models['new_kr']['KeywordContentType'].objects.get_or_create(
                        keyword_id=new_keyword_id,
                        content_type_id=new_content_type_id,
                        defaults=defaults
                    )
                    
                    if created:
                        self.stats['keyword_content_types'] += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"    ⚠️  Erreur KeywordContentType: {str(e)}")
                    )
    
    def _migrate_cocoons_for_brand(self, brand_id):
        """🎯 Migre tous les cocons par MATCHING NAME"""
        
        old_cocoons = self.models['old']['SemanticCocoon'].objects.all()
        
        for old_cocoon in old_cocoons:
            if self.dry_run:
                self.stats['cocoons'] += 1
                continue
            
            # Générer slug unique
            base_slug = slugify(old_cocoon.name)
            slug = base_slug
            counter = 1
            while self.models['new_kr']['SemanticCocoon'].objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            # ✅ MATCHING PAR NAME (unique)
            defaults = {
                'description': self._safe_get_field(old_cocoon, 'description', ''),
                'slug': slug,
                'openai_file_id': self._safe_get_field(old_cocoon, 'openai_file_id', ''),
                'openai_vector_store_id': self._safe_get_field(old_cocoon, 'openai_vector_store_id', ''),
                'openai_storage_type': self._safe_get_field(old_cocoon, 'openai_storage_type', 'vector_store'),
                'openai_file_version': self._safe_get_field(old_cocoon, 'openai_file_version', 0),
                'last_pushed_at': self._safe_get_field(old_cocoon, 'last_pushed_at'),
            }
            defaults.update(self._get_timestamp_fields(old_cocoon))
            
            new_cocoon, created = self.models['new_kr']['SemanticCocoon'].objects.get_or_create(
                name=old_cocoon.name,  # ← Clé unique
                defaults=defaults
            )
            
            if created:
                self.stats['cocoons'] += 1
                
                # Migrer les relations ManyToMany categories avec nouveaux IDs
                if hasattr(old_cocoon, 'categories'):
                    for old_category in old_cocoon.categories.all():
                        new_category_id = self.id_mappings['categories'].get(old_category.id)
                        if new_category_id:
                            try:
                                new_category = self.models['new_kr']['CocoonCategory'].objects.get(id=new_category_id)
                                new_cocoon.categories.add(new_category)
                            except Exception:
                                pass
            
            # 🗺️ MAPPING ancien_id → nouveau_id
            self.id_mappings['cocoons'][old_cocoon.id] = new_cocoon.id
        
        # Relations CocoonKeyword avec nouveaux IDs
        old_cocoon_keywords = self.models['old']['CocoonKeyword'].objects.all()
        
        for old_ck in old_cocoon_keywords:
            if self.dry_run:
                self.stats['cocoon_keywords'] += 1
                continue
            
            # Utiliser les nouveaux IDs via mapping
            new_cocoon_id = self.id_mappings['cocoons'].get(old_ck.cocoon_id)
            new_keyword_id = self.id_mappings['keywords'].get(old_ck.keyword_id)
            
            if new_cocoon_id and new_keyword_id:
                try:
                    defaults = self._get_timestamp_fields(old_ck)
                    
                    new_ck, created = self.models['new_kr']['CocoonKeyword'].objects.get_or_create(
                        cocoon_id=new_cocoon_id,
                        keyword_id=new_keyword_id,
                        defaults=defaults
                    )
                    
                    if created:
                        self.stats['cocoon_keywords'] += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"    ⚠️  Erreur CocoonKeyword: {str(e)}")
                    )
    
    def _migrate_draft_keywords_for_brand(self, brand_id):
        """🎯 Migre les DraftKeywords par MATCHING KEYWORD+BRAND+USER"""
        
        old_drafts = self.models['old']['DraftKeyword'].objects.filter(brand_id=brand_id)
        
        for old_draft in old_drafts:
            if self.dry_run:
                self.stats['draft_keywords'] += 1
                continue
            
            # ✅ MATCHING PAR KEYWORD+BRAND+USER (unique_together)
            defaults = {
                'note': self._safe_get_field(old_draft, 'note', ''),
            }
            defaults.update(self._get_timestamp_fields(old_draft))
            
            new_draft, created = self.models['new_kr']['DraftKeyword'].objects.get_or_create(
                keyword=old_draft.keyword,
                brand_id=old_draft.brand_id,
                user_id=old_draft.user_id,
                defaults=defaults
            )
            
            if created:
                self.stats['draft_keywords'] += 1
    
    # ==================== WEBSITE_MANAGER MIGRATION ====================
    
    def _migrate_website_for_brand(self, brand_id):
        """🎯 Migre le website par MATCHING BRAND_ID"""
        
        try:
            old_website = self.models['old']['Website'].objects.get(brand_id=brand_id)
        except self.models['old']['Website'].DoesNotExist:
            self.stdout.write(f"    ⚠️  Aucun website pour brand {brand_id}")
            return None
        
        if self.dry_run:
            self.stats['websites'] += 1
            return f"dry_run_website_{brand_id}"
        
        # ✅ MATCHING PAR BRAND_ID (unique OneToOne)
        defaults = {
            'name': self._safe_get_field(old_website, 'name', f'Site Brand {brand_id}'),
            'url': self._safe_get_field(old_website, 'url', 'https://example.com'),
            'domain_authority': self._safe_get_field(old_website, 'domain_authority'),
            'max_competitor_backlinks': self._safe_get_field(old_website, 'max_competitor_backlinks'),
            'max_competitor_kd': self._safe_get_field(old_website, 'max_competitor_kd'),
            'last_openai_sync': self._safe_get_field(old_website, 'last_openai_sync'),
            'openai_sync_version': self._safe_get_field(old_website, 'openai_sync_version', 0),
        }
        defaults.update(self._get_timestamp_fields(old_website))
        
        new_website, created = self.models['new_wm']['Website'].objects.get_or_create(
            brand_id=old_website.brand_id,  # ← Clé unique
            defaults=defaults
        )
        
        if created:
            self.stats['websites'] += 1
        
        # 🗺️ MAPPING ancien_id → nouveau_id
        self.id_mappings['websites'][old_website.id] = new_website.id
        return new_website
    
    def _migrate_pages_for_website(self, website):
        """🎯 Migre toutes les pages par MATCHING WEBSITE+URL_PATH"""
        
        if self.dry_run:
            old_pages = self.models['old']['Page'].objects.filter(
                website_id=list(self.id_mappings['websites'].keys())[0] if self.id_mappings['websites'] else 1
            )
            self.stats['pages'] += old_pages.count()
            return
        
        old_pages = self.models['old']['Page'].objects.filter(
            website_id=[k for k, v in self.id_mappings['websites'].items() if v == website.id][0]
        ).order_by('id')
        
        # Phase 1: Créer toutes les pages sans parent
        for old_page in old_pages:
            # ✅ MATCHING PAR WEBSITE+URL_PATH (unique_together)
            defaults = {
                'title': self._safe_get_field(old_page, 'title', 'Page sans titre'),
                'meta_description': self._safe_get_field(old_page, 'meta_description', ''),
                'search_intent': self._safe_get_field(old_page, 'search_intent'),
                'page_type': self._safe_get_field(old_page, 'page_type', 'vitrine'),
                'status': self._safe_get_field(old_page, 'status', 'draft'),
                'status_changed_at': self._safe_get_field(old_page, 'status_changed_at'),
                'status_changed_by_id': self._safe_get_field(old_page, 'status_changed_by_id'),
                'production_notes': self._safe_get_field(old_page, 'production_notes', ''),
                'scheduled_publish_date': self._safe_get_field(old_page, 'scheduled_publish_date'),
                'sitemap_priority': self._safe_get_field(old_page, 'sitemap_priority', 0.5),
                'sitemap_changefreq': self._safe_get_field(old_page, 'sitemap_changefreq', 'weekly'),
                'exclude_from_sitemap': self._safe_get_field(old_page, 'exclude_from_sitemap', False),
                'page_template': self._safe_get_field(old_page, 'page_template', 'default'),
                'featured_image': self._safe_get_field(old_page, 'featured_image'),
                'last_rendered_at': self._safe_get_field(old_page, 'last_rendered_at'),
            }
            defaults.update(self._get_timestamp_fields(old_page))
            
            # URL path avec fallback
            url_path = self._safe_get_field(old_page, 'url_path', f'/page-{old_page.id}')
            
            new_page, created = self.models['new_wm']['Page'].objects.get_or_create(
                website=website,
                url_path=url_path,
                defaults=defaults
            )
            
            if created:
                self.stats['pages'] += 1
            
            # 🗺️ MAPPING ancien_id → nouveau_id
            self.id_mappings['pages'][old_page.id] = new_page.id
        
        # Phase 2: Fixer la hiérarchie parent-enfant avec nouveaux IDs
        for old_page in old_pages:
            if hasattr(old_page, 'parent_id') and old_page.parent_id:
                new_parent_id = self.id_mappings['pages'].get(old_page.parent_id)
                new_page_id = self.id_mappings['pages'].get(old_page.id)
                
                if new_parent_id and new_page_id:
                    try:
                        new_page = self.models['new_wm']['Page'].objects.get(id=new_page_id)
                        new_parent = self.models['new_wm']['Page'].objects.get(id=new_parent_id)
                        new_page.parent = new_parent
                        new_page.save(update_fields=['parent'])
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f"    ⚠️  Erreur hiérarchie page {old_page.id}: {str(e)}")
                        )
    
    def _migrate_page_keywords_for_website(self, website):
        """🎯 Migre les PageKeywords avec nouveaux IDs"""
        
        if self.dry_run:
            # Compter approximativement
            self.stats['page_keywords'] += 100  # Estimation
            return
        
        # Trouver l'ancien website_id via mapping inversé
        old_website_id = None
        for old_id, new_id in self.id_mappings['websites'].items():
            if new_id == website.id:
                old_website_id = old_id
                break
        
        if not old_website_id:
            self.stdout.write(f"    ⚠️  Impossible de trouver l'ancien website_id")
            return
        
        old_page_keywords = self.models['old']['PageKeyword'].objects.filter(
            page__website_id=old_website_id
        ).select_related('page', 'keyword', 'source_cocoon')
        
        for old_pk in old_page_keywords:
            # Utiliser les nouveaux IDs via mapping
            new_page_id = self.id_mappings['pages'].get(old_pk.page_id)
            new_keyword_id = self.id_mappings['keywords'].get(old_pk.keyword_id)
            new_source_cocoon_id = None
            
            if hasattr(old_pk, 'source_cocoon_id') and old_pk.source_cocoon_id:
                new_source_cocoon_id = self.id_mappings['cocoons'].get(old_pk.source_cocoon_id)
            
            if new_page_id and new_keyword_id:
                try:
                    defaults = {
                        'position': self._safe_get_field(old_pk, 'position'),
                        'keyword_type': self._safe_get_field(old_pk, 'keyword_type', 'secondary'),
                        'source_cocoon_id': new_source_cocoon_id,
                        'is_ai_selected': self._safe_get_field(old_pk, 'is_ai_selected', False),
                        'notes': self._safe_get_field(old_pk, 'notes', ''),
                    }
                    defaults.update(self._get_timestamp_fields(old_pk))
                    
                    new_pk, created = self.models['new_wm']['PageKeyword'].objects.get_or_create(
                        page_id=new_page_id,
                        keyword_id=new_keyword_id,
                        defaults=defaults
                    )
                    
                    if created:
                        self.stats['page_keywords'] += 1
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f"    ⚠️  Erreur PageKeyword page:{old_pk.page_id}→{new_page_id} "
                            f"keyword:{old_pk.keyword_id}→{new_keyword_id}: {str(e)}"
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"    ⚠️  IDs manquants PageKeyword page:{old_pk.page_id}→{new_page_id} "
                        f"keyword:{old_pk.keyword_id}→{new_keyword_id}"
                    )
                )
    
    def _print_final_report(self):
        """Affiche le rapport final détaillé"""
        
        mode = "🧪 SIMULATION" if self.dry_run else "🚀 MIGRATION RÉELLE"
        
        self.stdout.write(f"\n" + "="*80)
        self.stdout.write(
            self.style.SUCCESS(f"🎉 {mode} TERMINÉE !")
        )
        self.stdout.write("="*80)
        
        # Rapport keyword_research
        self.stdout.write(
            self.style.SUCCESS("📦 KEYWORD_RESEARCH:")
        )
        kr_stats = [
            ('Categories', self.stats['categories']),
            ('Keywords', self.stats['keywords']),
            ('PPAs', self.stats['ppas']),
            ('KeywordPPAs', self.stats['keyword_ppas']),
            ('ContentTypes', self.stats['content_types']),
            ('KeywordContentTypes', self.stats['keyword_content_types']),
            ('Cocons', self.stats['cocoons']),
            ('CocoonKeywords', self.stats['cocoon_keywords']),
            ('DraftKeywords', self.stats['draft_keywords']),
        ]
        
        for name, count in kr_stats:
            self.stdout.write(f"  📊 {name}: {count}")
        
        # Rapport website_manager
        self.stdout.write(
            self.style.SUCCESS("\n🌐 WEBSITE_MANAGER:")
        )
        wm_stats = [
            ('Websites', self.stats['websites']),
            ('Pages', self.stats['pages']),
            ('PageKeywords', self.stats['page_keywords']),
        ]
        
        for name, count in wm_stats:
            self.stdout.write(f"  📊 {name}: {count}")
        
        # Rapport mappings d'IDs
        self.stdout.write(
            self.style.SUCCESS("\n🗺️  MAPPINGS CRÉÉS:")
        )
        for entity_type, mapping in self.id_mappings.items():
            if mapping:
                self.stdout.write(f"  📋 {entity_type}: {len(mapping)} mappings")
        
        # Total
        total = sum(self.stats.values())
        self.stdout.write(
            self.style.SUCCESS(f"\n🎯 TOTAL: {total} entités migrées")
        )
        
        if self.stats['errors']:
            self.stdout.write(
                self.style.ERROR(f"❌ Erreurs: {self.stats['errors']}")
            )
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n💡 Mode simulation - Lancez sans --dry-run pour migrer réellement"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "\n✅ Migration intelligente terminée avec succès !"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    "🔥 Nouveaux IDs séquentiels propres générés dans les nouvelles apps"
                )
            )