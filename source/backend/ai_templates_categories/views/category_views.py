# backend/ai_templates_categories/views/category_views.py

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember
from ..models import TemplateCategory, TemplateTag, CategoryPermission
from ..serializers import TemplateCategorySerializer, TemplateTagSerializer, CategoryPermissionSerializer
from ..filters import TemplateCategoryFilter, TemplateTagFilter

class TemplateCategoryViewSet(ModelViewSet):
    """Gestion catégories de templates"""
    queryset = TemplateCategory.objects.select_related('parent').prefetch_related('children')
    serializer_class = TemplateCategorySerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TemplateCategoryFilter
    ordering = ['level', 'sort_order', 'name']
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Arbre hiérarchique complet"""
        root_categories = self.get_queryset().filter(parent=None, is_active=True)
        
        def build_tree(category):
            serialized = TemplateCategorySerializer(category).data
            children = category.children.filter(is_active=True)
            if children.exists():
                serialized['children'] = [build_tree(child) for child in children]
            return serialized
        
        tree_data = [build_tree(cat) for cat in root_categories]
        return Response(tree_data)
    
    @action(detail=True, methods=['get'])
    def breadcrumb(self, request, pk=None):
        """Fil d'Ariane pour une catégorie"""
        category = self.get_object()
        breadcrumb = []
        current = category
        while current:
            breadcrumb.insert(0, {
                'id': current.id,
                'name': current.display_name,
                'level': current.level
            })
            current = current.parent
        return Response(breadcrumb)

class TemplateTagViewSet(ModelViewSet):
    """Gestion tags de templates"""
    queryset = TemplateTag.objects.filter(is_active=True)
    serializer_class = TemplateTagSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TemplateTagFilter
    ordering = ['-usage_count', 'name']
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Tags les plus utilisés"""
        popular_tags = self.get_queryset().filter(usage_count__gt=0)[:20]
        serializer = TemplateTagSerializer(popular_tags, many=True)
        return Response(serializer.data)

class CategoryPermissionViewSet(ReadOnlyModelViewSet):
    """Permissions de catégories - lecture seule"""
    queryset = CategoryPermission.objects.select_related('category').filter(is_active=True)
    serializer_class = CategoryPermissionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
