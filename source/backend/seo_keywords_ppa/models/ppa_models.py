# backend/seo_keywords_ppa/models/ppa_models.py

from django.db import models
from django.core.exceptions import ValidationError
from common.models.mixins import TimestampedMixin

class PPA(TimestampedMixin):
    """Questions 'People Also Ask' uniques"""
    
    question = models.TextField(unique=True)
    
    def __str__(self):
        return self.question[:100] + "..." if len(self.question) > 100 else self.question
    
    class Meta:
        db_table = 'seo_keywords_ppa_ppa'
        ordering = ['question']

class KeywordPPA(TimestampedMixin):
    """Association Keyword ↔ PPA avec position"""
    
    keyword = models.ForeignKey(
        'seo_keywords_base.Keyword', 
        on_delete=models.CASCADE, 
        related_name='ppa_associations'
    )
    ppa = models.ForeignKey(
        PPA, 
        on_delete=models.CASCADE, 
        related_name='keyword_associations'
    )
    position = models.IntegerField()
    
    class Meta:
        db_table = 'seo_keywords_ppa_keywordppa'
        unique_together = ('keyword', 'ppa', 'position')
        ordering = ['keyword', 'position']
    
    def clean(self):
        if self.position < 1 or self.position > 4:
            raise ValidationError("Position must be between 1 and 4")
    
    def __str__(self):
        return f"{self.keyword.keyword} - {self.ppa.question[:50]}... (Pos: {self.position})"