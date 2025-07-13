# backend/seo_keywords_base/models/keyword_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class Keyword(TimestampedMixin):
    """Modèle central des mots-clés - données de base uniquement"""
    
    keyword = models.CharField(max_length=1000, unique=True)
    volume = models.IntegerField(null=True, blank=True)
    search_intent = models.CharField(
        max_length=10,
        choices=[
            ('TOFU', 'Top of Funnel'),
            ('MOFU', 'Middle of Funnel'),
            ('BOFU', 'Bottom of Funnel')
        ],
        null=True, blank=True
    )
    cpc = models.CharField(max_length=50, null=True, blank=True)
    youtube_videos = models.CharField(max_length=500, null=True, blank=True)
    local_pack = models.BooleanField(default=False)
    search_results = models.JSONField(default=dict, blank=True)
    
    # Legacy field (sera progressivement remplacé par ContentType)
    content_types = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.keyword
    
    class Meta:
        db_table = 'seo_keywords_base_keyword'
        ordering = ['-volume', 'keyword']
        indexes = [
            models.Index(fields=['keyword']),
            models.Index(fields=['volume']),
            models.Index(fields=['search_intent']),
        ]