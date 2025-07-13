# backend/seo_keywords_metrics/serializers/metrics_serializers.py

from rest_framework import serializers
from common.serializers.mixins import TimestampedSerializer
from ..models import KeywordMetrics

class KeywordMetricsSerializer(TimestampedSerializer):
    """Serializer pour métriques des mots-clés"""
    
    keyword_text = serializers.CharField(source='keyword.keyword', read_only=True)
    kdifficulty_normalized = serializers.SerializerMethodField()
    
    class Meta:
        model = KeywordMetrics
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_kdifficulty_normalized(self, obj):
        return obj.get_normalized_difficulty()