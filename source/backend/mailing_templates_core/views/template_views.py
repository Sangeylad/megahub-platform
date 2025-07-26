# /var/www/megahub/backend/mailing_templates_core/views/template_views.py

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from common.views.mixins import BrandScopedViewSetMixin, BulkActionViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember, IsBrandAdmin
from ..models import EmailTemplate
from ..serializers.template_serializers import (
    EmailTemplateListSerializer,
    EmailTemplateDetailSerializer,
    EmailTemplateWriteSerializer
)

class EmailTemplateViewSet(BrandScopedViewSetMixin, BulkActionViewSetMixin, viewsets.ModelViewSet):
    """
    CRUD complet pour les templates email
    
    Endpoints disponibles :
    - GET /mailing/templates/ - Liste paginée
    - POST /mailing/templates/ - Créer template
    - GET /mailing/templates/{id}/ - Détail template
    - PUT/PATCH /mailing/templates/{id}/ - Modifier
    - DELETE /mailing/templates/{id}/ - Supprimer
    - POST /mailing/templates/{id}/duplicate/ - Dupliquer
    - POST /mailing/templates/{id}/toggle-favorite/ - Favoris
    - GET /mailing/templates/{id}/preview/ - Prévisualisation
    """
    queryset = EmailTemplate.objects.select_related('brand', 'created_by')
    permission_classes = [IsAuthenticated, IsBrandMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'is_favorite']
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['created_at', 'name', 'usage_count', 'last_used_at']
    ordering = ['-created_at']
    brand_filter_field = 'brand'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmailTemplateListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmailTemplateWriteSerializer
        return EmailTemplateDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(
            brand=self.request.current_brand,
            created_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        POST /mailing/templates/{id}/duplicate/
        Body: {"name": "Nouveau nom (optionnel)"}
        """
        template = self.get_object()
        new_name = request.data.get('name', f"{template.name} (Copie)")
        
        # Vérifier unicité du nom
        if EmailTemplate.objects.filter(name=new_name, brand=request.current_brand).exists():
            return Response(
                {'error': 'Un template avec ce nom existe déjà'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Dupliquer
        new_template = EmailTemplate.objects.create(
            name=new_name,
            description=f"Copie de {template.name}",
            category=template.category,
            brand=request.current_brand,
            created_by=request.user,
            html_content=template.html_content,
            text_content=template.text_content,
            design_config=template.design_config,
            variables=template.variables,
            tags=template.tags
        )
        
        serializer = EmailTemplateDetailSerializer(new_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """
        POST /mailing/templates/{id}/toggle-favorite/
        Basculer le statut favori
        """
        template = self.get_object()
        template.is_favorite = not template.is_favorite
        template.save(update_fields=['is_favorite'])
        
        return Response({
            'is_favorite': template.is_favorite,
            'message': 'Ajouté aux favoris' if template.is_favorite else 'Retiré des favoris'
        })
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """
        GET /mailing/templates/{id}/preview/
        Prévisualisation HTML du template
        """
        template = self.get_object()
        
        # TODO: Rendu du template avec variables d'exemple
        preview_data = {
            'html_content': template.html_content,
            'text_content': template.text_content,
            'variables': template.variables,
            'design_config': template.design_config
        }
        
        return Response(preview_data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques templates"""
        queryset = self.get_queryset()
        
        stats = {
            'total_templates': queryset.count(),
            'active_templates': queryset.filter(status='active').count(),
            'favorites': queryset.filter(is_favorite=True).count(),
            'by_category': {},
            'most_used': None
        }
        
        # Stats par catégorie
        for cat_data in queryset.values('category').annotate(count=models.Count('id')):
            stats['by_category'][cat_data['category']] = cat_data['count']
        
        # Template le plus utilisé
        most_used = queryset.order_by('-usage_count').first()
        if most_used:
            stats['most_used'] = {
                'name': most_used.name,
                'usage_count': most_used.usage_count
            }
        
        return Response(stats)
