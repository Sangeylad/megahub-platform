# backend/seo_keywords_metrics/models/metrics_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class KeywordMetrics(TimestampedMixin):
    """Métriques SEO des mots-clés"""
    
    keyword = models.OneToOneField(
        'seo_keywords_base.Keyword',
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    
    # Domain Authority métriques
    da_min = models.IntegerField(null=True, blank=True)
    da_max = models.IntegerField(null=True, blank=True)
    da_median = models.IntegerField(null=True, blank=True)
    da_q1 = models.IntegerField(null=True, blank=True)
    da_q3 = models.IntegerField(null=True, blank=True)
    
    # Backlinks métriques
    bl_min = models.IntegerField(null=True, blank=True)
    bl_max = models.IntegerField(null=True, blank=True)
    bl_median = models.IntegerField(null=True, blank=True)
    bl_q1 = models.IntegerField(null=True, blank=True)
    bl_q3 = models.IntegerField(null=True, blank=True)
    
    # Difficulté
    kdifficulty = models.CharField(max_length=200, null=True, blank=True)
    
    def get_normalized_difficulty(self):
        """Normalise la difficulté en float 0-1"""
        if not self.kdifficulty:
            return None
        try:
            kd_str = str(self.kdifficulty).strip().replace('%', '').replace(',', '.')
            kd_value = float(kd_str)
            return kd_value / 100 if kd_value > 1 else kd_value
        except (ValueError, TypeError):
            return None
    
    def __str__(self):
        return f"Metrics for {self.keyword.keyword}"
    
    class Meta:
        db_table = 'seo_keywords_metrics_keywordmetrics'
        ordering = ['keyword__keyword']