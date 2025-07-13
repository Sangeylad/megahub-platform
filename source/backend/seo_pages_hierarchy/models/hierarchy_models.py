# backend/seo_pages_hierarchy/models/hierarchy_models.py

from django.db import models
from django.core.exceptions import ValidationError

from .base_models import PageHierarchyBaseModel

class PageHierarchy(PageHierarchyBaseModel):
    """Hiérarchie parent-enfant des pages (3 niveaux max)"""
    
    page = models.OneToOneField(
        'seo_pages_content.Page',
        on_delete=models.CASCADE,
        related_name='hierarchy'
    )
    
    parent = models.ForeignKey(
        'seo_pages_content.Page',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='children_hierarchy'
    )
    
    def clean(self):
        """Validation hiérarchie 3 niveaux max"""
        super().clean()
        
        if self.parent and self.page == self.parent:
            raise ValidationError("Une page ne peut pas être son propre parent")
        
        if self.parent:
            # Vérifier niveau max
            if hasattr(self.parent, 'hierarchy') and self.parent.hierarchy.parent:
                if hasattr(self.parent.hierarchy.parent, 'hierarchy') and self.parent.hierarchy.parent.hierarchy.parent:
                    raise ValidationError("Hiérarchie limitée à 3 niveaux maximum")
    
    def get_level(self):
        """Retourne le niveau hiérarchique (1-3)"""
        if not self.parent:
            return 1
        elif not hasattr(self.parent, 'hierarchy') or not self.parent.hierarchy.parent:
            return 2
        else:
            return 3
    
    def get_root_page(self):
        """Retourne la page racine"""
        current = self.page
        while hasattr(current, 'hierarchy') and current.hierarchy.parent:
            current = current.hierarchy.parent
        return current
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Hierarchy: {self.page.title} (Level {self.get_level()})"
    
    class Meta:
        db_table = 'seo_pages_hierarchy_hierarchy'
        ordering = ['page', '-created_at']  # 🔧 AJOUTER CETTE LIGNE
        verbose_name = "Hiérarchie de Page"
        verbose_name_plural = "Hiérarchies de Page"
        indexes = [
            models.Index(fields=['page', 'parent']),
        ]