# backend/ai_templates_workflow/models/workflow_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class TemplateValidationRule(TimestampedMixin):
    """Règles de validation pour templates"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    rule_type = models.CharField(max_length=50, choices=[
        ('security', 'Sécurité'),
        ('quality', 'Qualité'),
        ('format', 'Format'),
        ('content', 'Contenu')
    ])
    validation_function = models.CharField(max_length=200, help_text="Nom de la fonction de validation")
    is_active = models.BooleanField(default=True)
    is_blocking = models.BooleanField(default=False, help_text="Bloque la publication si échec")
    error_message = models.TextField(help_text="Message d'erreur si validation échoue")
    
    class Meta:
        db_table = 'template_validation_rule'
        ordering = ['rule_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.rule_type})"

class TemplateValidationResult(TimestampedMixin):
    """Résultats des validations de templates"""
    template = models.ForeignKey('ai_templates_core.BaseTemplate', on_delete=models.CASCADE, related_name='validation_results')
    validation_rule = models.ForeignKey(TemplateValidationRule, on_delete=models.CASCADE)
    is_valid = models.BooleanField()
    error_details = models.TextField(blank=True)
    validated_by = models.ForeignKey('users_core.CustomUser', on_delete=models.SET_NULL, null=True)
    validation_data = models.JSONField(default=dict, help_text="Données techniques de la validation")
    
    class Meta:
        db_table = 'template_validation_result'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['template', 'is_valid']),
            models.Index(fields=['validation_rule', 'created_at'])
        ]
    
    def __str__(self):
        status = "✅" if self.is_valid else "❌"
        return f"{status} {self.template.name} - {self.validation_rule.name}"

class TemplateApproval(TimestampedMixin):
    """Processus d'approbation des templates"""
    template = models.ForeignKey('ai_templates_core.BaseTemplate', on_delete=models.CASCADE, related_name='approvals')
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Brouillon'),
        ('pending_review', 'En attente de review'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('published', 'Publié')
    ], default='draft')
    submitted_by = models.ForeignKey('users_core.CustomUser', on_delete=models.SET_NULL, null=True, related_name='submitted_approvals')
    reviewed_by = models.ForeignKey('users_core.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_approvals')
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'template_approval'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['template', 'status']),
            models.Index(fields=['status', 'submitted_at'])
        ]
    
    def __str__(self):
        return f"{self.template.name} - {self.status}"

class TemplateReview(TimestampedMixin):
    """Commentaires et retours lors des reviews"""
    approval = models.ForeignKey(TemplateApproval, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey('users_core.CustomUser', on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    review_type = models.CharField(max_length=20, choices=[
        ('comment', 'Commentaire'),
        ('suggestion', 'Suggestion'),
        ('approval', 'Approbation'),
        ('rejection', 'Rejet')
    ])
    
    class Meta:
        db_table = 'template_review'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review {self.approval.template.name} par {self.reviewer.username}"
