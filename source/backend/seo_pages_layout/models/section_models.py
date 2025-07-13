# backend/seo_pages_layout/models/section_models.py

from django.db import models
from django.core.exceptions import ValidationError

from .base_models import PageLayoutBaseModel

class PageSection(PageLayoutBaseModel):
    """Sections du page builder avec hiérarchie parent-enfant"""
    
    page = models.ForeignKey(
        'seo_pages_content.Page',
        on_delete=models.CASCADE,
        related_name='sections'
    )
    
    # Hiérarchie parent-enfant (2 niveaux max)
    parent_section = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='child_sections'
    )
    
    SECTION_TYPE_CHOICES = [
        # Layout containers
        ('layout_columns', 'Layout en Colonnes'),
        ('layout_grid', 'Layout en Grille'),
        ('layout_stack', 'Layout Vertical'),
        
        # Content sections
        ('hero_banner', 'Hero Banner'),
        ('cta_banner', 'CTA Banner'),
        ('features_grid', 'Features Grid'),
        ('rich_text', 'Rich Text Block'),
    ]
    
    section_type = models.CharField(
        max_length=50,
        choices=SECTION_TYPE_CHOICES
    )
    
    data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Props JSON pour React"
    )

    # Configuration CSS Grid
    layout_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Config CSS Grid : {columns: [8, 4], gap: '2rem'}"
    )
    
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    version = models.CharField(max_length=10, default='1.0')
    
    created_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    
    def clean(self):
        """Validation hiérarchie 2 niveaux max et même page"""
        super().clean()
        
        if self.parent_section:
            # Vérifier hiérarchie 2 niveaux max
            if self.parent_section.parent_section:
                raise ValidationError(
                    "Hiérarchie limitée à 2 niveaux : Container → Enfants"
                )
            
            # Vérifier que le parent est sur la même page
            if self.parent_section.page_id != self.page_id:
                raise ValidationError(
                    "La section parent doit être sur la même page"
                )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.page.title} - {self.get_section_type_display()}"
    
    class Meta:
        db_table = 'seo_pages_layout_section'
        unique_together = ['page', 'parent_section', 'order']
        # 🔧 FIX: Simplifier l'ordering pour éviter la boucle infinie
        ordering = ['order', 'created_at']  # Au lieu de ['page', 'parent_section', 'order']
        verbose_name = "Section de Page"
        verbose_name_plural = "Sections de Page"
        indexes = [
            models.Index(fields=['page', 'parent_section', 'order']),
            models.Index(fields=['order', 'created_at']),  # Index pour le nouvel ordering
        ]