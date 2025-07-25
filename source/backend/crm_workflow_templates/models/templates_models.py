# /var/www/megahub/backend/crm_workflow_templates/models/templates_models.py
import uuid
from django.db import models
from crm_workflow_core.models import WorkflowBaseMixin

class WorkflowTemplate(WorkflowBaseMixin):
    """Templates de workflows réutilisables"""
    
    TEMPLATE_CATEGORIES = [
        ('lead_management', 'Gestion de Leads'),
        ('sales_process', 'Processus de Vente'),
        ('customer_onboarding', 'Onboarding Client'),
        ('customer_retention', 'Fidélisation Client'),
        ('support_automation', 'Automatisation Support'),
        ('data_management', 'Gestion de Données'),
        ('reporting', 'Reporting'),
        ('compliance', 'Conformité'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom du template"
    )
    display_name = models.CharField(
        max_length=150,
        help_text="Nom d'affichage"
    )
    
    # Classification
    category = models.CharField(
        max_length=20,
        choices=TEMPLATE_CATEGORIES,
        help_text="Catégorie du template"
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags du template"
    )
    
    # Contenu
    description = models.TextField(
        help_text="Description détaillée"
    )
    use_case = models.TextField(
        blank=True,
        help_text="Cas d'usage typique"
    )
    
    # Configuration du template
    template_config = models.JSONField(
        default=dict,
        help_text="Configuration complète du workflow"
    )
    steps_config = models.JSONField(
        default=list,
        help_text="Configuration des étapes"
    )
    variables = models.JSONField(
        default=dict,
        blank=True,
        help_text="Variables paramétrables"
    )
    
    # Métadonnées
    prerequisites = models.JSONField(
        default=list,
        blank=True,
        help_text="Prérequis pour utiliser ce template"
    )
    complexity_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Débutant'),
            ('intermediate', 'Intermédiaire'),
            ('advanced', 'Avancé'),
            ('expert', 'Expert'),
        ],
        default='intermediate',
        help_text="Niveau de complexité"
    )
    
    # Publication
    is_public = models.BooleanField(
        default=False,
        help_text="Template public (marketplace)"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Template mis en avant"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Template vérifié par l'équipe"
    )
    
    # Statistiques d'usage
    usage_count = models.IntegerField(
        default=0,
        help_text="Nombre d'utilisations"
    )
    rating_average = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Note moyenne"
    )
    rating_count = models.IntegerField(
        default=0,
        help_text="Nombre d'évaluations"
    )
    
    # Versioning
    version = models.CharField(
        max_length=20,
        default='1.0.0',
        help_text="Version du template"
    )
    changelog = models.TextField(
        blank=True,
        help_text="Journal des modifications"
    )
    
    class Meta:
        db_table = 'crm_workflow_template'
        ordering = ['-is_featured', '-rating_average', '-usage_count']
        verbose_name = 'Template Workflow'
        verbose_name_plural = 'Templates Workflow'
        indexes = [
            models.Index(fields=['category', 'is_public']),
            models.Index(fields=['is_featured', 'is_verified']),
            models.Index(fields=['rating_average', 'usage_count']),
        ]
    
    def __str__(self):
        return self.display_name
    
    def increment_usage(self):
        """Incrémente le compteur d'usage"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
    
    def add_rating(self, rating):
        """Ajoute une évaluation"""
        current_total = (self.rating_average or 0) * self.rating_count
        new_total = current_total + rating
        self.rating_count += 1
        self.rating_average = new_total / self.rating_count
        self.save(update_fields=['rating_average', 'rating_count'])
    
    def create_workflow_from_template(self, **kwargs):
        """Crée un workflow basé sur ce template"""
        from crm_workflow_core.models import Workflow, WorkflowStep
        
        # Configuration par défaut du template
        config = self.template_config.copy()
        config.update(kwargs)
        
        # Créer le workflow
        workflow = Workflow.objects.create(
            name=config.get('name', self.name),
            workflow_type=config.get('workflow_type', 'custom'),
            description=config.get('description', self.description),
            trigger_event=config.get('trigger_event', 'manual'),
            trigger_object=config.get('trigger_object', 'Account'),
            trigger_conditions=config.get('trigger_conditions', {}),
            brand=kwargs['brand'],
            owner=kwargs['owner'],
            company_category=config.get('company_category'),
            is_template=False
        )
        
        # Créer les étapes
        for step_config in self.steps_config:
            WorkflowStep.objects.create(
                workflow=workflow,
                name=step_config['name'],
                step_type=step_config['step_type'],
                step_order=step_config['step_order'],
                step_config=step_config.get('config', {}),
                conditions=step_config.get('conditions', {}),
                delay_hours=step_config.get('delay_hours', 0),
                description=step_config.get('description', ''),
                brand=kwargs['brand'],
                owner=kwargs['owner']
            )
        
        # Incrémenter l'usage
        self.increment_usage()
        
        return workflow

class TemplateRating(WorkflowBaseMixin):
    """Évaluations des templates"""
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        WorkflowTemplate,
        on_delete=models.CASCADE,
        related_name='ratings',
        help_text="Template évalué"
    )
    user = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.CASCADE,
        related_name='template_ratings',
        help_text="Utilisateur qui évalue"
    )
    
    # Évaluation
    rating = models.IntegerField(
        help_text="Note (1-5)"
    )
    review = models.TextField(
        blank=True,
        help_text="Commentaire"
    )
    
    # Métadonnées
    usage_context = models.CharField(
        max_length=100,
        blank=True,
        help_text="Contexte d'utilisation"
    )
    would_recommend = models.BooleanField(
        default=True,
        help_text="Recommanderait ce template"
    )
    
    class Meta:
        db_table = 'crm_template_rating'
        unique_together = ['template', 'user']
        ordering = ['-created_at']
        verbose_name = 'Évaluation Template'
        verbose_name_plural = 'Évaluations Template'
    
    def __str__(self):
        return f"{self.template.name} - {self.rating}/5 par {self.user.get_full_name()}"

class IndustryWorkflowPreset(WorkflowBaseMixin):
    """Presets de workflows par industrie"""
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom du preset"
    )
    
    # Industry specific
    industry_category = models.ForeignKey(
        'company_categorization_core.IndustryCategory',
        on_delete=models.CASCADE,
        related_name='workflow_presets',
        help_text="Catégorie d'industrie"
    )
    
    # Configuration
    preset_config = models.JSONField(
        default=dict,
        help_text="Configuration preset"
    )
    included_templates = models.ManyToManyField(
        WorkflowTemplate,
        related_name='industry_presets',
        help_text="Templates inclus dans le preset"
    )
    
    # Métadonnées
    description = models.TextField(
        help_text="Description du preset"
    )
    benefits = models.JSONField(
        default=list,
        blank=True,
        help_text="Bénéfices du preset"
    )
    setup_time_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text="Temps de setup estimé (minutes)"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        help_text="Preset actif"
    )
    
    class Meta:
        db_table = 'crm_industry_workflow_preset'
        ordering = ['industry_category', 'name']
        verbose_name = 'Preset Workflow Industrie'
        verbose_name_plural = 'Presets Workflow Industries'
        indexes = [
            models.Index(fields=['industry_category', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.industry_category.name})"
