# backend/seo_keywords_content_types/views/content_type_views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count

# Local imports
from ..models import ContentType, KeywordContentType
from ..serializers import (
    ContentTypeSerializer,
    ContentTypeListSerializer,
    KeywordContentTypeSerializer,
    KeywordContentTypeListSerializer
)


class ContentTypeViewSet(viewsets.ModelViewSet):
    """
    GESTION DES TYPES DE CONTENU - CRUD UNIQUEMENT
    
    Endpoints RESTful :
    - GET /seo/content-types/types/        # Liste
    - POST /seo/content-types/types/       # Création
    - GET /seo/content-types/types/{id}/   # Détail
    - PUT /seo/content-types/types/{id}/   # Update
    - DELETE /seo/content-types/types/{id}/# Delete
    """
    
    queryset = ContentType.objects.all()
    permission_classes = [IsAuthenticated]
    ordering = ['name']
    
    def get_serializer_class(self):
        """Serializer par action selon pattern obligatoire"""
        if self.action == 'list':
            return ContentTypeListSerializer
        return ContentTypeSerializer
    
    def get_queryset(self):
        """Optimisation requêtes avec annotations"""
        return super().get_queryset().annotate(
            keywords_count=Count('keyword_associations', distinct=True)
        )


class KeywordContentTypeViewSet(viewsets.ModelViewSet):
    """
    GESTION ASSOCIATIONS KEYWORD-CONTENT TYPE - CRUD UNIQUEMENT
    
    Endpoints RESTful :
    - GET /seo/content-types/associations/        # Liste
    - POST /seo/content-types/associations/       # Création
    - GET /seo/content-types/associations/{id}/   # Détail
    - PUT /seo/content-types/associations/{id}/   # Update
    - DELETE /seo/content-types/associations/{id}/# Delete
    """
    
    queryset = KeywordContentType.objects.all()
    permission_classes = [IsAuthenticated]
    ordering = ['keyword__keyword', 'priority']
    
    def get_serializer_class(self):
        """Serializer par action selon pattern obligatoire"""
        if self.action == 'list':
            return KeywordContentTypeListSerializer
        return KeywordContentTypeSerializer
    
    def get_queryset(self):
        """Optimisation requêtes avec select_related"""
        return super().get_queryset().select_related(
            'keyword', 'content_type'
        )