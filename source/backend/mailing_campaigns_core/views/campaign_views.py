# /var/www/megahub/backend/mailing_campaigns_core/views/campaign_views.py

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from common.views.mixins import BrandScopedViewSetMixin, BulkActionViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember, IsBrandAdmin
from ..models import Campaign
from ..serializers.campaign_serializers import (
    CampaignListSerializer,
    CampaignDetailSerializer,
    CampaignWriteSerializer
)

class CampaignViewSet(BrandScopedViewSetMixin, BulkActionViewSetMixin, viewsets.ModelViewSet):
    """
    CRUD complet pour les campagnes email
    
    Endpoints disponibles :
    - GET /mailing/campaigns/ - Liste paginée
    - POST /mailing/campaigns/ - Créer campagne
    - GET /mailing/campaigns/{id}/ - Détail campagne
    - PUT/PATCH /mailing/campaigns/{id}/ - Modifier
    - DELETE /mailing/campaigns/{id}/ - Supprimer
    - POST /mailing/campaigns/{id}/send/ - Envoyer maintenant
    - POST /mailing/campaigns/{id}/schedule/ - Programmer envoi
    - POST /mailing/campaigns/{id}/pause/ - Mettre en pause
    - POST /mailing/campaigns/{id}/duplicate/ - Dupliquer
    """
    queryset = Campaign.objects.select_related('brand', 'created_by', 'template')
    permission_classes = [IsAuthenticated, IsBrandMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['campaign_type', 'status']
    search_fields = ['name', 'subject_line']
    ordering_fields = ['created_at', 'sent_at', 'open_rate', 'click_rate']
    ordering = ['-created_at']
    brand_filter_field = 'brand'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CampaignListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CampaignWriteSerializer
        return CampaignDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(
            brand=self.request.current_brand,
            created_by=self.request.user
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsBrandAdmin])
    def send(self, request, pk=None):
        """
        POST /mailing/campaigns/{id}/send/
        Envoyer la campagne immédiatement
        """
        campaign = self.get_object()
        
        # Vérifications
        if campaign.status != 'draft':
            return Response(
                {'error': 'Seules les campagnes en brouillon peuvent être envoyées'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not campaign.subject_line:
            return Response(
                {'error': 'Sujet requis pour l\'envoi'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Implémenter logique d'envoi réelle
        # - Validation finale
        # - Queue d'envoi
        # - Mise à jour statut
        
        campaign.status = 'sending'
        campaign.sent_at = timezone.now()
        campaign.save(update_fields=['status', 'sent_at'])
        
        return Response({
            'message': 'Campagne mise en queue d\'envoi',
            'campaign_id': campaign.id,
            'status': campaign.status
        })
    
    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """
        POST /mailing/campaigns/{id}/schedule/
        Body: {"send_time": "2024-12-01T10:00:00Z"}
        """
        campaign = self.get_object()
        send_time_str = request.data.get('send_time')
        
        if not send_time_str:
            return Response(
                {'error': 'send_time requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            send_time = timezone.datetime.fromisoformat(send_time_str.replace('Z', '+00:00'))
        except ValueError:
            return Response(
                {'error': 'Format de date invalide'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if send_time <= timezone.now():
            return Response(
                {'error': 'La date doit être dans le futur'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        campaign.scheduled_send_time = send_time
        campaign.status = 'scheduled'
        campaign.save(update_fields=['scheduled_send_time', 'status'])
        
        return Response({
            'message': 'Campagne programmée avec succès',
            'scheduled_for': send_time
        })
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """
        POST /mailing/campaigns/{id}/pause/
        Mettre en pause une campagne en cours
        """
        campaign = self.get_object()
        
        if campaign.status not in ['sending', 'scheduled']:
            return Response(
                {'error': 'Seules les campagnes en cours ou programmées peuvent être mises en pause'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        campaign.status = 'paused'
        campaign.save(update_fields=['status'])
        
        return Response({'message': 'Campagne mise en pause'})
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        POST /mailing/campaigns/{id}/duplicate/
        Body: {"name": "Nouveau nom (optionnel)"}
        """
        campaign = self.get_object()
        new_name = request.data.get('name', f"{campaign.name} (Copie)")
        
        # Vérifier unicité
        if Campaign.objects.filter(name=new_name, brand=request.current_brand).exists():
            return Response(
                {'error': 'Une campagne avec ce nom existe déjà'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Dupliquer
        new_campaign = Campaign.objects.create(
            name=new_name,
            subject_line=campaign.subject_line,
            preview_text=campaign.preview_text,
            campaign_type=campaign.campaign_type,
            brand=request.current_brand,
            created_by=request.user,
            template=campaign.template,
            html_content=campaign.html_content,
            text_content=campaign.text_content,
            from_name=campaign.from_name,
            from_email=campaign.from_email,
            reply_to_email=campaign.reply_to_email,
            ab_test_config=campaign.ab_test_config,
            tags=campaign.tags,
            status='draft'
        )
        
        # Dupliquer associations listes
        for campaign_list in campaign.campaignlist_set.all():
            CampaignList.objects.create(
                campaign=new_campaign,
                mailing_list=campaign_list.mailing_list,
                recipients_count=campaign_list.recipients_count
            )
        
        serializer = CampaignDetailSerializer(new_campaign)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques campagnes"""
        queryset = self.get_queryset()
        
        stats = {
            'total_campaigns': queryset.count(),
            'sent_campaigns': queryset.filter(status='sent').count(),
            'draft_campaigns': queryset.filter(status='draft').count(),
            'avg_open_rate': queryset.filter(status='sent').aggregate(
                avg_open=models.Avg('open_rate')
            )['avg_open'] or 0,
            'total_emails_sent': queryset.aggregate(
                total_sent=models.Sum('emails_sent')
            )['total_sent'] or 0
        }
        
        return Response(stats)
