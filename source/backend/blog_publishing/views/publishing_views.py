# backend/blog_publishing/views/publishing_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from common.views.mixins import BrandScopedViewSetMixin, BulkActionViewSetMixin
from rest_framework.permissions import IsAuthenticated
from common.permissions.business_permissions import IsBrandMember, IsBrandAdmin
from ..models import BlogPublishingStatus, BlogScheduledPublication
from ..serializers import BlogPublishingStatusSerializer, BlogScheduledPublicationSerializer


class BlogPublishingStatusViewSet(BrandScopedViewSetMixin, BulkActionViewSetMixin, viewsets.ModelViewSet):
    """Workflow publication avec dashboard"""
    queryset = BlogPublishingStatus.objects.select_related(
        'article', 'article__page', 'article__primary_author', 'approved_by'
    )
    serializer_class = BlogPublishingStatusSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'is_featured', 'is_premium', 'is_evergreen']
    ordering_fields = ['created_at', 'published_date', 'scheduled_date']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Permissions par action"""
        if self.action in ['approve', 'bulk_approve']:
            return [IsAuthenticated(), IsBrandAdmin()]
        return super().get_permissions() 
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Dashboard éditorial complet"""
        queryset = self.get_queryset()
        
        stats = {
            'draft': queryset.filter(status='draft').count(),
            'pending_review': queryset.filter(status='pending_review').count(),
            'approved': queryset.filter(status='approved').count(),
            'scheduled': queryset.filter(status='scheduled').count(),
            'published': queryset.filter(status='published').count(),
            'total': queryset.count()
        }
        
        # Articles en attente de review
        pending_review = queryset.filter(status='pending_review').order_by('submitted_for_review_at')[:10]
        pending_serializer = self.get_serializer(pending_review, many=True)
        
        # Articles programmés prochains
        upcoming_scheduled = queryset.filter(
            status='scheduled',
            scheduled_date__gte=timezone.now()
        ).order_by('scheduled_date')[:5]
        scheduled_serializer = self.get_serializer(upcoming_scheduled, many=True)
        
        # Articles récemment publiés
        recent_published = queryset.filter(status='published').order_by('-published_date')[:5]
        published_serializer = self.get_serializer(recent_published, many=True)
        
        return Response({
            'stats': stats,
            'pending_review': pending_serializer.data,
            'upcoming_scheduled': scheduled_serializer.data,
            'recent_published': published_serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approuver un article (admin seulement)"""
        status_obj = self.get_object()
        
        if status_obj.status != 'pending_review':
            return Response(
                {'error': 'Article doit être en attente de relecture'}, 
                status=400
            )
        
        status_obj.status = 'approved'
        status_obj.approved_at = timezone.now()
        status_obj.approved_by = request.user
        status_obj.save(update_fields=['status', 'approved_at', 'approved_by'])
        
        return Response({
            'message': 'Article approuvé',
            'approved_at': status_obj.approved_at,
            'approved_by': status_obj.approved_by.get_full_name()
        })
    
    @action(detail=True, methods=['post'])
    def publish_now(self, request, pk=None):
        """Publication immédiate"""
        status_obj = self.get_object()
        
        if not status_obj.can_be_published():
            return Response(
                {'error': 'Article ne peut pas être publié'}, 
                status=400
            )
        
        status_obj.status = 'published'
        status_obj.published_date = timezone.now()
        status_obj.last_published_date = timezone.now()
        status_obj.save(update_fields=['status', 'published_date', 'last_published_date'])
        
        # Synchro avec Page
        status_obj.article.page.status = 'published'
        status_obj.article.page.save(update_fields=['status'])
        
        return Response({
            'message': 'Article publié immédiatement',
            'published_date': status_obj.published_date
        })
    
    @action(detail=False, methods=['post'])
    def bulk_approve(self, request):
        """Approbation en masse"""
        article_ids = request.data.get('article_ids', [])
        if not article_ids:
            return Response({'error': 'article_ids required'}, status=400)
        
        updated = self.get_queryset().filter(
            article_id__in=article_ids,
            status='pending_review'
        ).update(
            status='approved',
            approved_at=timezone.now(),
            approved_by=request.user
        )
        
        return Response({
            'message': f'{updated} articles approuvés',
            'approved_count': updated
        })


class BlogScheduledPublicationViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """Publications programmées avec exécution"""
    queryset = BlogScheduledPublication.objects.select_related(
        'article', 'article__page', 'scheduled_by'
    )
    serializer_class = BlogScheduledPublicationSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['execution_status']
    ordering_fields = ['scheduled_for', 'created_at']
    ordering = ['scheduled_for']
    
    @action(detail=False, methods=['get'])
    def ready_for_execution(self, request):
        """Publications prêtes à exécuter"""
        ready_publications = self.get_queryset().filter(
            execution_status='pending',
            scheduled_for__lte=timezone.now()
        )
        
        serializer = self.get_serializer(ready_publications, many=True)
        return Response({
            'ready_publications': serializer.data,
            'count': ready_publications.count()
        })
    
    @action(detail=True, methods=['post'])
    def execute_now(self, request, pk=None):
        """Exécuter publication immédiatement"""
        publication = self.get_object()
        
        if publication.execution_status != 'pending':
            return Response(
                {'error': 'Publication déjà exécutée ou en cours'}, 
                status=400
            )
        
        try:
            publication.execution_status = 'processing'
            publication.save(update_fields=['execution_status'])
            
            # Publier l'article
            status_obj = publication.article.publishing_status
            status_obj.status = 'published'
            status_obj.published_date = timezone.now()
            status_obj.last_published_date = timezone.now()
            status_obj.save(update_fields=['status', 'published_date', 'last_published_date'])
            
            # Synchro Page
            publication.article.page.status = 'published'
            publication.article.page.save(update_fields=['status'])
            
            # Marquer comme terminé
            publication.execution_status = 'completed'
            publication.executed_at = timezone.now()
            publication.save(update_fields=['execution_status', 'executed_at'])
            
            return Response({
                'message': 'Publication exécutée avec succès',
                'executed_at': publication.executed_at
            })
            
        except Exception as e:
            publication.execution_status = 'failed'
            publication.error_message = str(e)
            publication.retry_count += 1
            publication.save(update_fields=['execution_status', 'error_message', 'retry_count'])
            
            return Response(
                {'error': f'Échec publication: {str(e)}'}, 
                status=500
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Annuler publication programmée"""
        publication = self.get_object()
        
        if publication.execution_status != 'pending':
            return Response(
                {'error': 'Publication ne peut pas être annulée'}, 
                status=400
            )
        
        publication.execution_status = 'cancelled'
        publication.save(update_fields=['execution_status'])
        
        return Response({'message': 'Publication annulée'})