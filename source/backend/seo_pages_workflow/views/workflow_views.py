# backend/seo_pages_workflow/views/workflow_views.py

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone

from .base_views import PageWorkflowBaseViewSet
from ..models import PageStatus, PageWorkflowHistory, PageScheduling
from ..serializers import (
    PageStatusSerializer,
    PageStatusUpdateSerializer,
    PageWorkflowHistorySerializer,
    PageSchedulingSerializer,
    PageWorkflowDashboardSerializer
)

class PageStatusViewSet(PageWorkflowBaseViewSet):
    """
    ViewSet pour statuts workflow des pages
    
    Endpoints RESTful :
    - GET /status/                # Liste
    - GET /status/{id}/           # Détail
    - PUT /status/{id}/           # Update statut
    - GET /status/dashboard/      # Dashboard workflow
    - POST /status/bulk-update/   # Mise à jour en masse
    """
    
    serializer_class = PageStatusSerializer
    filterset_fields = ['status', 'page__website']
    
    def get_queryset(self):
        """Le BrandScopedViewSetMixin gère automatiquement le filtrage"""
        return PageStatus.objects.select_related(
            'page',
            'page__website',
            'page__website__brand',
            'status_changed_by'
        )
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return PageStatusUpdateSerializer
        return PageStatusSerializer
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Dashboard workflow avec statistiques"""
        website_id = request.query_params.get('website_id')
        queryset = self.get_queryset()
        
        if website_id:
            queryset = queryset.filter(page__website_id=website_id)
        
        # Stats par statut
        status_stats = queryset.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        pages_by_status = {
            item['status']: item['count'] for item in status_stats
        }
        
        # ✅ CORRECTION : Filter AVANT slice
        recent_changes_query = PageWorkflowHistory.objects.select_related(
            'page', 'changed_by'
        ).order_by('-created_at')
        
        if website_id:
            recent_changes_query = recent_changes_query.filter(page__website_id=website_id)
        
        recent_changes = recent_changes_query[:10]
        
        # ✅ CORRECTION : Même pattern pour scheduled_pages
        scheduled_pages_query = PageScheduling.objects.filter(
            scheduled_publish_date__isnull=False
        ).select_related('page')
        
        if website_id:
            scheduled_pages_query = scheduled_pages_query.filter(page__website_id=website_id)
        
        scheduled_pages = scheduled_pages_query[:10]
        
        # Pages prêtes à publier
        ready_to_publish = queryset.filter(status='approved').count()
        
        # ✅ CORRECTION PRINCIPALE : Retourner directement les données
        # Au lieu d'utiliser PageWorkflowDashboardSerializer qui cause l'erreur
        dashboard_data = {
            'total_pages': queryset.count(),
            'pages_by_status': pages_by_status,
            'recent_changes': PageWorkflowHistorySerializer(recent_changes, many=True).data,
            'scheduled_pages': PageSchedulingSerializer(scheduled_pages, many=True).data,
            'pages_ready_to_publish': ready_to_publish
        }
        
        # ❌ PROBLÉMATIQUE : Utiliser le serializer avec des données déjà sérialisées
        # serializer = PageWorkflowDashboardSerializer(dashboard_data)
        # return Response(serializer.data)
        
        # ✅ SOLUTION : Retourner directement les données
        return Response(dashboard_data)
    
    
    
    
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Mise à jour en masse des statuts"""
        page_ids = request.data.get('page_ids', [])
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if not page_ids or not new_status:
            return Response(
                {'error': 'page_ids et status requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_statuses = self.get_queryset().filter(page_id__in=page_ids)
        updated_count = 0
        errors = []
        
        for page_status in updated_statuses:
            try:
                # Vérifier transition autorisée
                if new_status in page_status.get_next_possible_statuses():
                    page_status.update_status(new_status, request.user, notes)
                    updated_count += 1
                else:
                    errors.append({
                        'page_id': page_status.page.id,
                        'current_status': page_status.status,
                        'error': f'Transition vers {new_status} non autorisée'
                    })
            except Exception as e:
                errors.append({
                    'page_id': page_status.page.id,
                    'error': str(e)
                })
        
        return Response({
            'updated_count': updated_count,
            'total_requested': len(page_ids),
            'errors': errors
        })

class PageWorkflowHistoryViewSet(PageWorkflowBaseViewSet):
    """
    ViewSet pour historique workflow (Read-only)
    
    Endpoints RESTful :
    - GET /history/               # Liste
    - GET /history/{id}/          # Détail
    """
    
    serializer_class = PageWorkflowHistorySerializer
    http_method_names = ['get']  # Read-only
    filterset_fields = ['page', 'old_status', 'new_status', 'changed_by']
    
    def get_queryset(self):
        """Le BrandScopedViewSetMixin gère automatiquement le filtrage"""
        return PageWorkflowHistory.objects.select_related(
            'page',
            'page__website',
            'page__website__brand',
            'changed_by'
        )

class PageSchedulingViewSet(PageWorkflowBaseViewSet):
    """
    ViewSet pour programmation publication
    
    Endpoints RESTful :
    - GET /scheduling/            # Liste
    - POST /scheduling/           # Création
    - PUT /scheduling/{id}/       # Update
    - POST /scheduling/publish-ready/ # Publier pages prêtes
    """
    
    serializer_class = PageSchedulingSerializer
    
    def get_queryset(self):
        """Le BrandScopedViewSetMixin gère automatiquement le filtrage"""
        return PageScheduling.objects.select_related(
            'page',
            'page__website',
            'page__website__brand'
        )
    
    @action(detail=False, methods=['post'])
    def publish_ready(self, request):
        """Publication automatique des pages prêtes"""
        ready_schedules = self.get_queryset().filter(
            scheduled_publish_date__lte=timezone.now(),
            auto_publish=True,
            page__workflow_status__status='scheduled'
        )
        
        published_count = 0
        errors = []
        
        for schedule in ready_schedules:
            try:
                # Changer le statut en published
                page_status = schedule.page.workflow_status
                page_status.update_status('published', None, 'Publication automatique')
                published_count += 1
            except Exception as e:
                errors.append({
                    'page_id': schedule.page.id,
                    'page_title': schedule.page.title,
                    'error': str(e)
                })
        
        return Response({
            'published_count': published_count,
            'total_ready': ready_schedules.count(),
            'errors': errors
        })