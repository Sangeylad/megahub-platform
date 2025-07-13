# backend/seo_pages_hierarchy/serializers/hierarchy_serializers.py

from rest_framework import serializers
from django.db import IntegrityError

from .base_serializers import PageHierarchyBaseSerializer
from ..models import PageHierarchy, PageBreadcrumb

class PageHierarchySerializer(PageHierarchyBaseSerializer):
    """Serializer hiérarchie des pages avec gestion des contraintes"""
    
    page_title = serializers.CharField(source='page.title', read_only=True)
    page_url = serializers.CharField(source='page.url_path', read_only=True)
    parent_title = serializers.CharField(source='parent.title', read_only=True)
    level = serializers.SerializerMethodField()
    root_page = serializers.SerializerMethodField()
    
    class Meta:
        model = PageHierarchy
        fields = [
            'id', 'page', 'page_title', 'page_url',
            'parent', 'parent_title', 'level', 'root_page'
        ]
    
    def get_level(self, obj):
        return obj.get_level()
    
    def get_root_page(self, obj):
        root = obj.get_root_page()
        return {
            'id': root.id,
            'title': root.title,
            'url_path': root.url_path
        }
    
    def create(self, validated_data):
        """Création avec gestion gracieuse des contraintes d'unicité"""
        try:
            return super().create(validated_data)
        except IntegrityError:
            # Si hiérarchie existe déjà, la retourner au lieu d'erreur
            page = validated_data['page']
            existing = PageHierarchy.objects.filter(page=page).first()
            if existing:
                return existing
            raise
    
    def validate(self, data):
        page = data.get('page')
        parent = data.get('parent')
        
        # 🆕 Vérifier si une hiérarchie existe déjà pour cette page
        if page and not self.instance:  # Seulement pour création
            existing = PageHierarchy.objects.filter(page=page).first()
            if existing:
                # Ne pas lever d'erreur, juste informer
                self._existing_hierarchy = existing
        
        if page and parent:
            # Éviter auto-référence
            if page == parent:
                raise serializers.ValidationError({
                    'parent': 'Une page ne peut pas être son propre parent'
                })
            
            # Vérifier que parent n'est pas déjà enfant de page
            current = parent
            while hasattr(current, 'hierarchy') and current.hierarchy.parent:
                current = current.hierarchy.parent
                if current == page:
                    raise serializers.ValidationError({
                        'parent': 'Relation circulaire détectée'
                    })
        
        return data

# 🆕 AJOUTER un serializer de création spécialisé
class PageHierarchyCreateSerializer(PageHierarchyBaseSerializer):
    """Serializer spécialisé pour création avec gestion robuste"""
    
    class Meta:
        model = PageHierarchy
        fields = ['page', 'parent']
    
    def create(self, validated_data):
        """Création avec get_or_create pour éviter les erreurs"""
        page = validated_data['page']
        parent = validated_data.get('parent')
        
        # Utiliser get_or_create pour éviter les contraintes d'unicité
        hierarchy, created = PageHierarchy.objects.get_or_create(
            page=page,
            defaults={'parent': parent}
        )
        
        # Si existe déjà et parent différent, mettre à jour
        if not created and hierarchy.parent != parent:
            hierarchy.parent = parent
            hierarchy.save(update_fields=['parent'])
        
        return hierarchy

class PageHierarchyTreeSerializer(PageHierarchyBaseSerializer):
    """Serializer pour arbre hiérarchique complet"""
    
    page_title = serializers.CharField(source='page.title', read_only=True)
    page_url = serializers.CharField(source='page.url_path', read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = PageHierarchy
        fields = ['page', 'page_title', 'page_url', 'children']
    
    def get_children(self, obj):
        # Récupérer les enfants directs
        children_pages = obj.page.children_hierarchy.all()
        children_hierarchies = [child.hierarchy for child in children_pages if hasattr(child, 'hierarchy')]
        return PageHierarchyTreeSerializer(children_hierarchies, many=True).data

class PageBreadcrumbSerializer(PageHierarchyBaseSerializer):
    """Serializer fil d'Ariane"""
    
    page_title = serializers.CharField(source='page.title', read_only=True)
    breadcrumb = serializers.JSONField(source='breadcrumb_json', read_only=True)
    
    class Meta:
        model = PageBreadcrumb
        fields = ['id', 'page', 'page_title', 'breadcrumb', 'updated_at']