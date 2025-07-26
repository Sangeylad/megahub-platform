# /var/www/megahub/backend/mailing_lists_core/views/list_views.py

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from common.views.mixins import BrandScopedViewSetMixin, BulkActionViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember, IsBrandAdmin
from ..models import MailingList, ListMembership
from mailing_contacts_core.models import EmailSubscriber
from ..serializers.list_serializers import (
    MailingListListSerializer,
    MailingListDetailSerializer,
    MailingListWriteSerializer,
    ListMembershipSerializer
)

class MailingListViewSet(BrandScopedViewSetMixin, BulkActionViewSetMixin, viewsets.ModelViewSet):
    """
    CRUD complet pour les listes de diffusion
    
    Endpoints disponibles :
    - GET /mailing/lists/ - Liste paginée
    - POST /mailing/lists/ - Créer liste
    - GET /mailing/lists/{id}/ - Détail liste  
    - PUT/PATCH /mailing/lists/{id}/ - Modifier
    - DELETE /mailing/lists/{id}/ - Supprimer
    - GET /mailing/lists/{id}/subscribers/ - Abonnés de la liste
    - POST /mailing/lists/{id}/add-subscribers/ - Ajouter abonnés
    - POST /mailing/lists/{id}/remove-subscribers/ - Retirer abonnés
    """
    queryset = MailingList.objects.select_related('brand', 'created_by')
    permission_classes = [IsAuthenticated, IsBrandMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['list_type', 'is_public']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name', 'subscriber_count']
    ordering = ['-created_at']
    brand_filter_field = 'brand'
    
    def get_serializer_class(self):
        """Serializer selon l'action"""
        if self.action == 'list':
            return MailingListListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return MailingListWriteSerializer
        return MailingListDetailSerializer
    
    def perform_create(self, serializer):
        """Assigner brand et créateur"""
        serializer.save(
            brand=self.request.current_brand,
            created_by=self.request.user
        )
    
    @action(detail=True, methods=['get'])
    def subscribers(self, request, pk=None):
        """
        GET /mailing/lists/{id}/subscribers/
        Liste des abonnés de cette liste
        """
        mailing_list = self.get_object()
        memberships = ListMembership.objects.filter(
            mailing_list=mailing_list,
            is_active=True
        ).select_related('subscriber', 'added_by').order_by('-added_at')
        
        # Pagination manuelle
        page = self.paginate_queryset(memberships)
        if page is not None:
            serializer = ListMembershipSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ListMembershipSerializer(memberships, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsBrandAdmin])
    def add_subscribers(self, request, pk=None):
        """
        POST /mailing/lists/{id}/add-subscribers/
        Body: {"subscriber_ids": [1, 2, 3], "source": "manual"}
        """
        mailing_list = self.get_object()
        subscriber_ids = request.data.get('subscriber_ids', [])
        source = request.data.get('source', 'manual')
        
        if not subscriber_ids:
            return Response(
                {'error': 'subscriber_ids requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que les abonnés existent et appartiennent à la bonne brand
        subscribers = EmailSubscriber.objects.filter(
            id__in=subscriber_ids,
            source_brand=request.current_brand
        )
        
        if len(subscribers) != len(subscriber_ids):
            return Response(
                {'error': 'Certains abonnés sont introuvables ou n\'appartiennent pas à votre marque'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Ajouter en masse (éviter les doublons)
        added_count = 0
        with transaction.atomic():
            for subscriber in subscribers:
                membership, created = ListMembership.objects.get_or_create(
                    mailing_list=mailing_list,
                    subscriber=subscriber,
                    defaults={
                        'subscription_source': source,
                        'added_by': request.user,
                        'is_active': True
                    }
                )
                if created:
                    added_count += 1
                elif not membership.is_active:
                    # Réactiver si existait mais inactif
                    membership.is_active = True
                    membership.save(update_fields=['is_active'])
                    added_count += 1
            
            # Mettre à jour le compteur
            mailing_list.subscriber_count = mailing_list.subscribers.filter(
                listmembership__is_active=True
            ).count()
            mailing_list.save(update_fields=['subscriber_count'])
        
        return Response({
            'message': f'{added_count} abonnés ajoutés avec succès',
            'added_count': added_count,
            'total_subscribers': mailing_list.subscriber_count
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsBrandAdmin])
    def remove_subscribers(self, request, pk=None):
        """
        POST /mailing/lists/{id}/remove-subscribers/
        Body: {"subscriber_ids": [1, 2, 3]}
        """
        mailing_list = self.get_object()
        subscriber_ids = request.data.get('subscriber_ids', [])
        
        if not subscriber_ids:
            return Response(
                {'error': 'subscriber_ids requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Désactiver les memberships
        removed_count = ListMembership.objects.filter(
            mailing_list=mailing_list,
            subscriber_id__in=subscriber_ids,
            is_active=True
        ).update(is_active=False)
        
        # Mettre à jour le compteur
        mailing_list.subscriber_count = mailing_list.subscribers.filter(
            listmembership__is_active=True
        ).count()
        mailing_list.save(update_fields=['subscriber_count'])
        
        return Response({
            'message': f'{removed_count} abonnés retirés avec succès',
            'removed_count': removed_count,
            'total_subscribers': mailing_list.subscriber_count
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        GET /mailing/lists/stats/
        Statistiques globales des listes
        """
        queryset = self.get_queryset()
        
        stats = {
            'total_lists': queryset.count(),
            'public_lists': queryset.filter(is_public=True).count(),
            'total_subscribers': sum(lst.subscriber_count for lst in queryset),
            'by_type': {},
            'largest_list': None
        }
        
        # Stats par type
        for list_type_data in queryset.values('list_type').annotate(count=models.Count('id')):
            stats['by_type'][list_type_data['list_type']] = list_type_data['count']
        
        # Plus grande liste
        largest = queryset.order_by('-subscriber_count').first()
        if largest:
            stats['largest_list'] = {
                'name': largest.name,
                'subscriber_count': largest.subscriber_count
            }
        
        return Response(stats)
