# backend/task_persistence/views/persistent_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from common.views.mixins import BrandScopedViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember
from ..models import PersistentJob, JobCheckpoint
from ..serializers import PersistentJobSerializer, JobCheckpointSerializer
from ..services import RecoveryService, PersistenceService

class PersistentJobViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """CRUD pour jobs persistants avec reprise"""
    ordering = ['-created_at']
    queryset = PersistentJob.objects.all()
    serializer_class = PersistentJobSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    filter_backends = [DjangoFilterBackend]
    ordering = ['-created_at']
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'base_task', 'base_task__brand', 'base_task__created_by', 'job_state'
        ).prefetch_related('checkpoints')
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Reprendre un job interrompu"""
        persistent_job = self.get_object()
        
        result = RecoveryService.resume_job(persistent_job)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def resumable(self, request):
        """Liste des jobs qui peuvent être repris"""
        brand_id = getattr(request, 'current_brand', None)
        brand_id = brand_id.id if brand_id else None
        
        resumable_jobs = RecoveryService.find_resumable_jobs(brand_id)
        serializer = self.get_serializer(resumable_jobs, many=True)
        
        return Response({
            'count': len(resumable_jobs),
            'jobs': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def checkpoints(self, request, pk=None):
        """Historique des checkpoints d'un job"""
        persistent_job = self.get_object()
        checkpoints = persistent_job.checkpoints.all()
        
        serializer = JobCheckpointSerializer(checkpoints, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='cleanup-old')
    def cleanup_old(self, request):
        """Nettoie les anciens checkpoints"""
        days_old = request.data.get('days_old', 30)
        
        result = RecoveryService.cleanup_old_checkpoints(days_old)
        return Response(result)

class JobCheckpointViewSet(viewsets.ReadOnlyModelViewSet):
    """Lecture seule des checkpoints"""
    
    queryset = JobCheckpoint.objects.all()
    serializer_class = JobCheckpointSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['-created_at']
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'persistent_job__base_task'
        )
