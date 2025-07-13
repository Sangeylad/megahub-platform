# backend/ai_templates_core/views/template_views.py
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import timedelta

from common.views.mixins import (
    BrandScopedViewSetMixin, BulkActionViewSetMixin, AnalyticsViewSetMixin
)
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember

from ..models import TemplateType, BrandTemplateConfig, BaseTemplate
from ..serializers import (
    TemplateTypeSerializer, BrandTemplateConfigSerializer,
    BaseTemplateListSerializer, BaseTemplateDetailSerializer, 
    BaseTemplateWriteSerializer
)
from ..filters import BaseTemplateFilter

class TemplateTypeViewSet(ReadOnlyModelViewSet):
    """Types de templates - lecture seule"""
    queryset = TemplateType.objects.filter(is_active=True)
    serializer_class = TemplateTypeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

class BrandTemplateConfigViewSet(BrandScopedViewSetMixin, ModelViewSet):
    """Configuration templates par brand"""
    queryset = BrandTemplateConfig.objects.all()
    serializer_class = BrandTemplateConfigSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    brand_field = 'brand'

class BaseTemplateViewSet(
    BrandScopedViewSetMixin,
    BulkActionViewSetMixin,
    AnalyticsViewSetMixin,
    ModelViewSet
):
    """
    🔥 CRUD TEMPLATES + ACTIONS INTELLIGENTES
    
    CRUD Standard :
    - GET /templates/                     # Liste avec filtres
    - POST /templates/                    # Création
    - GET /templates/{id}/                # Détail
    - PUT /templates/{id}/                # Update
    - PATCH /templates/{id}/              # Update partiel
    - DELETE /templates/{id}/             # Suppression
    
    Actions Intelligentes :
    - POST /templates/{id}/duplicate/     # Duplication
    - GET /templates/by-type/             # Groupés par type
    - GET /templates/analytics/           # Métriques
    - GET /templates/my-templates/        # Mes templates
    - GET /templates/trending/            # Tendances
    - POST /templates/bulk-update/        # Actions en masse
    """
    
    queryset = BaseTemplate.objects.select_related(
        'template_type', 'brand', 'created_by'
    )
    
    permission_classes = [IsAuthenticated, IsBrandMember]
    filterset_class = BaseTemplateFilter
    ordering = ['-created_at']
    brand_field = 'brand'
    
    search_fields = ['name', 'description', 'prompt_content']
    ordering_fields = ['name', 'created_at', 'updated_at']

    def get_queryset(self):
        """Queryset avec annotations pour performance"""
        queryset = super().get_queryset()
        
        # Annotations conditionnelles selon apps disponibles
        annotations = {}
        
        # Storage - versions
        try:
            from ai_templates_storage.models import TemplateVersion
            annotations['versions_count'] = Count('versions', distinct=True)
        except ImportError:
            pass
        
        # Insights - recommandations
        try:
            from ai_templates_insights.models import TemplateRecommendation
            annotations['recommendations_count'] = Count('template_recommendations', distinct=True)
        except ImportError:
            pass
        
        if annotations:
            queryset = queryset.annotate(**annotations)
        
        return queryset

    def get_serializer_class(self):
        """Serializer adapté par action"""
        if self.action == 'list':
            return BaseTemplateListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return BaseTemplateWriteSerializer
        return BaseTemplateDetailSerializer

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        Duplication template
        
        Body: {"name": "Nouveau nom (optionnel)"}
        """
        template = self.get_object()
        new_name = request.data.get('name', f"{template.name} (Copie)")
        
        new_template = BaseTemplate.objects.create(
            name=new_name,
            description=template.description,
            template_type=template.template_type,
            brand=request.current_brand,
            prompt_content=template.prompt_content,
            created_by=request.user,
            is_active=False,  # Désactivé par défaut
            is_public=False   # Privé par défaut
        )
        
        serializer = BaseTemplateDetailSerializer(new_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Templates groupés par type avec stats"""
        queryset = self.filter_queryset(self.get_queryset())
        
        templates_by_type = {}
        
        for template in queryset:
            type_name = template.template_type.display_name
            
            if type_name not in templates_by_type:
                templates_by_type[type_name] = {
                    'type_id': template.template_type.id,
                    'total_count': 0,
                    'active_count': 0,
                    'public_count': 0,
                    'templates': []
                }
            
            templates_by_type[type_name]['total_count'] += 1
            if template.is_active:
                templates_by_type[type_name]['active_count'] += 1
            if template.is_public:
                templates_by_type[type_name]['public_count'] += 1
            
            templates_by_type[type_name]['templates'].append(
                BaseTemplateListSerializer(template).data
            )
        
        return Response({
            'total_types': len(templates_by_type),
            'templates_by_type': templates_by_type
        })

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """
        Analytics intelligentes
        
        Query params:
        - period: 7d, 30d, 90d
        - breakdown: type, status, brand
        """
        queryset = self.filter_queryset(self.get_queryset())
        period = request.query_params.get('period', '30d')
        breakdown = request.query_params.get('breakdown', 'type')
        
        # Calcul période
        if period == '7d':
            date_threshold = timezone.now() - timedelta(days=7)
        elif period == '90d':
            date_threshold = timezone.now() - timedelta(days=90)
        else:  # 30d par défaut
            date_threshold = timezone.now() - timedelta(days=30)
        
        # Stats globales
        total = queryset.count()
        active = queryset.filter(is_active=True).count()
        public = queryset.filter(is_public=True).count()
        recent = queryset.filter(created_at__gte=date_threshold).count()
        
        # Breakdown selon paramètre
        breakdown_data = {}
        if breakdown == 'type':
            breakdown_data = self._get_breakdown_by_type(queryset)
        elif breakdown == 'status':
            breakdown_data = {
                'active': active,
                'inactive': total - active,
                'public': public,
                'private': total - public
            }
        elif breakdown == 'brand':
            breakdown_data = self._get_breakdown_by_brand(queryset)
        
        return Response({
            'period': period,
            'summary': {
                'total_templates': total,
                'active_templates': active,
                'public_templates': public,
                'recent_templates': recent,
                'activity_rate': round((recent / total * 100), 2) if total > 0 else 0
            },
            'breakdown': breakdown_data
        })

    @action(detail=False, methods=['get'])
    def my_templates(self, request):
        """Templates de l'utilisateur courant"""
        my_templates = self.get_queryset().filter(created_by=request.user)
        
        # Stats rapides
        total = my_templates.count()
        active = my_templates.filter(is_active=True).count()
        public = my_templates.filter(is_public=True).count()
        
        # Templates récents (7 jours)
        recent_date = timezone.now() - timedelta(days=7)
        recent_templates = my_templates.filter(created_at__gte=recent_date)
        
        return Response({
            'summary': {
                'total': total,
                'active': active,
                'public': public,
                'recent_count': recent_templates.count()
            },
            'recent_templates': BaseTemplateListSerializer(recent_templates, many=True).data,
            'all_templates': BaseTemplateListSerializer(my_templates, many=True).data
        })

    @action(detail=False, methods=['get'])
    def trending(self, request):
        """
        Templates tendance intelligents
        
        Query params:
        - limit: nombre de résultats (défaut: 10)
        """
        limit = int(request.query_params.get('limit', 10))
        
        # Stratégie fallback intelligente
        trending_queryset = self.get_queryset()
        
        # 1. Essayer avec insights si disponible
        try:
            from ai_templates_insights.models import TemplateInsight
            trending_queryset = trending_queryset.filter(
                insights__insight_type='trending_up',
                insights__is_resolved=False
            ).distinct()
        except ImportError:
            # 2. Fallback : activité récente + popularité
            recent_date = timezone.now() - timedelta(days=7)
            trending_queryset = trending_queryset.filter(
                Q(updated_at__gte=recent_date) | Q(is_public=True)
            ).order_by('-updated_at', '-created_at')
        
        trending_templates = trending_queryset[:limit]
        
        return Response({
            'count': len(trending_templates),
            'templates': BaseTemplateListSerializer(trending_templates, many=True).data,
            'note': 'Basé sur activité récente et popularité'
        })

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Actions en masse
        
        Body: {
            "template_ids": [1, 2, 3],
            "action": "activate" | "deactivate" | "make_public" | "make_private"
        }
        """
        template_ids = request.data.get('template_ids', [])
        action = request.data.get('action')
        
        if not template_ids or not action:
            return Response({
                'error': 'template_ids et action requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Sécurité : filtrer par brand
        templates = self.get_queryset().filter(id__in=template_ids)
        
        updated_count = 0
        errors = []
        
        for template in templates:
            try:
                if action == 'activate':
                    template.is_active = True
                elif action == 'deactivate':
                    template.is_active = False
                elif action == 'make_public':
                    template.is_public = True
                elif action == 'make_private':
                    template.is_public = False
                else:
                    errors.append(f"Action '{action}' non supportée")
                    continue
                
                template.save()
                updated_count += 1
                
            except Exception as e:
                errors.append(f"Template {template.id}: {str(e)}")
        
        return Response({
            'updated_count': updated_count,
            'total_requested': len(template_ids),
            'errors': errors
        })

    # ===== MÉTHODES PRIVÉES =====
    
    def _get_breakdown_by_type(self, queryset):
        """Breakdown par type de template"""
        breakdown = {}
        for template in queryset:
            type_name = template.template_type.display_name
            if type_name not in breakdown:
                breakdown[type_name] = {'count': 0, 'active': 0}
            breakdown[type_name]['count'] += 1
            if template.is_active:
                breakdown[type_name]['active'] += 1
        return breakdown
    
    def _get_breakdown_by_brand(self, queryset):
        """Breakdown par brand"""
        breakdown = {}
        for template in queryset:
            brand_name = template.brand.name
            if brand_name not in breakdown:
                breakdown[brand_name] = {'count': 0, 'active': 0}
            breakdown[brand_name]['count'] += 1
            if template.is_active:
                breakdown[brand_name]['active'] += 1
        return breakdown