# backend/task_core/views/task_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from common.views.mixins import BrandScopedViewSetMixin, AnalyticsViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember
from ..models import BaseTask
from ..serializers import BaseTaskSerializer, BaseTaskListSerializer
from ..filters import BaseTaskFilter
from ..services import QueueManager

class BaseTaskViewSet(BrandScopedViewSetMixin, AnalyticsViewSetMixin, viewsets.ModelViewSet):
    """CRUD tasks avec analytics intégrés"""
    
    queryset = BaseTask.objects.all()
    permission_classes = [IsAuthenticated, IsBrandMember]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BaseTaskFilter
    ordering = ['-created_at']
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'created_by', 'brand'
        )
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BaseTaskListSerializer
        return BaseTaskSerializer
    
    def perform_create(self, serializer):
        """Auto-assigner brand et user depuis middleware"""
        serializer.save(
            brand=self.request.current_brand,
            created_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Relancer une tâche échouée"""
        task = self.get_object()
        
        if task.status != 'failed':
            return Response(
                {'error': 'Seules les tâches échouées peuvent être relancées'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = 'pending'
        task.save(update_fields=['status'])
        
        return Response({'status': 'Task queued for retry'})
    
    @action(detail=False, methods=['get'])
    def queue_stats(self, request):
        """Statistiques des queues"""
        stats = QueueManager.get_queue_stats()
        return Response(stats)