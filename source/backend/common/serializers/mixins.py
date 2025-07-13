# backend/common/serializers/mixins.py
# Contenu du fichier fusionné - je vais te le donner après
# /var/www/megahub/backend/common/serializers/mixins.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.text import slugify

User = get_user_model()


# ====== MIXINS DE BASE ======

class DynamicFieldsSerializer(serializers.ModelSerializer):
    """Base serializer avec champs dynamiques et permissions"""
    
    def __init__(self, *args, **kwargs):
        # Configuration fields selon le contexte
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)
        action = kwargs.pop('action', None)
        
        super().__init__(*args, **kwargs)
        
        # Configuration automatique par action
        if not action:
            action = self.context.get('action')
        if action:
            self._configure_for_action(action)
        
        # Configuration manuelle
        if fields is not None:
            self._limit_fields(fields)
        if exclude is not None:
            self._exclude_fields(exclude)
        
        # Appliquer permissions
        self._apply_field_permissions()
    
    def _configure_for_action(self, action):
        """Configure les champs selon l'action ViewSet"""
        field_config = getattr(self.Meta, 'field_config', {})
        
        if action in field_config:
            self._limit_fields(field_config[action])
    
    def _limit_fields(self, fields):
        """Limite aux champs spécifiés"""
        allowed = set(fields)
        existing = set(self.fields)
        for field_name in existing - allowed:
            self.fields.pop(field_name)
    
    def _exclude_fields(self, exclude):
        """Exclut les champs spécifiés"""
        for field_name in exclude:
            self.fields.pop(field_name, None)
    
    def _apply_field_permissions(self):
        """Applique les permissions par champ"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            self._remove_authenticated_fields()
            return
        
        user = request.user
        
        # Permissions par rôle
        if not user.is_staff:
            self._remove_admin_fields()
        
        # Permissions par propriété
        if hasattr(self, 'instance') and self.instance:
            if not self._user_can_edit(user):
                self._make_protected_readonly()
    
    def _remove_authenticated_fields(self):
        """Supprime les champs pour utilisateurs non connectés"""
        auth_fields = getattr(self.Meta, 'authenticated_only_fields', [])
        for field in auth_fields:
            self.fields.pop(field, None)
    
    def _remove_admin_fields(self):
        """Supprime les champs admin"""
        admin_fields = getattr(self.Meta, 'admin_only_fields', [])
        for field in admin_fields:
            self.fields.pop(field, None)
    
    def _make_protected_readonly(self):
        """Rend certains champs read-only"""
        protected_fields = getattr(self.Meta, 'owner_only_fields', [])
        for field_name in protected_fields:
            if field_name in self.fields:
                self.fields[field_name].read_only = True
    
    def _user_can_edit(self, user):
        """Vérifie si l'user peut éditer l'instance"""
        # Override dans les serializers enfants
        return True


class TimestampedSerializer(DynamicFieldsSerializer):
    """Serializer avec gestion automatique des timestamps"""
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        abstract = True
        read_only_fields = ['created_at', 'updated_at']


class UserOwnedSerializer(DynamicFieldsSerializer):
    """Serializer pour objets avec propriétaire"""
    
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', 
        read_only=True
    )
    
    def create(self, validated_data):
        """Assigne automatiquement le créateur"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)
    
    def _user_can_edit(self, user):
        """Seul le propriétaire ou admin peut éditer"""
        return (
            user.is_staff or 
            (hasattr(self.instance, 'created_by') and self.instance.created_by == user)
        )


# ====== MIXINS SCOPE ======

class BrandScopedSerializer(DynamicFieldsSerializer):
    """Serializer pour objets scopés par brand"""
    
    def validate(self, attrs):
        """Validation scope brand automatique"""
        request = self.context.get('request')
        current_brand = getattr(request, 'current_brand', None)
        
        if current_brand and hasattr(self.Meta.model, 'brand'):
            attrs['brand'] = current_brand
        
        return super().validate(attrs)


class WebsiteScopedSerializer(DynamicFieldsSerializer):
    """Serializer pour objets scopés par website"""
    
    def get_website_from_context(self):
        """Récupère le website depuis le contexte"""
        request = self.context.get('request')
        return getattr(request, 'current_website', None) or self.context.get('website')
    
    def validate(self, attrs):
        """Validation scope website automatique"""
        website = self.get_website_from_context()
        
        if website and hasattr(self.Meta.model, 'website'):
            attrs['website'] = website
        
        return super().validate(attrs)


# ====== MIXINS FONCTIONNELS ======

class SearchableSerializerMixin:
    """Mixin pour recherche textuelle"""
    
    def get_search_fields(self):
        """Champs de recherche configurables"""
        return getattr(self.Meta, 'search_fields', [])


class StatsMixin:
    """Mixin pour stats calculées"""
    
    def get_stats_fields(self):
        """Champs stats configurables"""
        return getattr(self.Meta, 'stats_fields', {})
    
    def to_representation(self, instance):
        """Ajoute les stats à la représentation"""
        data = super().to_representation(instance)
        
        # Ajouter stats si demandées
        if self.context.get('include_stats', False):
            stats = self._calculate_stats(instance)
            data.update(stats)
        
        return data
    
    def _calculate_stats(self, instance):
        """Calcule les stats pour l'instance"""
        stats = {}
        stats_config = self.get_stats_fields()
        
        for stat_name, stat_method in stats_config.items():
            if hasattr(self, stat_method):
                stats[stat_name] = getattr(self, stat_method)(instance)
        
        return stats


class SlugMixin:
    """Mixin pour génération automatique de slugs"""
    
    def create(self, validated_data):
        """Génère le slug automatiquement à la création"""
        slug_field = getattr(self.Meta, 'slug_field', 'slug')
        source_field = getattr(self.Meta, 'slug_source_field', 'name')
        
        if slug_field in self.Meta.fields and source_field in validated_data:
            if not validated_data.get(slug_field):
                validated_data[slug_field] = self._generate_unique_slug(
                    validated_data[source_field]
                )
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Régénère le slug si le champ source change"""
        slug_field = getattr(self.Meta, 'slug_field', 'slug')
        source_field = getattr(self.Meta, 'slug_source_field', 'name')
        
        if (source_field in validated_data and 
            hasattr(instance, source_field) and
            validated_data[source_field] != getattr(instance, source_field)):
            
            validated_data[slug_field] = self._generate_unique_slug(
                validated_data[source_field],
                exclude_id=instance.pk
            )
        
        return super().update(instance, validated_data)
    
    def _generate_unique_slug(self, text, exclude_id=None):
        """Génère un slug unique"""
        base_slug = slugify(text)
        slug = base_slug
        counter = 1
        
        while self._slug_exists(slug, exclude_id):
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def _slug_exists(self, slug, exclude_id=None):
        """Vérifie si le slug existe déjà"""
        slug_field = getattr(self.Meta, 'slug_field', 'slug')
        qs = self.Meta.model.objects.filter(**{slug_field: slug})
        
        if exclude_id:
            qs = qs.exclude(pk=exclude_id)
        
        return qs.exists()


class RelatedFieldsMixin:
    """Mixin pour champs relationnels optimisés"""
    
    def to_representation(self, instance):
        """Optimise les requêtes pour les champs relationnels"""
        data = super().to_representation(instance)
        
        # Ajouter les champs relationnels si demandés
        expand = self.context.get('expand', [])
        if isinstance(expand, str):
            expand = expand.split(',')
        
        for field_name in expand:
            if hasattr(self, f'get_{field_name}'):
                data[field_name] = getattr(self, f'get_{field_name}')(instance)
        
        return data