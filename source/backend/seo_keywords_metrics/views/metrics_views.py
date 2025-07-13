# backend/seo_keywords_metrics/views/metrics_views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

# Local imports
from ..models import KeywordMetrics
from ..serializers.metrics_serializers import KeywordMetricsSerializer


class KeywordMetricsViewSet(viewsets.ModelViewSet):
    """
    GESTION DES MÉTRIQUES MOTS-CLÉS - CRUD UNIQUEMENT
    
    Endpoints RESTful :
    - GET /seo/keywords-metrics/metrics/        # Liste
    - POST /seo/keywords-metrics/metrics/       # Création  
    - GET /seo/keywords-metrics/metrics/{id}/   # Détail
    - PUT /seo/keywords-metrics/metrics/{id}/   # Update
    - DELETE /seo/keywords-metrics/metrics/{id}/# Delete
    """
    
    queryset = KeywordMetrics.objects.all()
    serializer_class = KeywordMetricsSerializer
    permission_classes = [IsAuthenticated]
    # filter_backends = [DjangoFilterBackend]  # ✅ Commenté temporairement
    # filterset_class = MetricsFilter          # ✅ Commenté temporairement
    ordering = ['keyword__keyword']
    
    def get_queryset(self):
        """Optimisation requêtes avec select_related obligatoire"""
        return super().get_queryset().select_related('keyword')