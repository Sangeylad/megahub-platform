# backend/ai_openai/urls.py

from rest_framework import routers
from django.urls import path, include
from .views import OpenAIJobViewSet, ChatCompletionViewSet

router = routers.DefaultRouter()
router.register(r'jobs', OpenAIJobViewSet, basename='openai-jobs')

urlpatterns = [
    # 🎯 Endpoints chat avec chemins spécifiques
    path('chat/models/', ChatCompletionViewSet.as_view({'get': 'models'}), name='openai-chat-models'),
    path('chat/create_job/', ChatCompletionViewSet.as_view({'post': 'create_job'}), name='openai-chat-create'),
    
    # 🎯 Endpoint completion pour récupérer résultats
    path('completion/job_result/', ChatCompletionViewSet.as_view({'get': 'job_result'}), name='openai-completion-result'),
    
    # Router principal
    path('', include(router.urls)),
]