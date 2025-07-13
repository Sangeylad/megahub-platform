# backend/ai_templates_categories/models/category_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class TemplateCategory(TimestampedMixin):
    """Catégories hiérarchiques pour templates"""
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    level = models.PositiveIntegerField(default=1, help_text="Niveau dans la hiérarchie (1-3)")
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    icon_name = models.CharField(max_length=50, blank=True, help_text="Nom icône Lucide")
    
    class Meta:
        db_table = 'template_category'
        ordering = ['level', 'sort_order', 'name']
        indexes = [
            models.Index(fields=['parent', 'is_active']),
            models.Index(fields=['level', 'sort_order'])
        ]
        unique_together = ['parent', 'name']
    
    def __str__(self):
        if self.level > 1:
            return f"{'→' * (self.level - 1)} {self.display_name}"
        return self.display_name
    
    def save(self, *args, **kwargs):
        """Auto-calcul du niveau"""
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 1
        super().save(*args, **kwargs)

class TemplateTag(TimestampedMixin):
    """Tags libres pour templates"""
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default='blue', help_text="Couleur Tailwind")
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0, help_text="Nombre d'utilisations")
    
    class Meta:
        db_table = 'template_tag'
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return self.display_name

class CategoryPermission(TimestampedMixin):
    """Permissions d'accès par catégorie selon plan/rôle"""
    category = models.ForeignKey(TemplateCategory, on_delete=models.CASCADE, related_name='permissions')
    permission_type = models.CharField(max_length=20, choices=[
        ('view', 'Voir'),
        ('create', 'Créer'),
        ('edit', 'Modifier'),
        ('admin', 'Administration')
    ])
    required_plan = models.CharField(max_length=50, choices=[
        ('free', 'Gratuit'),
        ('starter', 'Starter'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise')
    ], default='free')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'category_permission'
        unique_together = ['category', 'permission_type', 'required_plan']
    
    def __str__(self):
        return f"{self.category.name} - {self.permission_type} ({self.required_plan})"
