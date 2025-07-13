# backend/seo_keywords_cocoons/serializers/cocoon_serializers.py

from rest_framework import serializers
from django.db import models

# Common - avec fallback
try:
    from common.serializers.mixins import TimestampedSerializer
except ImportError:
    TimestampedSerializer = serializers.ModelSerializer

# Local imports
from ..models import SemanticCocoon, CocoonCategory

import logging
logger = logging.getLogger(__name__)

class CocoonCategorySerializer(serializers.ModelSerializer):
    """Serializer pour catégories de cocons avec validation"""
    
    class Meta:
        model = CocoonCategory
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_name(self, value):
        """Validation nom catégorie"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Le nom doit faire au moins 2 caractères")
        
        # Unicité (case insensitive)
        name_clean = value.strip().lower()
        existing = CocoonCategory.objects.filter(name__iexact=name_clean)
        
        # Exclure l'instance actuelle en cas de modification
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise serializers.ValidationError("Une catégorie avec ce nom existe déjà")
        
        return value.strip()
    
    def validate_color(self, value):
        """Validation couleur hexadécimale"""
        import re
        if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
            raise serializers.ValidationError(
                "La couleur doit être au format hexadécimal (#RRGGBB)"
            )
        return value.upper()  # Standardiser en majuscules

class SemanticCocoonListSerializer(serializers.ModelSerializer):
    """Serializer optimisé pour liste des cocons"""
    
    categories_names = serializers.StringRelatedField(source='categories', many=True, read_only=True)
    categories_colors = serializers.SerializerMethodField()
    keywords_count = serializers.IntegerField(read_only=True)
    needs_sync = serializers.SerializerMethodField()
    sync_status = serializers.SerializerMethodField()
    
    class Meta:
        model = SemanticCocoon
        fields = [
            'id', 'name', 'slug', 'description', 
            'categories_names', 'categories_colors', 'keywords_count', 
            'needs_sync', 'sync_status', 'openai_storage_type',
            'created_at', 'updated_at'
        ]
    
    def get_categories_colors(self, obj):
        """Couleurs des catégories pour affichage UI"""
        return [{'name': cat.name, 'color': cat.color} for cat in obj.categories.all()]
    
    def get_needs_sync(self, obj):
        """Besoin de synchronisation"""
        try:
            return obj.needs_sync()
        except Exception as e:
            logger.warning(f"Error checking sync status for cocoon {obj.id}: {e}")
            return None
    
    def get_sync_status(self, obj):
        """Statut de synchronisation détaillé"""
        if not obj.last_pushed_at:
            return 'never_synced'
        elif obj.needs_sync():
            return 'needs_update'
        else:
            return 'up_to_date'

class SemanticCocoonSerializer(TimestampedSerializer):
    """Serializer complet pour cocons sémantiques avec validation robuste"""
    
    categories = CocoonCategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=CocoonCategory.objects.all(),
        many=True,
        write_only=True,
        source='categories',
        required=False
    )
    keywords_count = serializers.IntegerField(read_only=True)
    needs_sync = serializers.SerializerMethodField()
    sync_status = serializers.SerializerMethodField()
    
    class Meta:
        model = SemanticCocoon
        fields = [
            # 🔥 LISTE EXPLICITE au lieu de '__all__'
            'id', 'name', 'slug', 'description',
            'categories', 'category_ids', 'keywords_count',
            'needs_sync', 'sync_status',
            'openai_file_id', 'openai_vector_store_id', 
            'openai_storage_type', 'openai_file_version', 'last_pushed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'slug', 'created_at', 'updated_at',
            'openai_file_id', 'openai_vector_store_id', 
            'openai_file_version', 'last_pushed_at'
        ]
    
    def validate_name(self, value):
        """Validation nom cocon"""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("Le nom doit faire au moins 3 caractères")
        
        if len(value.strip()) > 255:
            raise serializers.ValidationError("Le nom ne peut pas dépasser 255 caractères")
        
        # Unicité (case insensitive)
        name_clean = value.strip().lower()
        existing = SemanticCocoon.objects.filter(name__iexact=name_clean)
        
        # Exclure l'instance actuelle en cas de modification
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise serializers.ValidationError("Un cocon avec ce nom existe déjà")
        
        return value.strip()
    
    def validate_description(self, value):
        """Validation description"""
        if value and len(value.strip()) > 2000:
            raise serializers.ValidationError("La description ne peut pas dépasser 2000 caractères")
        return value.strip() if value else value
    
    def validate_categories(self, value):
        """Validation catégories"""
        if len(value) > 5:
            raise serializers.ValidationError("Maximum 5 catégories par cocon")
        
        # Vérifier que toutes les catégories existent
        category_ids = [cat.id for cat in value]
        existing_count = CocoonCategory.objects.filter(id__in=category_ids).count()
        
        if existing_count != len(category_ids):
            raise serializers.ValidationError("Une ou plusieurs catégories n'existent pas")
        
        return value
    
    def get_needs_sync(self, obj):
        """Besoin de synchronisation"""
        try:
            return obj.needs_sync()
        except Exception as e:
            logger.warning(f"Error checking sync status for cocoon {obj.id}: {e}")
            return None
    
    def get_sync_status(self, obj):
        """Statut de synchronisation détaillé"""
        if not obj.last_pushed_at:
            return 'never_synced'
        elif obj.needs_sync():
            return 'needs_update'
        else:
            return 'up_to_date'

class SemanticCocoonDetailSerializer(SemanticCocoonSerializer):
    """Serializer pour vue détaillée avec stats supplémentaires"""
    
    top_keywords = serializers.SerializerMethodField()
    recent_keywords = serializers.SerializerMethodField()
    
    class Meta:
        model = SemanticCocoon
        # 🔥 CORRECTION: Redéfinition complète des champs
        fields = [
            # Champs de base (hérités)
            'id', 'name', 'slug', 'description',
            'categories', 'category_ids', 'keywords_count',
            'needs_sync', 'sync_status',
            'openai_file_id', 'openai_vector_store_id', 
            'openai_storage_type', 'openai_file_version', 'last_pushed_at',
            'created_at', 'updated_at',
            # Champs supplémentaires du detail
            'top_keywords', 'recent_keywords'
        ]
        read_only_fields = [
            'slug', 'created_at', 'updated_at',
            'openai_file_id', 'openai_vector_store_id', 
            'openai_file_version', 'last_pushed_at'
        ]
    
    def get_top_keywords(self, obj):
        """Top 10 des mots-clés par volume"""
        try:
            top_kw = obj.cocoon_keywords.select_related('keyword').filter(
                keyword__volume__isnull=False
            ).order_by('-keyword__volume')[:10]
            
            return [
                {
                    'keyword': ck.keyword.keyword,
                    'volume': ck.keyword.volume,
                    'search_intent': ck.keyword.search_intent
                }
                for ck in top_kw
            ]
        except Exception as e:
            logger.warning(f"Error getting top keywords for cocoon {obj.id}: {e}")
            return []
    
    def get_recent_keywords(self, obj):
        """5 derniers mots-clés ajoutés"""
        try:
            recent = obj.cocoon_keywords.select_related('keyword').order_by('-created_at')[:5]
            
            return [
                {
                    'keyword': ck.keyword.keyword,
                    'volume': ck.keyword.volume,
                    'added_at': ck.created_at
                }
                for ck in recent
            ]
        except Exception as e:
            logger.warning(f"Error getting recent keywords for cocoon {obj.id}: {e}")
            return []