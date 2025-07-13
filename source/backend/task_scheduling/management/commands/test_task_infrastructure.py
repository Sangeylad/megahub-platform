# backend/task_scheduling/management/commands/test_task_infrastructure.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
import json
import uuid

from brands_core.models import Brand
from task_core.models import BaseTask
from task_scheduling.models import PeriodicTask, CronJob, TaskCalendar
from task_persistence.models import PersistentJob, JobCheckpoint, JobState
from task_monitoring.models import TaskMetrics, AlertRule, WorkerHealth

User = get_user_model()

class Command(BaseCommand):
    help = 'Test complet de l\'infrastructure tasks'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-cleanup',
            action='store_true',
            help='Ne pas nettoyer les données de test'
        )
        parser.add_argument(
            '--force-cleanup',
            action='store_true',
            help='Nettoyer AVANT de commencer'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Testing MEGAHUB Task Infrastructure\n'))
        
        # Cleanup initial si demandé
        if options['force_cleanup']:
            self.cleanup_test_data()
        
        # Setup
        self.setup_test_data()
        
        # Tests par couche
        self.test_task_core()
        self.test_task_persistence() 
        self.test_task_monitoring()
        self.test_task_scheduling()
        
        # Tests d'intégration
        self.test_extensions_integration()
        
        if not options['skip_cleanup']:
            self.cleanup_test_data()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Tous les tests sont passés !'))
    
    def setup_test_data(self):
        """Prépare les données de test"""
        self.stdout.write('📝 Setup des données de test...')
        
        # Brand et user de test
        self.test_brand = Brand.objects.first()
        self.test_user = User.objects.first()
        
        if not self.test_brand:
            self.stdout.write(self.style.ERROR('❌ Aucune brand trouvée'))
            return
        
        self.stdout.write(f'  ✅ Brand: {self.test_brand.name}')
        self.stdout.write(f'  ✅ User: {self.test_user.username}')
    
    def test_task_core(self):
        """Test du hub central BaseTask"""
        self.stdout.write('\n🎯 Testing task_core (Hub Central)...')
        
        # Créer une BaseTask avec task_id généré manuellement
        unique_suffix = str(uuid.uuid4())[:8]
        task_id = f"test_infrastructure_{unique_suffix}"
        
        self.base_task = BaseTask.objects.create(
            task_id=task_id,  # 🎯 FORCER LE task_id
            task_type=f'test_infrastructure_{unique_suffix}',
            brand=self.test_brand,
            created_by=self.test_user,
            priority='normal',
            description='Test task infrastructure',
            context_data={'test': True}
        )
        
        self.stdout.write(f'  ✅ BaseTask créée: {self.base_task.task_id}')
        self.stdout.write(f'  ✅ Status: {self.base_task.status}')
        self.stdout.write(f'  ✅ Priority: {self.base_task.priority}')
        
        # Tester les statuts
        self.base_task.status = 'running'
        self.base_task.save()
        self.stdout.write(f'  ✅ Status modifié: {self.base_task.status}')
    def test_task_persistence(self):
        """Test des jobs persistants"""
        self.stdout.write('\n💾 Testing task_persistence (Jobs Persistants)...')
        
        # Créer un PersistentJob
        self.persistent_job = PersistentJob.objects.create(
            base_task=self.base_task,
            job_data={
                'total_pages': 100,
                'processed_pages': 0,
                'target_pages': list(range(1, 101))
            },
            current_step='initialization',
            total_steps=5,
            can_resume=True
        )
        
        self.stdout.write(f'  ✅ PersistentJob créé: {self.persistent_job.id}')
        self.stdout.write(f'  ✅ Current step: {self.persistent_job.current_step}')
        self.stdout.write(f'  ✅ Can resume: {self.persistent_job.can_resume}')
        self.stdout.write(f'  ✅ Progress: {self.persistent_job.progress_percentage}%')
        
        # Créer des checkpoints avec les bons champs
        for i in range(3):
            checkpoint = JobCheckpoint.objects.create(
                persistent_job=self.persistent_job,
                step_name=f'step_{i+1}',
                checkpoint_data={'processed': (i+1) * 20, 'timestamp': timezone.now().isoformat()}
            )
            self.stdout.write(f'  ✅ Checkpoint {i+1}: {checkpoint.step_name}')
        
        # Tester les méthodes du modèle
        self.persistent_job.mark_step_completed('step_2')
        self.stdout.write(f'  ✅ Step completed, nouveau progress: {self.persistent_job.progress_percentage}%')
        
        # Créer checkpoint via méthode
        self.persistent_job.create_checkpoint({'manual_checkpoint': True, 'data': 'test'})
        self.stdout.write(f'  ✅ Checkpoint créé via méthode')
        
        # Tester latest checkpoint
        latest = self.persistent_job.get_latest_checkpoint()
        if latest:
            self.stdout.write(f'  ✅ Latest checkpoint: {latest.step_name}')
        
        # Tester is_resumable
        self.stdout.write(f'  ✅ Is resumable: {self.persistent_job.is_resumable()}')
        
        # Créer JobState
        job_state = JobState.objects.create(
            persistent_job=self.persistent_job,
            pages_status={'page_1': 'completed', 'page_2': 'in_progress'},
            retry_count=0,
            max_retries=3
        )
        
        self.stdout.write(f'  ✅ JobState créé: {job_state.id}')
        
        # Tester add_error
        job_state.add_error('Test error message', page_id=123)
        self.stdout.write(f'  ✅ Error ajoutée: {job_state.last_error_message}')
        self.stdout.write(f'  ✅ Can retry: {job_state.can_retry()}')
    
    def test_task_monitoring(self):
        """Test du monitoring"""
        self.stdout.write('\n📊 Testing task_monitoring (Métriques)...')
        
        # Créer des métriques
        self.task_metrics = TaskMetrics.objects.create(
            base_task=self.base_task,
            execution_time_ms=1500,
            memory_usage_mb=256,
            cpu_usage_percent=45.5,
            error_count=0,
            queue_wait_time_ms=200,
            api_calls_count=5,
            tokens_used=1200,
            cost_usd=0.024
        )
        
        self.stdout.write(f'  ✅ TaskMetrics créées: {self.task_metrics.id}')
        self.stdout.write(f'  ✅ Execution time: {self.task_metrics.execution_time_ms}ms')
        self.stdout.write(f'  ✅ Memory usage: {self.task_metrics.memory_usage_mb}MB')
        self.stdout.write(f'  ✅ API calls: {self.task_metrics.api_calls_count}')
        self.stdout.write(f'  ✅ Cost: ${self.task_metrics.cost_usd}')
        
        # Créer une règle d'alerte avec les bons champs
        alert_rule = AlertRule.objects.create(
            name=f'Test Alert Rule {uuid.uuid4().hex[:8]}',
            brand=self.test_brand,
            description='Test alert for execution time',
            metric_field='execution_time_ms',
            condition='gt',
            threshold_value=2000,
            is_active=True,
            notification_emails=['admin@test.com'],
            cooldown_minutes=30
        )
        
        self.stdout.write(f'  ✅ AlertRule créée: {alert_rule.name}')
        self.stdout.write(f'  ✅ Metric: {alert_rule.metric_field}')
        self.stdout.write(f'  ✅ Condition: {alert_rule.condition} {alert_rule.threshold_value}')
        
        # Worker health (simulation)
        worker = WorkerHealth.objects.create(
            worker_name=f'test-worker-{uuid.uuid4().hex[:8]}',
            queue_name='normal',
            is_online=True,
            cpu_percent=25.0,
            memory_percent=60.0,
            active_tasks=3,
            processed_tasks=150,
            failed_tasks=2,
            load_average=1.5
        )
        
        self.stdout.write(f'  ✅ WorkerHealth créé: {worker.worker_name}')
        self.stdout.write(f'  ✅ Queue: {worker.queue_name}')
        self.stdout.write(f'  ✅ Active tasks: {worker.active_tasks}')
        self.stdout.write(f'  ✅ Success rate: {((worker.processed_tasks - worker.failed_tasks) / worker.processed_tasks * 100):.1f}%')
        
        
        
        
    def test_task_scheduling(self):
        """Test du scheduling"""
        self.stdout.write('\n⏰ Testing task_scheduling (Planification)...')
        
        # Créer une nouvelle BaseTask pour le périodique avec task_id forcé
        unique_suffix = str(uuid.uuid4())[:8]
        periodic_task_id = f"test_periodic_{unique_suffix}"
        
        periodic_base_task = BaseTask.objects.create(
            task_id=periodic_task_id,  # 🎯 FORCER LE task_id
            task_type=f'test_periodic_{unique_suffix}',
            brand=self.test_brand,
            created_by=self.test_user,
            priority='low'
        )
        
        # Créer une tâche périodique
        self.periodic_task = PeriodicTask.objects.create(
            base_task=periodic_base_task,
            cron_expression='0 9 * * 1-5',  # Weekdays 9am
            timezone='Europe/Paris'
        )
        
        self.stdout.write(f'  ✅ PeriodicTask créée: {self.periodic_task.id}')
        self.stdout.write(f'  ✅ Cron: {self.periodic_task.cron_expression}')
        self.stdout.write(f'  ✅ Next run: {self.periodic_task.next_run_at}')
        self.stdout.write(f'  ✅ Ready to run: {self.periodic_task.is_ready_to_run()}')
        
        # Créer un CronJob
        cron_job = CronJob.objects.create(
            name=f'Test Daily Backup {uuid.uuid4().hex[:8]}',
            brand=self.test_brand,
            task_type='backup',
            frequency='daily',
            task_config={'backup_type': 'full', 'retention_days': 7}
        )
        
        self.stdout.write(f'  ✅ CronJob créé: {cron_job.name}')
        self.stdout.write(f'  ✅ Frequency: {cron_job.frequency}')
        self.stdout.write(f'  ✅ Cron expression: {cron_job.get_cron_expression()}')
        
        # Créer un calendrier
        calendar = TaskCalendar.objects.create(
            name=f'Test Production Calendar {uuid.uuid4().hex[:8]}',
            brand=self.test_brand,
            description='Calendrier de test pour validation',
            color='#ff6b6b'
        )
        
        self.stdout.write(f'  ✅ TaskCalendar créé: {calendar.name}')
    
    
    
    def test_extensions_integration(self):
        """Test de l'intégration des extensions OneToOne"""
        self.stdout.write('\n🔗 Testing Extensions Integration...')
        
        # Vérifier que toutes les extensions sont liées
        base_task = self.base_task
        
        # Récupérer avec toutes les relations
        base_task_full = BaseTask.objects.select_related(
            'persistent_job',
            'metrics'
        ).get(id=base_task.id)
        
        self.stdout.write(f'  ✅ BaseTask: {base_task_full.task_id}')
        
        # Vérifier les extensions
        if hasattr(base_task_full, 'persistent_job'):
            self.stdout.write(f'  ✅ PersistentJob extension: {base_task_full.persistent_job.id}')
        
        if hasattr(base_task_full, 'metrics'):
            self.stdout.write(f'  ✅ TaskMetrics extension: {base_task_full.metrics.id}')
        
        # Test query optimisée (comme dans seo_keywords)
        all_tasks = BaseTask.objects.select_related(
            'brand', 'created_by', 'persistent_job', 'metrics'
        ).filter(brand=self.test_brand, task_type__startswith='test_')
        
        self.stdout.write(f'  ✅ Query optimisée: {all_tasks.count()} tasks trouvées')
        
        # Test filtres cross-app (simulation)
        tasks_with_metrics = BaseTask.objects.filter(
            metrics__execution_time_ms__gte=1000
        )
        
        tasks_resumable = BaseTask.objects.filter(
            persistent_job__can_resume=True
        )
        
        self.stdout.write(f'  ✅ Tasks avec métriques > 1s: {tasks_with_metrics.count()}')
        self.stdout.write(f'  ✅ Tasks resumables: {tasks_resumable.count()}')
    
    def cleanup_test_data(self):
        """Nettoie les données de test"""
        self.stdout.write('\n🧹 Cleanup des données de test...')
        
        # Les relations en cascade vont tout nettoyer
        BaseTask.objects.filter(task_type__startswith='test_').delete()
        CronJob.objects.filter(name__startswith='Test').delete()
        TaskCalendar.objects.filter(name__startswith='Test').delete()
        AlertRule.objects.filter(name__startswith='Test').delete()
        WorkerHealth.objects.filter(worker_name__startswith='test-').delete()
        
        # Nettoyer aussi les task_id vides si ils existent
        BaseTask.objects.filter(task_id='').delete()
        
        self.stdout.write('  ✅ Données de test supprimées')