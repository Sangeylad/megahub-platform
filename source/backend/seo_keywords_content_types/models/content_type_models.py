# backend/seo_keywords_content_types/models/content_type_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class ContentType(TimestampedMixin):
    """Types de contenu pour mots-clés"""
    
    name = models.CharField(max_length=500, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'seo_keywords_content_types_contenttype'
        ordering = ['name']

class KeywordContentType(TimestampedMixin):
    """Association Keyword ↔ ContentType avec priorité"""
    
    keyword = models.ForeignKey(
        'seo_keywords_base.Keyword', 
        on_delete=models.CASCADE, 
        related_name='content_type_associations'
    )
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        related_name='keyword_associations'
    )
    priority = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'seo_keywords_content_types_keywordcontenttype'
        unique_together = ('keyword', 'content_type')
        ordering = ['keyword', 'priority']
    
    def __str__(self):
        return f"{self.keyword.keyword} - {self.content_type.name}"