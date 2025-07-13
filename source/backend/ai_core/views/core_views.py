# backend/ai_core/views/core_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from common.views.mixins import BrandScopedViewSetMixin, AnalyticsViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember

from ..models import AIJob, AIJobType
from ..serializers import AIJobSerializer, AIJobTypeSerializer
from ..services import JobService, StatusService

class AIJobTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """Types de jobs IA disponibles"""
    queryset = AIJobType.objects.all()  # ✅ FIX 1: Enlever is_active=True
    serializer_class = AIJobTypeSerializer
    permission_classes = [IsAuthenticated]

class AIJobViewSet(BrandScopedViewSetMixin, AnalyticsViewSetMixin, viewsets.ModelViewSet):
    """CRUD jobs IA avec monitoring"""
    queryset = AIJob.objects.all()
    serializer_class = AIJobSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['-created_at']
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'job_type', 'brand', 'created_by'
        )
    
    def perform_create(self, serializer):
        """✅ FIX: Auto-assign brand, user et job_type"""
        # Récupère le job_type par nom depuis request.data
        job_type_name = self.request.data.get('job_type')
        
        if isinstance(job_type_name, str):
            # Si c'est un string, chercher le job_type
            try:
                job_type = AIJobType.objects.get(name=job_type_name)  # ✅ FIX 2: Enlever is_active=True
            except AIJobType.DoesNotExist:
                raise ValidationError(f"Job type '{job_type_name}' non trouvé")
        elif isinstance(job_type_name, int):
            # Si c'est un ID
            try:
                job_type = AIJobType.objects.get(id=job_type_name)  # ✅ FIX 3: Enlever is_active=True
            except AIJobType.DoesNotExist:
                raise ValidationError(f"Job type ID '{job_type_name}' non trouvé")
        else:
            # Pas de job_type fourni
            raise ValidationError("job_type est requis")
        
        # Auto-assign depuis le middleware/context
        serializer.save(
            brand=self.request.current_brand,
            created_by=self.request.user,
            job_type=job_type
        )
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """GET /ai/jobs/dashboard/ - Stats dashboard"""
        stats = StatusService.get_dashboard_stats(
            brand=getattr(request, 'current_brand', None)
        )
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """GET /ai/jobs/by_status/?status=pending"""
        status_filter = request.query_params.get('status')
        if not status_filter:
            return Response(
                {'error': 'Parameter status required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        jobs = StatusService.get_jobs_by_status(
            status_filter,
            brand=getattr(request, 'current_brand', None)
        )
        return Response({'jobs': jobs})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """POST /ai/jobs/{id}/cancel/"""
        ai_job = self.get_object()
        
        if ai_job.status not in ['pending', 'running']:
            return Response(
                {'error': 'Job cannot be cancelled'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ai_job.status = 'cancelled'
        ai_job.save(update_fields=['status'])
        
        return Response({'message': 'Job cancelled successfully'})