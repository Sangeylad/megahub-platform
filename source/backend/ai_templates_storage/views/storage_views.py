# backend/ai_templates_storage/views/storage_views.py

from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from common.views.mixins import BrandScopedViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember
from ..models import TemplateVariable, TemplateVersion
from ..serializers import (
    TemplateVariableSerializer,
    TemplateVersionListSerializer, TemplateVersionDetailSerializer, TemplateVersionWriteSerializer
)
from ..filters import TemplateVersionFilter

class TemplateVariableViewSet(ReadOnlyModelViewSet):
    """Variables disponibles - lecture seule"""
    queryset = TemplateVariable.objects.all().order_by('variable_type', 'name')
    serializer_class = TemplateVariableSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Variables groupées par type"""
        variables_by_type = {}
        for variable in self.get_queryset():
            var_type = variable.variable_type
            if var_type not in variables_by_type:
                variables_by_type[var_type] = []
            variables_by_type[var_type].append(TemplateVariableSerializer(variable).data)
        
        return Response(variables_by_type)

class TemplateVersionViewSet(BrandScopedViewSetMixin, ModelViewSet):
    """Gestion versions de templates"""
    queryset = TemplateVersion.objects.select_related('template', 'created_by')
    permission_classes = [IsAuthenticated, IsBrandMember]
    filterset_class = TemplateVersionFilter
    ordering = ['-version_number']
    brand_field = 'template__brand'
    
    def get_serializer_class(self):
        """Serializer par action"""
        if self.action == 'list':
            return TemplateVersionListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TemplateVersionWriteSerializer
        return TemplateVersionDetailSerializer
    
    @action(detail=True, methods=['post'])
    def set_current(self, request, pk=None):
        """Définir comme version courante"""
        version = self.get_object()
        
        # Désactiver autres versions
        TemplateVersion.objects.filter(template=version.template).update(is_current=False)
        
        # Activer cette version
        version.is_current = True
        version.save()
        
        return Response({'status': 'Version définie comme courante'})
