# /var/www/megahub/backend/mailing_contacts_core/views/contact_views.py

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from common.views.mixins import BrandScopedViewSetMixin, BulkActionViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember, IsBrandAdmin
from ..models import EmailSubscriber
from ..serializers.contact_serializers import (
    EmailSubscriberListSerializer,
    EmailSubscriberDetailSerializer, 
    EmailSubscriberWriteSerializer
)

class EmailSubscriberViewSet(BrandScopedViewSetMixin, BulkActionViewSetMixin, viewsets.ModelViewSet):
    """
    CRUD complet pour les abonnés email
    
    Endpoints disponibles :
    - GET /mailing/contacts/ - Liste paginée
    - POST /mailing/contacts/ - Créer abonné  
    - GET /mailing/contacts/{id}/ - Détail abonné
    - PUT/PATCH /mailing/contacts/{id}/ - Modifier
    - DELETE /mailing/contacts/{id}/ - Supprimer
    - GET /mailing/contacts/stats/ - Statistiques globales
    - POST /mailing/contacts/bulk-import/ - Import en masse
    """
    queryset = EmailSubscriber.objects.select_related(
        'source_brand', 'crm_contact'
    ).prefetch_related(
        'subscriberpreferences', 'subscribertracking'
    )
    permission_classes = [IsAuthenticated, IsBrandMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'source', 'language']
    search_fields = ['email', 'first_name', 'last_name', 'company']
    ordering_fields = ['created_at', 'email', 'last_name']
    ordering = ['-created_at']
    brand_filter_field = 'source_brand'  # Pour BrandScopedViewSetMixin
    
    def get_serializer_class(self):
        """Serializer selon l'action"""
        if self.action == 'list':
            return EmailSubscriberListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmailSubscriberWriteSerializer
        return EmailSubscriberDetailSerializer
    
    def perform_create(self, serializer):
        """Assigner la brand automatiquement"""
        serializer.save(source_brand=self.request.current_brand)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        GET /mailing/contacts/stats/
        Statistiques globales des abonnés
        """
        queryset = self.get_queryset()
        
        stats = {
            'total_subscribers': queryset.count(),
            'active_subscribers': queryset.filter(status='active').count(),
            'unsubscribed': queryset.filter(status='unsubscribed').count(),
            'bounced': queryset.filter(status='bounced').count(),
            'by_source': {},
            'recent_signups': queryset.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count()
        }
        
        # Stats par source
        for source_data in queryset.values('source').annotate(count=models.Count('id')):
            stats['by_source'][source_data['source']] = source_data['count']
        
        return Response(stats)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsBrandAdmin])
    def bulk_import(self, request):
        """
        POST /mailing/contacts/bulk-import/
        Import en masse d'abonnés depuis CSV/Excel
        """
        # TODO: Implémenter logique d'import
        # Utiliser les services d'import de mailing_lists_imports
        return Response({
            'message': 'Import en masse - À implémenter',
            'feature': 'bulk_import'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        """
        POST /mailing/contacts/{id}/subscribe/
        Réabonner un contact désabonné
        """
        subscriber = self.get_object()
        if subscriber.status == 'unsubscribed':
            subscriber.status = 'active'
            subscriber.save(update_fields=['status', 'updated_at'])
            return Response({'message': 'Abonné réactivé avec succès'})
        return Response(
            {'error': 'L\'abonné n\'est pas désabonné'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def unsubscribe(self, request, pk=None):
        """
        POST /mailing/contacts/{id}/unsubscribe/
        Désabonner un contact
        """
        subscriber = self.get_object()
        reason = request.data.get('reason', 'manual')
        
        subscriber.status = 'unsubscribed'
        subscriber.save(update_fields=['status', 'updated_at'])
        
        # Créer/MAJ les préférences avec la raison
        if hasattr(subscriber, 'subscriberpreferences'):
            subscriber.subscriberpreferences.unsubscribe_reason = reason
            subscriber.subscriberpreferences.save(update_fields=['unsubscribe_reason'])
        
        return Response({'message': 'Abonné désabonné avec succès'})
