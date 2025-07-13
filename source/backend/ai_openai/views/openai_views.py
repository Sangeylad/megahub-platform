# backend/ai_openai/views/openai_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views.mixins import BrandScopedViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember

from ..models import OpenAIJob
from ..serializers import OpenAIJobSerializer, ChatCompletionSerializer
from ..services import ChatService
from ai_core.models import AIJob  # 🆕 Import pour job_result

class OpenAIJobViewSet(BrandScopedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """Jobs OpenAI avec filtrage brand"""
    queryset = OpenAIJob.objects.all()
    serializer_class = OpenAIJobSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    
    def get_queryset(self):
        return super().get_queryset().select_related('ai_job').order_by('-created_at')

class ChatCompletionViewSet(viewsets.ViewSet):
    """Endpoints chat completions"""
    permission_classes = [IsAuthenticated, IsBrandMember]
    
    @action(detail=False, methods=['post'])
    def create_job(self, request):
        """POST /openai/chat/create_job/ - Créer job chat"""
        serializer = ChatCompletionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = ChatService.create_chat_job(
                messages=serializer.validated_data['messages'],
                brand=getattr(request, 'current_brand'),
                created_by=request.user,
                model=serializer.validated_data.get('model', 'gpt-4o'),
                temperature=serializer.validated_data.get('temperature', 0.7),
                max_tokens=serializer.validated_data.get('max_tokens'),
                description=serializer.validated_data.get('description', ''),
                tools=serializer.validated_data.get('tools'),
                tool_resources=serializer.validated_data.get('tool_resources'),
                reasoning_effort=serializer.validated_data.get('reasoning_effort'),  # 🆕 O3
                response_format=serializer.validated_data.get('response_format')
            )
            
            return Response(result, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def models(self, request):
        """GET /openai/chat/models/ - Modèles disponibles"""
        return Response({
            'models': [
                {'id': 'gpt-4o', 'name': 'GPT-4 Omni'},
                {'id': 'gpt-4-turbo', 'name': 'GPT-4 Turbo'},
                {'id': 'o3-mini', 'name': 'O3 Mini'},
                {'id': 'o3', 'name': 'O3'}
            ]
        })
    
    @action(detail=False, methods=['get'])
    def job_result(self, request):
        """GET /openai/completion/job_result/ - Récupérer résultat job"""
        job_id = request.query_params.get('job_id')
        if not job_id:
            return Response(
                {'error': 'job_id parameter required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Récupérer le job via ai_core
            ai_job = AIJob.objects.select_related('openai_job').filter(
                job_id=job_id,
                brand=getattr(request, 'current_brand')  # Sécurité brand
            ).first()
            
            if not ai_job:
                return Response(
                    {'error': 'Job not found or access denied'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Construire la réponse
            result = {
                'job_id': job_id,
                'status': ai_job.status,
                'created_at': ai_job.created_at,
                'completed_at': ai_job.completed_at,
                'result_data': ai_job.result_data,
                'error_message': ai_job.error_message
            }
            
            # Ajouter infos OpenAI si disponibles
            if hasattr(ai_job, 'openai_job'):
                openai_job = ai_job.openai_job
                result.update({
                    'model': openai_job.model,
                    'tokens_used': openai_job.total_tokens,
                    'reasoning_effort': openai_job.reasoning_effort,
                    'messages_format': openai_job.messages_format
                })
            
            return Response(result)
                
        except Exception as e:
            return Response(
                {'error': f'Internal error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )