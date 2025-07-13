# backend/seo_websites_core/views/website_views.py

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, F, Q, Min, Max
from django.db import models

from .base_views import WebsiteCoreBaseViewSet
from ..models import Website
from ..serializers import (
    WebsiteListSerializer,
    WebsiteDetailSerializer,
    WebsiteCreateSerializer
)
from ..filters import WebsiteFilter

class WebsiteViewSet(WebsiteCoreBaseViewSet):
    """
    ViewSet pour gestion des sites web avec filtrage cross-app ultra-avancé
    
    Endpoints RESTful :
    - GET /websites/              # Liste optimisée + filtres cross-app
    - POST /websites/             # Création
    - GET /websites/{id}/         # Détail
    - PUT /websites/{id}/         # Update
    - DELETE /websites/{id}/      # Delete
    - GET /websites/{id}/stats/   # Stats site
    
    Features :
    - 54 filtres cross-app disponibles
    - Optimisations conditionnelles selon filtres actifs
    - Stats intelligentes dans les réponses
    - Performance optimisée avec préchargements ciblés
    """
    
    queryset = Website.objects.all()
    filterset_class = WebsiteFilter
    search_fields = ['name', 'url', 'brand__name']
    ordering_fields = ['name', 'created_at', 'domain_authority', 'pages_count']
    
    def get_queryset(self):
        """
        🔥 QUERYSET INTELLIGENT : Optimisations conditionnelles selon filtres
        
        Performance Strategy:
        - Base: select_related('brand') + pages_count (TOUJOURS via parent)
        - Keywords: + prefetch keywords SI filtres keywords actifs  
        - SEO: + prefetch seo_config SI filtres SEO actifs
        - Workflow: + prefetch workflow_status SI filtres workflow actifs
        - Layout: + prefetch layout/sections SI filtres layout actifs
        - Categorization: + prefetch categories SI filtres catégorie actifs
        
        Résultat: 0 N+1 queries même avec filtres complexes
        """
        queryset = super().get_queryset()
        
        # Détection filtres cross-app pour optimisations ciblées
        request_params = getattr(self.request, 'GET', {})
        
        # 🔥 KEYWORDS OPTIMIZATION
        keywords_filters = [
            'has_keywords', 'total_keywords_count', 'unique_keywords_count',
            'keywords_coverage', 'has_primary_keywords', 'ai_keywords_ratio',
            'avg_keyword_volume'
        ]
        if any(param in request_params for param in keywords_filters):
            queryset = queryset.prefetch_related(
                'pages__page_keywords__keyword'
            ).annotate(
                total_keywords=Count('pages__page_keywords', distinct=True),
                unique_keywords=Count('pages__page_keywords__keyword', distinct=True)
            )
        
        # 🔥 SEO OPTIMIZATION  
        seo_filters = [
            'has_seo_config', 'has_featured_images', 'avg_sitemap_priority',
            'excluded_from_sitemap_count', 'meta_description_coverage'
        ]
        if any(param in request_params for param in seo_filters):
            queryset = queryset.prefetch_related(
                'pages__seo_config'
            ).annotate(
                avg_sitemap_priority=Avg('pages__seo_config__sitemap_priority'),
                excluded_pages=Count(
                    'pages',
                    filter=Q(pages__seo_config__exclude_from_sitemap=True),
                    distinct=True
                )
            )
        
        # 🔥 WORKFLOW OPTIMIZATION
        workflow_filters = [
            'has_published_pages', 'has_draft_pages', 'has_scheduled_pages',
            'published_pages_count', 'publication_ratio'
        ]
        if any(param in request_params for param in workflow_filters):
            queryset = queryset.prefetch_related(
                'pages__workflow_status'
            ).annotate(
                published_pages=Count(
                    'pages',
                    filter=Q(pages__workflow_status__status='published'),
                    distinct=True
                ),
                draft_pages=Count(
                    'pages',
                    filter=Q(pages__workflow_status__status='draft'),
                    distinct=True
                )
            )
        
        # 🔥 LAYOUT OPTIMIZATION
        layout_filters = [
            'has_page_builder', 'sections_count', 'layout_coverage',
            'popular_section_types', 'render_strategy'
        ]
        if any(param in request_params for param in layout_filters):
            queryset = queryset.prefetch_related(
                'pages__layout_config',
                'pages__sections'
            ).annotate(
                total_sections=Count('pages__sections', distinct=True),
                pages_with_layout=Count(
                    'pages',
                    filter=Q(pages__layout_config__isnull=False),
                    distinct=True
                )
            )
        
        # 🔥 CATEGORIZATION OPTIMIZATION
        category_filters = [
            'website_category', 'primary_category', 'categorization_source',
            'has_primary_category', 'da_above_category', 'pages_above_category',
            'performance_vs_category'
        ]
        if any(param in request_params for param in category_filters):
            queryset = queryset.prefetch_related(
                'categorizations__category'
            )
        
        return queryset
    
    def get_serializer_class(self):
        """Serializer par action avec optimisations"""
        if self.action == 'list':
            return WebsiteListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return WebsiteCreateSerializer
        return WebsiteDetailSerializer
    
    def list(self, request, *args, **kwargs):
        """
        🔥 LIST ENRICHIE : Stats conditionnelles + réponse intelligente
        
        Comportements :
        - GET /websites/ = Réponse standard avec pagination
        - GET /websites/?include_stats=true = + Stats globales dans response
        - GET /websites/?[filtres_cross_app] = + Métriques spécifiques automatiques
        - GET /websites/?has_keywords=true&avg_sitemap_priority_min=0.6 = + Stats keywords + SEO
        
        Performance : Stats calculées en 1 query supplémentaire maximum
        """
        # 1. Filtrage standard
        queryset = self.filter_queryset(self.get_queryset())
        
        # 2. Détection enrichissement demandé
        include_stats = request.GET.get('include_stats', '').lower() == 'true'
        has_filters = len([k for k, v in request.GET.items() if v and k not in ['page', 'page_size']]) > 0
        
        # 3. Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            # 4. Enrichissement conditionnel
            if include_stats or has_filters:
                response.data['search_stats'] = self._calculate_search_stats(
                    queryset, request.GET
                )
            
            return response
        
        # 5. Sans pagination
        serializer = self.get_serializer(queryset, many=True)
        response_data = {'results': serializer.data}
        
        if include_stats or has_filters:
            response_data['search_stats'] = self._calculate_search_stats(
                queryset, request.GET
            )
        
        return Response(response_data)
    
    def _calculate_search_stats(self, queryset, params):
        """
        🔥 STATS INTELLIGENTES selon filtres appliqués
        
        Logique :
        - Stats de base : TOUJOURS (DA moyen, pages moyennes, ranges)
        - Stats keywords : SI filtres keywords actifs
        - Stats SEO : SI filtres SEO actifs  
        - Stats workflow : SI filtres workflow actifs
        
        Performance : 1 seule query aggregate() supplémentaire
        """
        count = queryset.count()
        if count == 0:
            return {
                'total_found': 0, 
                'filters_applied': len([k for k, v in params.items() if v and k not in ['page', 'page_size']]),
                'message': 'Aucun résultat trouvé avec ces filtres'
            }
        
        # Stats de base (toujours calculées)
        base_stats = queryset.aggregate(
            avg_da=Avg('domain_authority'),
            avg_pages=Avg('pages_count'),
            min_da=Min('domain_authority'),
            max_da=Max('domain_authority')
        )
        
        stats = {
            'total_found': count,
            'filters_applied': len([k for k, v in params.items() if v and k not in ['page', 'page_size']]),
            'avg_domain_authority': round(base_stats['avg_da'] or 0, 1),
            'avg_pages_per_site': round(base_stats['avg_pages'] or 0, 1),
            'da_range': {
                'min': base_stats['min_da'] or 0,
                'max': base_stats['max_da'] or 0
            }
        }
        
        # Stats conditionnelles selon filtres actifs
        
        # Keywords stats si filtres keywords
        keywords_filters = ['has_keywords', 'total_keywords_count', 'ai_keywords_ratio']
        if any(param in params for param in keywords_filters):
            try:
                kw_stats = queryset.aggregate(
                    avg_total_keywords=Avg('total_keywords'),
                    avg_unique_keywords=Avg('unique_keywords')
                )
                stats['keywords_stats'] = {
                    'avg_total_keywords': round(kw_stats['avg_total_keywords'] or 0, 1),
                    'avg_unique_keywords': round(kw_stats['avg_unique_keywords'] or 0, 1),
                    'message': f'Moyennes calculées sur {count} sites avec mots-clés'
                }
            except:
                pass
        
        # SEO stats si filtres SEO
        seo_filters = ['avg_sitemap_priority', 'has_featured_images']
        if any(param in params for param in seo_filters):
            try:
                seo_stats = queryset.aggregate(
                    avg_sitemap_prio=Avg('avg_sitemap_priority'),
                    avg_excluded=Avg('excluded_pages')
                )
                stats['seo_stats'] = {
                    'avg_sitemap_priority': round(seo_stats['avg_sitemap_prio'] or 0, 2),
                    'avg_excluded_pages': round(seo_stats['avg_excluded'] or 0, 1),
                    'message': f'Métriques SEO sur {count} sites'
                }
            except:
                pass
        
        # Workflow stats si filtres workflow
        workflow_filters = ['publication_ratio', 'has_published_pages']
        if any(param in params for param in workflow_filters):
            try:
                workflow_stats = queryset.aggregate(
                    avg_published=Avg('published_pages'),
                    avg_drafts=Avg('draft_pages')
                )
                stats['workflow_stats'] = {
                    'avg_published_pages': round(workflow_stats['avg_published'] or 0, 1),
                    'avg_draft_pages': round(workflow_stats['avg_drafts'] or 0, 1),
                    'message': f'Workflow stats sur {count} sites'
                }
            except:
                pass
        
        return stats
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Statistiques détaillées d'un site spécifique
        
        GET /websites/{id}/stats/
        
        Retourne :
        - Métriques de base du site
        - Répartition des pages par type/statut
        - Métriques concurrence
        - Ratios de performance si données disponibles
        """
        website = self.get_object()
        
        # Import local pour éviter circular import
        try:
            from seo_pages_content.models import Page
            from seo_pages_workflow.models import PageStatus
            
            pages = Page.objects.filter(website=website)
            
            stats = {
                'website_id': website.id,
                'website_name': website.name,
                'website_url': website.url,
                'brand_name': website.brand.name,
                'total_pages': pages.count(),
                'pages_by_type': dict(
                    pages.values('page_type').annotate(count=Count('id')).values_list('page_type', 'count')
                ),
                'pages_by_status': {},
                'domain_authority': website.domain_authority,
                'competitor_metrics': {
                    'max_backlinks': website.max_competitor_backlinks,
                    'max_kd': website.max_competitor_kd
                }
            }
            
            # Stats statuts si disponibles
            try:
                status_stats = PageStatus.objects.filter(page__website=website).values(
                    'status'
                ).annotate(count=Count('id'))
                stats['pages_by_status'] = {
                    item['status']: item['count'] for item in status_stats
                }
                
                # Ratios de performance
                total_pages = stats['total_pages']
                if total_pages > 0:
                    published_count = stats['pages_by_status'].get('published', 0)
                    stats['performance_ratios'] = {
                        'publication_rate': round(published_count / total_pages, 2),
                        'completion_rate': round((total_pages - stats['pages_by_status'].get('draft', 0)) / total_pages, 2)
                    }
            except:
                pass
                
        except ImportError:
            # Apps pas disponibles
            stats = {
                'website_id': website.id,
                'website_name': website.name,
                'website_url': website.url,
                'brand_name': website.brand.name,
                'domain_authority': website.domain_authority,
                'competitor_metrics': {
                    'max_backlinks': website.max_competitor_backlinks,
                    'max_kd': website.max_competitor_kd
                },
                'message': 'Stats détaillées nécessitent les apps pages_content et workflow'
            }
        
        return Response(stats)