# backend/task_scheduling/models/schedule_models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone as django_timezone
from django.core.exceptions import ValidationError
from common.models.mixins import TimestampedMixin, BrandScopedMixin
from task_core.models import BaseTask
from croniter import croniter
from datetime import datetime

User = get_user_model()

class PeriodicTask(TimestampedMixin):
    """
    Extension OneToOne de BaseTask pour tâches périodiques
    """
    
    # Relation vers BaseTask (hub central)
    base_task = models.OneToOneField(
        BaseTask, 
        on_delete=models.CASCADE, 
        related_name='periodic_task'
    )
    
    # Configuration du planning
    cron_expression = models.CharField(
        max_length=100, 
        help_text="Expression cron (ex: '0 9 * * 1' pour lundi 9h)"
    )
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Dates de planification
    start_date = models.DateTimeField(default=django_timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField()
    last_run_at = models.DateTimeField(null=True, blank=True)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    max_executions = models.PositiveIntegerField(null=True, blank=True)
    executions_count = models.PositiveIntegerField(default=0)
    
    # Données pour l'exécution
    schedule_config = models.JSONField(
        default=dict, 
        help_text="Config spécifique à l'exécution"
    )
    
    class Meta:
        db_table = 'task_periodic_task'
        indexes = [
            models.Index(fields=['is_active', 'next_run_at']),
            models.Index(fields=['base_task', 'last_run_at']),
        ]
        
    def __str__(self):
        return f"Periodic: {self.base_task.task_id}"
    
    def clean(self):
        """Validation de l'expression cron"""
        if self.cron_expression:
            try:
                croniter(self.cron_expression)
            except ValueError as e:
                raise ValidationError(f"Expression cron invalide: {e}")
    
    def save(self, *args, **kwargs):
        """Calcule next_run_at lors de la sauvegarde"""
        if not self.next_run_at or self.cron_expression:
            self.calculate_next_run()
        super().save(*args, **kwargs)
    
    def calculate_next_run(self):
        """Calcule la prochaine exécution"""
        if not self.cron_expression:
            return
        
        base_time = self.last_run_at or django_timezone.now()
        cron = croniter(self.cron_expression, base_time)
        self.next_run_at = cron.get_next(datetime)
    
    def is_ready_to_run(self) -> bool:
        """Vérifie si la tâche est prête à être exécutée"""
        if not self.is_active:
            return False
        
        if self.end_date and django_timezone.now() > self.end_date:
            return False
        
        if self.max_executions and self.executions_count >= self.max_executions:
            return False
        
        return django_timezone.now() >= self.next_run_at
    
    def mark_executed(self):
        """Marque la tâche comme exécutée et calcule la prochaine"""
        self.last_run_at = django_timezone.now()
        self.executions_count += 1
        self.calculate_next_run()
        
        # Désactiver si max atteint
        if self.max_executions and self.executions_count >= self.max_executions:
            self.is_active = False
        
        self.save(update_fields=['last_run_at', 'executions_count', 'next_run_at', 'is_active'])

class CronJob(TimestampedMixin, BrandScopedMixin):
    """Jobs cron préfabriqués pour tâches récurrentes communes"""
    
    FREQUENCY_CHOICES = [
        ('minutely', 'Chaque minute'),
        ('hourly', 'Toutes les heures'),
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'), 
        ('monthly', 'Mensuel'),
        ('custom', 'Expression cron personnalisée'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=100)
    
    # Planning
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    custom_cron = models.CharField(max_length=100, blank=True)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    task_config = models.JSONField(
        default=dict, 
        help_text="Configuration pour la tâche"
    )
    
    # Statistiques
    last_execution_at = models.DateTimeField(null=True, blank=True)
    total_executions = models.PositiveIntegerField(default=0)
    successful_executions = models.PositiveIntegerField(default=0)
    failed_executions = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'task_cron_job'
        unique_together = ['brand', 'name']
        indexes = [
            models.Index(fields=['is_active', 'frequency']),
            models.Index(fields=['brand', 'task_type']),
        ]
        
    def __str__(self):
        return f"CronJob: {self.name}"
    
    def get_cron_expression(self) -> str:
        """Retourne l'expression cron selon la fréquence"""
        
        frequency_map = {
            'minutely': '* * * * *',
            'hourly': '0 * * * *',
            'daily': '0 9 * * *',      # 9h chaque jour
            'weekly': '0 9 * * 1',     # 9h chaque lundi
            'monthly': '0 9 1 * *',    # 9h le 1er de chaque mois
        }
        
        if self.frequency == 'custom':
            return self.custom_cron
        
        return frequency_map.get(self.frequency, '0 9 * * *')

class TaskCalendar(TimestampedMixin, BrandScopedMixin):
    """Calendrier de planification pour grouper les tâches"""
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6366f1')  # Couleur hex pour UI
    
    # Configuration
    is_active = models.BooleanField(default=True)
    default_timezone = models.CharField(max_length=50, default='UTC')
    
    class Meta:
        db_table = 'task_calendar'
        unique_together = ['brand', 'name']
        
    def __str__(self):
        return f"Calendar: {self.name}"

class CalendarTask(TimestampedMixin):
    """Association entre calendrier et tâche périodique"""
    
    calendar = models.ForeignKey(TaskCalendar, on_delete=models.CASCADE)
    periodic_task = models.ForeignKey(PeriodicTask, on_delete=models.CASCADE)
    
    # Surcharge spécifique au calendrier
    custom_cron = models.CharField(max_length=100, blank=True)
    custom_config = models.JSONField(default=dict, blank=True)
    is_active_in_calendar = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'task_calendar_task'
        unique_together = ['calendar', 'periodic_task']
        
    def __str__(self):
        return f"{self.calendar.name} → {self.periodic_task}"