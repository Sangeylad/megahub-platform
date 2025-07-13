# backend/seo_pages_hierarchy/models/breadcrumb_models.py

from django.db import models

from .base_models import PageHierarchyBaseModel

class PageBreadcrumb(PageHierarchyBaseModel):
    """Cache du fil d'Ariane pour performance"""
    
    page = models.OneToOneField(
        'seo_pages_content.Page',
        on_delete=models.CASCADE,
        related_name='breadcrumb_cache'
    )
    
    breadcrumb_json = models.JSONField(
        default=list,
        help_text="Cache JSON du fil d'Ariane"
    )
    
    def regenerate_breadcrumb(self):
        """Régénère le fil d'Ariane"""
        breadcrumb = []
        current = self.page
        
        # Construire le breadcrumb en remontant
        while current:
            breadcrumb.insert(0, {
                'title': current.title,
                'url': current.url_path,
                'page_id': current.id
            })
            
            # Remonter au parent
            if hasattr(current, 'hierarchy') and current.hierarchy.parent:
                current = current.hierarchy.parent
            else:
                break
        
        self.breadcrumb_json = breadcrumb
        self.save(update_fields=['breadcrumb_json', 'updated_at'])
        return breadcrumb
    
    def __str__(self):
        return f"Breadcrumb: {self.page.title}"
    
    class Meta:
        db_table = 'seo_pages_hierarchy_breadcrumb'
        ordering = ['page', '-updated_at']  # 🔧 AJOUTER CETTE LIGNE
        verbose_name = "Fil d'Ariane"
        verbose_name_plural = "Fils d'Ariane"
        indexes = [
            models.Index(fields=['page']),
        ]
