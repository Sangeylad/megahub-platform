# /var/www/megahub/backend/mailing_analytics_core/views/analytics_views.py

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from common.views.mixins import BrandScopedViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember
from ..models import EmailEvent
from ..serializers.analytics_serializers import (
    EmailEventListSerializer,
    EmailEventDetailSerializer,
    EmailEventCreateSerializer
)

class EmailEventViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """
    CRUD pour les événements email + analytics
    
    Endpoints disponibles :
    - GET /mailing/analytics/events/ - Liste événements
    - POST /mailing/analytics/events/ - Créer événement (webhook)
    - GET /mailing/analytics/events/{id}/ - Détail événement
    - GET /mailing/analytics/events/dashboard/ - Dashboard analytics
    - GET /mailing/analytics/events/trends/ - Tendances temporelles
    """
    queryset = EmailEvent.objects.select_related(
        'subscriber', 'campaign', 'automation'
    )
    permission_classes = [IsAuthenticated, IsBrandMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event_type', 'processed']
    search_fields = ['email_address', 'subscriber__email']
    ordering_fields = ['timestamp', 'created_at']
    ordering = ['-timestamp']
    brand_filter_field = 'subscriber__source_brand'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EmailEventCreateSerializer
        elif self.action == 'list':
            return EmailEventListSerializer
        return EmailEventDetailSerializer
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        GET /mailing/analytics/events/dashboard/
        Dashboard analytics complet
        """
        queryset = self.get_queryset()
        
        # Période (30 derniers jours par défaut)
        days = int(request.query_params.get('days', 30))
        since = timezone.now() - timedelta(days=days)
        recent_events = queryset.filter(timestamp__gte=since)
        
        # Métriques globales
        dashboard_data = {
            'period_days': days,
            'total_events': recent_events.count(),
            'events_by_type': {},
            'daily_trends': {},
            'top_campaigns': [],
            'engagement_metrics': {}
        }
        
        # Événements par type
        events_by_type = recent_events.values('event_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        for event_data in events_by_type:
            dashboard_data['events_by_type'][event_data['event_type']] = event_data['count']
        
        # Métriques d'engagement
        total_sent = dashboard_data['events_by_type'].get('sent', 0)
        total_delivered = dashboard_data['events_by_type'].get('delivered', 0)
        total_opened = dashboard_data['events_by_type'].get('opened', 0)
        total_clicked = dashboard_data['events_by_type'].get('clicked', 0)
        
        if total_sent > 0:
            dashboard_data['engagement_metrics'] = {
                'delivery_rate': round((total_delivered / total_sent) * 100, 2) if total_sent > 0 else 0,
                'open_rate': round((total_opened / total_delivered) * 100, 2) if total_delivered > 0 else 0,
                'click_rate': round((total_clicked / total_delivered) * 100, 2) if total_delivered > 0 else 0,
                'click_to_open_rate': round((total_clicked / total_opened) * 100, 2) if total_opened > 0 else 0
            }
        
        # Top campagnes (par nombre d'événements)
        top_campaigns = recent_events.filter(
            campaign__isnull=False
        ).values(
            'campaign__name', 'campaign__id'
        ).annotate(
            events_count=Count('id')
        ).order_by('-events_count')[:5]
        
        dashboard_data['top_campaigns'] = list(top_campaigns)
        
        return Response(dashboard_data)
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """
        GET /mailing/analytics/events/trends/
        Tendances temporelles des événements
        """
        queryset = self.get_queryset()
        
        # Période
        days = int(request.query_params.get('days', 7))
        since = timezone.now() - timedelta(days=days)
        
        # Événements par jour et par type
        trends_data = {}
        
        for i in range(days):
            date = (timezone.now() - timedelta(days=i)).date()
            day_events = queryset.filter(timestamp__date=date)
            
            trends_data[str(date)] = {
                'sent': day_events.filter(event_type='sent').count(),
                'delivered': day_events.filter(event_type='delivered').count(),
                'opened': day_events.filter(event_type='opened').count(),
                'clicked': day_events.filter(event_type='clicked').count(),
                'bounced': day_events.filter(event_type='bounced').count(),
                'unsubscribed': day_events.filter(event_type='unsubscribed').count()
            }
        
        return Response({
            'period_days': days,
            'trends': trends_data
        })
    
    @action(detail=False, methods=['get'])
    def performance_by_campaign(self, request):
        """
        GET /mailing/analytics/events/performance-by-campaign/
        Performance détaillée par campagne
        """
        queryset = self.get_queryset()
        
        # Grouper par campagne
        campaigns_data = []
        
        campaigns = queryset.filter(
            campaign__isnull=False
        ).values('campaign__id', 'campaign__name').distinct()
        
        for campaign in campaigns:
            campaign_events = queryset.filter(campaign__id=campaign['campaign__id'])
            
            sent = campaign_events.filter(event_type='sent').count()
            delivered = campaign_events.filter(event_type='delivered').count()
            opened = campaign_events.filter(event_type='opened').count()
            clicked = campaign_events.filter(event_type='clicked').count()
            unsubscribed = campaign_events.filter(event_type='unsubscribed').count()
            
            campaigns_data.append({
                'campaign_id': campaign['campaign__id'],
                'campaign_name': campaign['campaign__name'],
                'metrics': {
                    'sent': sent,
                    'delivered': delivered,
                    'opened': opened,
                    'clicked': clicked,
                    'unsubscribed': unsubscribed,
                    'delivery_rate': round((delivered / sent) * 100, 2) if sent > 0 else 0,
                    'open_rate': round((opened / delivered) * 100, 2) if delivered > 0 else 0,
                    'click_rate': round((clicked / delivered) * 100, 2) if delivered > 0 else 0
                }
            })
        
        # Trier par taux d'ouverture
        campaigns_data.sort(key=lambda x: x['metrics']['open_rate'], reverse=True)
        
        return Response({'campaigns': campaigns_data})
