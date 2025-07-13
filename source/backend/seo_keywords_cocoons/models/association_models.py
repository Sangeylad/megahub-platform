# backend/seo_keywords_cocoons/models/association_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class CocoonKeyword(TimestampedMixin):
    """Association Cocoon ↔ Keyword"""
    
    cocoon = models.ForeignKey(
        'SemanticCocoon', 
        on_delete=models.CASCADE, 
        related_name='cocoon_keywords'
    )
    keyword = models.ForeignKey(
        'seo_keywords_base.Keyword', 
        on_delete=models.CASCADE, 
        related_name='cocoon_associations'
    )
    
    class Meta:
        db_table = 'seo_keywords_cocoons_cocoonkeyword'
        unique_together = ('cocoon', 'keyword')
        ordering = ['cocoon__name', '-keyword__volume']
    
    def __str__(self):
        return f"{self.cocoon.name} - {self.keyword.keyword}"