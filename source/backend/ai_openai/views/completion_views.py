# backend/ai_openai/views/completion_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from common.views.mixins import BrandScopedViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember
from ..models import OpenAICompletion
from ..serializers import OpenAICompletionSerializer
from ..services import CompletionService

class OpenAICompletionViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """
    API pour gestion des completions OpenAI
    """
    queryset = OpenAICompletion.objects.all()
    serializer_class = OpenAICompletionSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    filter_backends = [DjangoFilterBackend]
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'ai_job', 'ai_job__brand', 'ai_job__created_by'
        )
    
    @action(detail=False, methods=['post'])
    def create_job(self, request):
        """Crée un job de completion"""
        try:
            data = request.data
            
            ai_job = CompletionService.create_completion_job(
                job_type_name=data.get('job_type', 'openai_completion'),
                messages=data['messages'],
                company=request.current_brand.company,
                brand=request.current_brand,
                user=request.user,
                model=data.get('model', 'gpt-4o'),
                description=data.get('description', ''),
                **{k: v for k, v in data.items() if k not in ['messages', 'model', 'description']}
            )
            
            # TODO: Déclencher task_core async ici
            # execute_openai_completion_task.delay(str(ai_job.job_id))
            
            return Response({
                'job_id': str(ai_job.job_id),
                'status': ai_job.status,
                'message': 'Job created and queued for execution'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def job_result(self, request):
        """Récupère le résultat d'un job"""
        job_id = request.query_params.get('job_id')
        if not job_id:
            return Response(
                {'error': 'job_id required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = CompletionService.get_completion_result(job_id)
        if result:
            return Response(result)
        else:
            return Response(
                {'error': 'Job not found or not completed'}, 
                status=status.HTTP_404_NOT_FOUND
            )
