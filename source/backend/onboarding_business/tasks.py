# backend/onboarding_business/tasks.py

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def daily_onboarding_maintenance(self):
    """
    Tâche quotidienne de maintenance onboarding
    Intégrée avec le système task_core de MEGAHUB
    """
    try:
        # Créer une Task dans task_core pour le monitoring
        from task_core.models import Task
        
        # Enregistrer la tâche dans le système MEGAHUB
        task_instance = Task.objects.create(
            task_id=self.request.id,
            task_type='onboarding_maintenance',
            status='running',
            priority='normal',
            description='Maintenance quotidienne système onboarding',
            context_data={
                'app': 'onboarding_business',
                'type': 'daily_maintenance',
                'scheduled': True
            },
            brand=None,  # Tâche système
            created_by=None  # Automatique
        )
        
        # Logique de maintenance
        from company_core.models import Company
        
        today = timezone.now().date()
        
        # Compter trials expirant
        warnings_7d = Company.objects.filter(
            trial_expires_at__date=today + timedelta(days=7),
            is_active=True
        ).count()
        
        warnings_3d = Company.objects.filter(
            trial_expires_at__date=today + timedelta(days=3),
            is_active=True
        ).count()
        
        warnings_1d = Company.objects.filter(
            trial_expires_at__date=today + timedelta(days=1),
            is_active=True
        ).count()
        
        expired_today = Company.objects.filter(
            trial_expires_at__date=today,
            is_active=True
        ).count()
        
        # Résultats
        result_data = {
            'warnings_7d': warnings_7d,
            'warnings_3d': warnings_3d, 
            'warnings_1d': warnings_1d,
            'expired_today': expired_today,
            'maintenance_date': today.isoformat()
        }
        
        # Finaliser la tâche dans task_core
        task_instance.status = 'completed'
        task_instance.result_data = result_data
        task_instance.completed_at = timezone.now()
        task_instance.save()
        
        # Créer métriques pour monitoring
        try:
            from task_monitoring.models import TaskMetrics
            TaskMetrics.objects.create(
                base_task=task_instance,
                execution_time_ms=int((timezone.now() - task_instance.created_at).total_seconds() * 1000),
                memory_usage_mb=50,  # Estimation
                cpu_usage_percent=10,  # Estimation
                cost_usd=0.001  # Estimation
            )
        except ImportError:
            pass
        
        logger.info(f"Onboarding maintenance completed: {result_data}")
        return result_data
        
    except Exception as e:
        # Marquer tâche comme failed dans task_core
        if 'task_instance' in locals():
            task_instance.status = 'failed'
            task_instance.error_message = str(e)
            task_instance.save()
            
        logger.error(f"Onboarding maintenance failed: {e}", exc_info=True)
        raise


@shared_task(bind=True)
def cleanup_onboarding_data(self):
    """
    Nettoyage périodique des données onboarding
    Job persistant pour gros volumes
    """
    try:
        # Créer Job Persistant si nécessaire
        from task_persistence.models import PersistentJob
        from task_core.models import Task
        
        # Tâche de base
        base_task = Task.objects.create(
            task_id=self.request.id,
            task_type='onboarding_cleanup',
            status='running',
            priority='low',
            description='Nettoyage données onboarding anciennes',
            context_data={
                'app': 'onboarding_business',
                'type': 'data_cleanup',
                'estimated_duration': '30min'
            }
        )
        
        # Job persistant pour pouvoir reprendre si interruption
        persistent_job = PersistentJob.objects.create(
            base_task=base_task,
            job_data={
                'cutoff_days': 90,
                'total_companies': 0,
                'processed_companies': 0
            },
            current_step='initialization',
            total_steps=3,
            can_resume=True
        )
        
        # Étape 1: Identifier les données à nettoyer
        from company_core.models import Company
        cutoff_date = timezone.now() - timedelta(days=90)
        
        old_companies = Company.objects.filter(
            is_deleted=True,
            deleted_at__lt=cutoff_date
        )
        
        total_count = old_companies.count()
        persistent_job.job_data['total_companies'] = total_count
        persistent_job.current_step = 'processing'
        persistent_job.save()
        
        # Étape 2: Supprimer par batch (pour éviter timeout)
        batch_size = 50
        processed = 0
        
        for batch_start in range(0, total_count, batch_size):
            batch_companies = old_companies[batch_start:batch_start + batch_size]
            batch_companies.delete()
            
            processed += len(batch_companies)
            
            # Mettre à jour progression
            persistent_job.job_data['processed_companies'] = processed
            persistent_job.progress_percentage = int((processed / total_count) * 100) if total_count > 0 else 100
            persistent_job.save()
            
            # Checkpoint pour reprise possible
            if processed % 200 == 0:  # Checkpoint tous les 200 items
                from task_persistence.models import JobCheckpoint
                JobCheckpoint.objects.create(
                    persistent_job=persistent_job,
                    checkpoint_data={
                        'processed_count': processed,
                        'last_processed_id': batch_companies.last().id if batch_companies else None
                    },
                    description=f"Processed {processed}/{total_count} companies"
                )
        
        # Étape 3: Finalisation
        persistent_job.current_step = 'finalization'
        persistent_job.progress_percentage = 100
        persistent_job.save()
        
        # Finaliser tâche
        base_task.status = 'completed'
        base_task.result_data = {
            'cleaned_companies': processed,
            'total_companies': total_count,
            'cleanup_date': timezone.now().isoformat()
        }
        base_task.completed_at = timezone.now()
        base_task.save()
        
        logger.info(f"Onboarding cleanup completed: {processed} companies cleaned")
        return {'cleaned_companies': processed}
        
    except Exception as e:
        # Marquer comme failed mais garder job pour reprise
        if 'base_task' in locals():
            base_task.status = 'failed'
            base_task.error_message = str(e)
            base_task.save()
            
        if 'persistent_job' in locals():
            persistent_job.current_step = 'error'
            persistent_job.save()
            
        logger.error(f"Onboarding cleanup failed: {e}", exc_info=True)
        raise


# Fonction pour programmer les tâches avec task_scheduling
def setup_onboarding_scheduled_tasks():
    """
    Configure les tâches programmées pour onboarding
    À appeler dans les migrations ou management commands
    """
    try:
        from task_scheduling.models import PeriodicTask
        
        # Tâche quotidienne de maintenance (8h du matin)
        maintenance_task, created = PeriodicTask.objects.get_or_create(
            name='onboarding_daily_maintenance',
            defaults={
                'task_type': 'onboarding_maintenance',
                'cron_expression': '0 8 * * *',  # 8h tous les jours
                'timezone': 'Europe/Paris',
                'is_active': True,
                'description': 'Maintenance quotidienne système onboarding',
                'task_module': 'onboarding_business.tasks',
                'task_function': 'daily_onboarding_maintenance'
            }
        )
        
        # Tâche de nettoyage (dimanche 2h du matin, hebdomadaire)
        cleanup_task, created = PeriodicTask.objects.get_or_create(
            name='onboarding_weekly_cleanup',
            defaults={
                'task_type': 'onboarding_cleanup',
                'cron_expression': '0 2 * * 0',  # Dimanche 2h
                'timezone': 'Europe/Paris',
                'is_active': True,
                'description': 'Nettoyage hebdomadaire données onboarding',
                'task_module': 'onboarding_business.tasks',
                'task_function': 'cleanup_onboarding_data'
            }
        )
        
        logger.info(f"Scheduled tasks configured: maintenance={'created' if created else 'updated'}")
        
    except ImportError:
        logger.warning("task_scheduling not available - tasks not scheduled")
    except Exception as e:
        logger.error(f"Error setting up scheduled tasks: {e}")


# Helper pour trigger manual
@shared_task(bind=True)
def trigger_business_analysis(self, company_id):
    """
    Analyse business spécifique - Tâche sur demande
    """
    try:
        from task_core.models import Task
        from company_core.models import Company
        
        company = Company.objects.get(id=company_id)
        
        # Créer tâche trackée
        task_instance = Task.objects.create(
            task_id=self.request.id,
            task_type='business_analysis',
            status='running',
            priority='normal',
            description=f'Analyse business {company.name}',
            context_data={
                'company_id': company_id,
                'company_name': company.name,
                'trigger': 'manual'
            }
        )
        
        # Logique d'analyse
        analysis_result = {
            'business_mode': company.get_business_mode(),
            'trial_status': company.is_in_trial(),
            'brands_count': company.brands.filter(is_deleted=False).count(),
            'users_count': company.members.filter(is_active=True).count(),
            'analysis_date': timezone.now().isoformat()
        }
        
        # Finaliser
        task_instance.status = 'completed'
        task_instance.result_data = analysis_result
        task_instance.completed_at = timezone.now()
        task_instance.save()
        
        return analysis_result
        
    except Exception as e:
        if 'task_instance' in locals():
            task_instance.status = 'failed'
            task_instance.error_message = str(e)
            task_instance.save()
        raise