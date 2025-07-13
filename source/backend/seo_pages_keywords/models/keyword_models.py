# backend/seo_pages_keywords/models/keyword_models.py

from django.db import models
from django.core.exceptions import ValidationError

from .base_models import PageKeywordsBaseModel

class PageKeyword(PageKeywordsBaseModel):
    """Association entre une page et un mot-clé"""
    
    KEYWORD_TYPE_CHOICES = [
        ('primary', 'Primaire'),
        ('secondary', 'Secondaire'),
        ('anchor', 'Ancre')
    ]
    
    page = models.ForeignKey(
        'seo_pages_content.Page',
        on_delete=models.CASCADE,
        related_name='page_keywords'
    )
    keyword = models.ForeignKey(
        'seo_keywords_base.Keyword',
        on_delete=models.CASCADE,
        related_name='page_associations'
    )
    position = models.IntegerField(null=True, blank=True)
    keyword_type = models.CharField(
        max_length=20,
        choices=KEYWORD_TYPE_CHOICES,
        default='secondary'
    )
    
    # Référence au cocon source
    source_cocoon = models.ForeignKey(
        'seo_keywords_cocoons.SemanticCocoon',  # ← FIX: Nouvelle référence
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='page_keyword_associations'
    )
    
    # Flag pour sélection IA
    is_ai_selected = models.BooleanField(
        default=False,
        help_text="Mot-clé sélectionné automatiquement par l'IA"
    )
    notes = models.TextField(null=True, blank=True)
    
    def clean(self):
        """Validation métier"""
        super().clean()
        
        # Un seul mot-clé primaire par page
        if self.keyword_type == 'primary':
            existing_primary = PageKeyword.objects.filter(
                page=self.page,
                keyword_type='primary'
            ).exclude(pk=self.pk)
            
            if existing_primary.exists():
                raise ValidationError({
                    'keyword_type': 'Une page ne peut avoir qu\'un seul mot-clé primaire.'
                })
        
        # Pas de doublon keyword/page
        existing = PageKeyword.objects.filter(
            page=self.page,
            keyword=self.keyword
        ).exclude(pk=self.pk)
        
        if existing.exists():
            raise ValidationError({
                'keyword': 'Ce mot-clé est déjà assigné à cette page.'
            })
    
    def save(self, *args, **kwargs):
        """Override save pour validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_keyword_volume(self):
        """Volume du mot-clé"""
        return self.keyword.volume if self.keyword else 0
    
    def is_from_cocoon(self):
        """Vérifie si le mot-clé vient d'un cocon"""
        return self.source_cocoon is not None
    
    def __str__(self):
        return f"{self.page.title} - {self.keyword.keyword} ({self.keyword_type})"
    
    class Meta:
        db_table = 'seo_pages_keywords_association'
        unique_together = ('page', 'keyword')
        ordering = ['page', 'keyword_type', 'position']
        verbose_name = "Association Page-Mot clé"
        verbose_name_plural = "Associations Page-Mot clé"
        indexes = [
            models.Index(fields=['page', 'keyword_type']),
            models.Index(fields=['keyword_type', 'is_ai_selected']),
            models.Index(fields=['source_cocoon']),
        ]
