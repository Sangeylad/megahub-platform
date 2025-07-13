# backend/blog_collections/serializers/__init__.py

from .collection_serializers import (
    BlogCollectionSerializer, 
    BlogCollectionItemSerializer,
    BlogCollectionManagementSerializer  # 🔧 MANQUAIT !
)

__all__ = [
    'BlogCollectionSerializer',
    'BlogCollectionItemSerializer', 
    'BlogCollectionManagementSerializer',  # 🔧 AJOUTER
]