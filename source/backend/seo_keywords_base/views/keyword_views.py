# backend/seo_keywords_base/views/keyword_views.py

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Q, Prefetch, Case, When, BooleanField, Exists, OuterRef

from common.views.mixins import (
    BulkActionViewSetMixin, 
    AnalyticsViewSetMixin,
    ExportViewSetMixin
)

from ..models import Keyword
from ..serializers import KeywordSerializer, KeywordListSerializer, KeywordDetailSerializer
from ..filters import KeywordFilter

import logging
logger = logging.getLogger(__name__)

class KeywordViewSet(
    BulkActionViewSetMixin,
    AnalyticsViewSetMixin, 
    ExportViewSetMixin,
    viewsets.ModelViewSet
):
    """
    🔍 ENDPOINT PRINCIPAL UNIFIÉ - TOUTES LES DONNÉES MOTS-CLÉS
    
    Agrège les données de toutes les apps keyword:
    - seo_keywords_base : Données de base
    - seo_keywords_metrics : DA, BL, KD
    - seo_keywords_cocoons : Associations cocons
    - seo_keywords_ppa : Questions PPA
    - seo_keywords_content_types : Types de contenu
    
    Endpoints:
    - GET /keywords/ : Liste unifiée avec tous filtres
    - POST /keywords/ : Création (+ batch support)
    - GET /keywords/{id}/ : Détail complet toutes apps
    - PUT/PATCH /keywords/{id}/ : Mise à jour
    - DELETE /keywords/{id}/ : Suppression cascade
    - GET /keywords/search/ : Recherche rapide
    - GET /keywords/stats/ : Analytics globales
    - POST /keywords/bulk-update/ : Actions masse
    """
    
    queryset = Keyword.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = KeywordFilter
    search_fields = ['keyword']
    ordering_fields = [
        # Base
        'keyword', 'volume', 'search_intent', 'cpc', 'created_at',
        
        # Metrics cross-app (via annotations)
        'da_min', 'da_q1', 'da_median', 'da_q3', 'da_max',
        'bl_min', 'bl_q1', 'bl_median', 'bl_q3', 'bl_max',
        'kdifficulty_normalized',
        
        # Compteurs
        'cocoons_count', 'ppas_count', 'content_types_count'
    ]
    ordering = ['-volume', 'keyword']
    
    def get_serializer_class(self):
        serializer_map = {
            'list': KeywordListSerializer,
            'retrieve': KeywordDetailSerializer,
            'search': KeywordListSerializer,
            'stats': KeywordListSerializer,
        }
        return serializer_map.get(self.action, KeywordSerializer)
    
    def get_queryset(self):
        """
        🎯 REQUÊTE OPTIMISÉE CROSS-APP avec préchargement metrics
        """
        queryset = super().get_queryset()
        
        # 🔥 CRUCIAL : Précharger la relation metrics
        queryset = queryset.select_related('metrics')
        queryset = queryset.prefetch_related('ppa_associations__ppa')
        
        # 📊 ANNOTATIONS DE BASE (toujours)
        queryset = queryset.annotate(
            # Compteurs relations
            cocoons_count=Count('cocoon_associations', distinct=True),
            ppas_count=Count('ppa_associations', distinct=True),
            content_types_count=Count('content_type_associations', distinct=True),
            
            # Flags existence (sans les métriques, maintenant via relation)
            has_ppas=Case(
                When(ppa_associations__isnull=False, then=True),
                default=False,
                output_field=BooleanField()
            ),
            has_content_types=Case(
                When(content_type_associations__isnull=False, then=True),
                default=False,
                output_field=BooleanField()
            )
        )
        
        # 📋 PRÉCHARGEMENTS PAR ACTION
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                # Cocons avec catégories
                Prefetch(
                    'cocoon_associations__cocoon',
                    queryset=self._get_cocoons_queryset()
                ),
                # PPAs avec positions
                Prefetch(
                    'ppa_associations',
                    queryset=self._get_ppas_queryset()
                ),
                # Content types
                'content_type_associations__content_type',
            )
        
        return queryset.distinct()
    def _get_metrics_subquery(self):
        """Subquery pour vérifier existence métriques"""
        try:
            from seo_keywords_metrics.models import KeywordMetrics
            return KeywordMetrics.objects.filter(keyword=OuterRef('pk'))
        except ImportError:
            logger.warning("seo_keywords_metrics app not available")
            return None
    
    def _needs_metrics_annotations(self):
        """Vérifie si les annotations métriques sont nécessaires"""
        request = getattr(self, 'request', None)
        if not request:
            return False
        
        # Si filtrage sur métriques
        metrics_filters = [
            'da_min', 'da_max', 'da_median', 'da_q1', 'da_q3',
            'bl_min', 'bl_max', 'bl_median', 'bl_q1', 'bl_q3',
            'kdifficulty_min', 'kdifficulty_max'
        ]
        
        return any(
            param in request.query_params 
            for param in metrics_filters
        )
    
    def _add_metrics_annotations(self, queryset):
        """Ajoute annotations métriques pour filtrage"""
        try:
            from seo_keywords_metrics.models import KeywordMetrics
            from django.db.models import F, FloatField, Value
            from django.db.models.functions import Cast, Replace
            
            # Sous-requête pour récupérer les métriques
            metrics_subquery = KeywordMetrics.objects.filter(
                keyword=OuterRef('pk')
            )
            
            return queryset.annotate(
                # DA metrics
                da_min=metrics_subquery.values('da_min')[:1],
                da_max=metrics_subquery.values('da_max')[:1],
                da_median=metrics_subquery.values('da_median')[:1],
                da_q1=metrics_subquery.values('da_q1')[:1],
                da_q3=metrics_subquery.values('da_q3')[:1],
                
                # BL metrics  
                bl_min=metrics_subquery.values('bl_min')[:1],
                bl_max=metrics_subquery.values('bl_max')[:1],
                bl_median=metrics_subquery.values('bl_median')[:1],
                bl_q1=metrics_subquery.values('bl_q1')[:1],
                bl_q3=metrics_subquery.values('bl_q3')[:1],
                
                # KD normalisé
                kdifficulty_normalized=Cast(
                    Replace(
                        Replace(
                            metrics_subquery.values('kdifficulty')[:1], 
                            Value('%'), Value('')
                        ),
                        Value(','), Value('.')
                    ),
                    FloatField()
                )
            )
        except ImportError:
            logger.warning("Could not add metrics annotations")
            return queryset
    
    def _get_cocoons_queryset(self):
        """Queryset optimisé pour cocons"""
        try:
            from seo_keywords_cocoons.models import SemanticCocoon
            return SemanticCocoon.objects.select_related().prefetch_related('categories')
        except ImportError:
            return None
    
    def _get_ppas_queryset(self):
        """Queryset optimisé pour PPAs"""
        try:
            from seo_keywords_ppa.models import KeywordPPA
            return KeywordPPA.objects.select_related('ppa').order_by('position')
        except ImportError:
            return None
    
    def list(self, request, *args, **kwargs):
        """Support vérification d'existence + liste normale"""
        
        # 🔍 MODE VÉRIFICATION (comme ancien endpoint)
        keywords_to_check = request.query_params.get('keyword__in')
        if keywords_to_check:
            keywords_list = keywords_to_check.split(',')
            existing = self.get_queryset().filter(
                keyword__in=keywords_list
            ).values('id', 'keyword', 'volume')
            
            existing_keywords = list(existing)
            existing_texts = [k['keyword'] for k in existing_keywords]
            missing = [k for k in keywords_list if k not in existing_texts]
            
            return Response({
                'count': len(existing_keywords),
                'results': existing_keywords,
                'missing': missing,
                'checked': len(keywords_list)
            })
        
        # 📋 MODE LISTE NORMALE
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """Détail enrichi avec toutes les relations cross-app"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Données de base
        data = serializer.data
        
        # 📊 ENRICHISSEMENT CROSS-APP
        try:
            # Stats cocons
            data['cocoons_stats'] = self._get_cocoons_stats(instance)
            
            # Stats PPAs
            data['ppas_stats'] = self._get_ppas_stats(instance)
            
            # Métriques complètes si disponibles
            if hasattr(instance, 'metrics'):
                data['metrics_complete'] = True
            
        except Exception as e:
            logger.error(f"Error enriching keyword {instance.id}: {e}")
        
        return Response(data)
    
    def _get_cocoons_stats(self, keyword):
        """Stats des cocons pour ce keyword"""
        try:
            cocoons = keyword.cocoon_associations.all()
            return {
                'total_cocoons': cocoons.count(),
                'cocoons_with_categories': cocoons.filter(
                    cocoon__categories__isnull=False
                ).distinct().count()
            }
        except:
            return {'total_cocoons': 0}
    
    def _get_ppas_stats(self, keyword):
        """Stats des PPAs pour ce keyword"""
        try:
            ppas = keyword.ppa_associations.all()
            positions = list(ppas.values_list('position', flat=True))
            return {
                'total_ppas': len(positions),
                'positions': positions,
                'avg_position': sum(positions) / len(positions) if positions else None
            }
        except:
            return {'total_ppas': 0}
    
    def create(self, request, *args, **kwargs):
        """Support création batch + simple"""
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    'created': len(serializer.data),
                    'results': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        
        return super().create(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        GET /keywords/search/?q=term&limit=10
        
        Recherche rapide optimisée pour autocomplétion
        """
        query = request.query_params.get('q', '')
        limit = int(request.query_params.get('limit', 10))
        
        if len(query) < 2:
            return Response({'results': []})
        
        queryset = self.get_queryset().filter(
            keyword__icontains=query
        ).annotate(
            # Annotations légères pour search
            cocoons_count=Count('cocoon_associations'),
            has_metrics=Exists(self._get_metrics_subquery())
        )[:limit]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})
    
    @action(detail=False, methods=['get'])
    def export_with_relations(self, request):
        """Export CSV enrichi avec données cross-app"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # TODO: Implémenter export CSV avec toutes les relations
        return Response({
            'message': 'Export functionality coming soon',
            'total_keywords': queryset.count()
        })