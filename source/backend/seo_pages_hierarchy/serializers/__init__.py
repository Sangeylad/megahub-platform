# backend/seo_pages_hierarchy/serializers/__init__.py

from .hierarchy_serializers import (
    PageHierarchySerializer,
    PageHierarchyCreateSerializer,  # 🆕 AJOUTER cette ligne
    PageHierarchyTreeSerializer,
    PageBreadcrumbSerializer
)

__all__ = [
    'PageHierarchySerializer',
    'PageHierarchyCreateSerializer',  # 🆕 AJOUTER cette ligne
    'PageHierarchyTreeSerializer', 
    'PageBreadcrumbSerializer'
]