# backend/seo_keywords_ppa/views/ppa_views.py

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

# Local imports
from ..models import PPA, KeywordPPA
from ..serializers import (
    PPASerializer,
    PPAListSerializer,
    KeywordPPASerializer,
    KeywordPPAListSerializer
)
from ..filters import PPAFilter, KeywordPPAFilter


class PPAViewSet(viewsets.ModelViewSet):
    """
    GESTION DES QUESTIONS PPA - CRUD UNIQUEMENT
    
    Endpoints RESTful :
    - GET /seo/ppa/questions/        # Liste
    - POST /seo/ppa/questions/       # Création
    - GET /seo/ppa/questions/{id}/   # Détail
    - PUT /seo/ppa/questions/{id}/   # Update
    - DELETE /seo/ppa/questions/{id}/# Delete
    """
    
    queryset = PPA.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PPAFilter
    ordering = ['question']
    
    def get_serializer_class(self):
        """Serializer par action selon pattern obligatoire"""
        if self.action == 'list':
            return PPAListSerializer
        return PPASerializer
    
    def get_queryset(self):
        """Optimisation requêtes avec annotations"""
        return super().get_queryset().annotate(
            keywords_count=Count('keyword_associations', distinct=True)
        )


class KeywordPPAViewSet(viewsets.ModelViewSet):
    """
    GESTION ASSOCIATIONS KEYWORD-PPA - CRUD UNIQUEMENT
    
    Endpoints RESTful :
    - GET /seo/ppa/associations/        # Liste
    - POST /seo/ppa/associations/       # Création
    - GET /seo/ppa/associations/{id}/   # Détail
    - PUT /seo/ppa/associations/{id}/   # Update
    - DELETE /seo/ppa/associations/{id}/# Delete
    """
    
    queryset = KeywordPPA.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = KeywordPPAFilter
    ordering = ['keyword__keyword', 'position']
    
    def get_serializer_class(self):
        """Serializer par action selon pattern obligatoire"""
        if self.action == 'list':
            return KeywordPPAListSerializer
        return KeywordPPASerializer
    
    def get_queryset(self):
        """Optimisation requêtes avec select_related"""
        return super().get_queryset().select_related(
            'keyword', 'ppa'
        )