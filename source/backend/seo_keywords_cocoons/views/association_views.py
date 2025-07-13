# backend/seo_keywords_cocoons/views/association_views.py

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

# Local imports
from ..models import CocoonKeyword
from ..serializers import CocoonKeywordSerializer, CocoonKeywordListSerializer

import logging
logger = logging.getLogger(__name__)

class CocoonKeywordViewSet(viewsets.ModelViewSet):
    """
    GESTION ASSOCIATIONS COCOON-KEYWORD - CRUD OPTIMISÉ
    
    Endpoints RESTful :
    - GET /seo/cocoons/associations/          # Liste avec filtres
    - POST /seo/cocoons/associations/         # Création
    - GET /seo/cocoons/associations/{id}/     # Détail
    - PUT /seo/cocoons/associations/{id}/     # Update
    - DELETE /seo/cocoons/associations/{id}/  # Delete
    """
    
    queryset = CocoonKeyword.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    ordering = ['cocoon__name', '-keyword__volume']
    
    def get_serializer_class(self):
        """Serializer par action"""
        if self.action == 'list':
            return CocoonKeywordListSerializer
        return CocoonKeywordSerializer
    
    def get_queryset(self):
        """Optimisation requêtes avec filtres dynamiques"""
        queryset = super().get_queryset().select_related(
            'cocoon', 'keyword'
        )
        
        # Filtres via query params
        cocoon_id = self.request.query_params.get('cocoon')
        keyword_id = self.request.query_params.get('keyword')
        search = self.request.query_params.get('search')
        
        if cocoon_id:
            try:
                queryset = queryset.filter(cocoon_id=int(cocoon_id))
            except (ValueError, TypeError):
                logger.warning(f"Invalid cocoon_id filter: {cocoon_id}")
        
        if keyword_id:
            try:
                queryset = queryset.filter(keyword_id=int(keyword_id))
            except (ValueError, TypeError):
                logger.warning(f"Invalid keyword_id filter: {keyword_id}")
        
        if search:
            queryset = queryset.filter(
                Q(cocoon__name__icontains=search) |
                Q(keyword__keyword__icontains=search)
            )
        
        return queryset.distinct()
    
    def create(self, request, *args, **kwargs):
        """Création avec gestion d'erreurs robuste"""
        try:
            # Vérification unicité avant création
            cocoon_id = request.data.get('cocoon')
            keyword_id = request.data.get('keyword')
            
            if cocoon_id and keyword_id:
                existing = CocoonKeyword.objects.filter(
                    cocoon_id=cocoon_id,
                    keyword_id=keyword_id
                ).exists()
                
                if existing:
                    return Response(
                        {'error': 'Cette association existe déjà'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            response = super().create(request, *args, **kwargs)
            logger.info(f"Association created: cocoon {cocoon_id} + keyword {keyword_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error creating association: {e}", exc_info=True)
            return Response(
                {'error': 'Erreur lors de la création de l\'association'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """Suppression avec audit"""
        try:
            association = self.get_object()
            cocoon_name = association.cocoon.name
            keyword_text = association.keyword.keyword
            
            result = super().destroy(request, *args, **kwargs)
            
            logger.info(f"Association deleted: {cocoon_name} - {keyword_text} by user {request.user.id}")
            return result
            
        except Exception as e:
            logger.error(f"Error deleting association {kwargs.get('pk')}: {e}", exc_info=True)
            return Response(
                {'error': 'Erreur lors de la suppression'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )