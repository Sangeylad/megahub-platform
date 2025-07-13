# backend/task_scheduling/management/commands/test_api_endpoints.py

from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json
import uuid
from rest_framework_simplejwt.tokens import RefreshToken

from brands_core.models import Brand
from task_core.models import BaseTask

User = get_user_model()

class Command(BaseCommand):
    help = 'Test des endpoints API tasks'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌐 Testing Task API Endpoints\n'))
        
        # Setup client et auth
        self.setup_client()
        
        # Tests par app
        self.test_core_endpoints()
        self.test_scheduling_endpoints() 
        self.test_monitoring_endpoints()
        self.test_persistence_endpoints()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Tous les tests API sont passés !'))
    
    def setup_client(self):
        """Setup client de test avec JWT auth"""
        self.client = Client()
        self.user = User.objects.first()
        self.brand = Brand.objects.first()
        
        if not self.user or not self.brand:
            self.stdout.write(self.style.ERROR('❌ User ou Brand manquant'))
            return
        
        # Générer JWT token
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        # Configurer les headers avec JWT
        self.auth_headers = {
            'HTTP_AUTHORIZATION': f'Bearer {access_token}',
            'HTTP_X_BRAND_ID': str(self.brand.id),  # Header brand explicite
        }
        
        self.stdout.write(f'🔐 Auth: {self.user.username} @ {self.brand.name}')
        self.stdout.write(f'🎫 JWT Token: {access_token[:20]}...')
    
    def test_core_endpoints(self):
        """Test des endpoints task_core"""
        self.stdout.write('\n📋 Testing task_core endpoints...')
        
        # 1. Créer une BaseTask via API
        task_data = {
            'task_type': f'api_test_{uuid.uuid4().hex[:8]}',
            'priority': 'normal',
            'description': 'Test API creation',
            'context_data': {'api_test': True}
        }
        
        response = self.client.post(
            '/tasks/tasks/', 
            task_data, 
            content_type='application/json',
            **self.auth_headers
        )
        self.stdout.write(f'  POST /tasks/tasks/: {response.status_code}')
        
        if response.status_code == 201:
            task_data = response.json()
            task_id = task_data['id']
            self.stdout.write(f'    ✅ Task créée: {task_data.get("task_id")}')
            
            # 2. Récupérer la task
            response = self.client.get(f'/tasks/tasks/{task_id}/', **self.auth_headers)
            self.stdout.write(f'  GET /tasks/tasks/{task_id}/: {response.status_code}')
            
            # 3. Retry de la task
            response = self.client.post(f'/tasks/tasks/{task_id}/retry/', **self.auth_headers)
            self.stdout.write(f'  POST /tasks/tasks/{task_id}/retry/: {response.status_code}')
        else:
            self.stdout.write(f'    ❌ Erreur création: {response.content.decode()[:200]}')
        
        # 4. Lister les tasks
        response = self.client.get('/tasks/tasks/', **self.auth_headers)
        self.stdout.write(f'  GET /tasks/tasks/: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            count = data.get('count') if isinstance(data, dict) else len(data)
            self.stdout.write(f'    ✅ {count} tasks trouvées')
        
        # 5. Stats des queues
        response = self.client.get('/tasks/tasks/queue-stats/', **self.auth_headers)
        self.stdout.write(f'  GET /tasks/tasks/queue-stats/: {response.status_code}')
    
    def test_scheduling_endpoints(self):
        """Test des endpoints task_scheduling"""
        self.stdout.write('\n⏰ Testing task_scheduling endpoints...')
        
        # 1. Valider expression cron
        cron_data = {'cron_expression': '0 9 * * 1-5'}
        response = self.client.post(
            '/tasks/scheduled/periodic-tasks/validate-cron/', 
            cron_data, 
            content_type='application/json',
            **self.auth_headers
        )
        self.stdout.write(f'  POST validate-cron: {response.status_code}')
        if response.status_code == 200:
            self.stdout.write(f'    ✅ Validation: {response.json()}')
        
        # 2. Lister tâches prêtes
        response = self.client.get('/tasks/scheduled/periodic-tasks/ready-for-execution/', **self.auth_headers)
        self.stdout.write(f'  GET ready-for-execution: {response.status_code}')
        
        # 3. Lister PeriodicTasks
        response = self.client.get('/tasks/scheduled/periodic-tasks/', **self.auth_headers)
        self.stdout.write(f'  GET periodic-tasks: {response.status_code}')
        
        # 4. Lister CronJobs
        response = self.client.get('/tasks/scheduled/cron-jobs/', **self.auth_headers)
        self.stdout.write(f'  GET cron-jobs: {response.status_code}')
        
        # 5. Lister calendriers
        response = self.client.get('/tasks/scheduled/calendars/', **self.auth_headers)
        self.stdout.write(f'  GET calendars: {response.status_code}')
    
    def test_monitoring_endpoints(self):
        """Test des endpoints task_monitoring"""
        self.stdout.write('\n📊 Testing task_monitoring endpoints...')
        
        # 1. Dashboard monitoring
        response = self.client.get('/tasks/monitoring/metrics/dashboard/', **self.auth_headers)
        self.stdout.write(f'  GET dashboard: {response.status_code}')
        
        # 2. Tendances
        response = self.client.get('/tasks/monitoring/metrics/trends/?days=7', **self.auth_headers)
        self.stdout.write(f'  GET trends: {response.status_code}')
        
        # 3. Worker health overview
        response = self.client.get('/tasks/monitoring/workers/overview/', **self.auth_headers)
        self.stdout.write(f'  GET workers overview: {response.status_code}')
        
        # 4. Lister métriques
        response = self.client.get('/tasks/monitoring/metrics/', **self.auth_headers)
        self.stdout.write(f'  GET metrics: {response.status_code}')
        
        # 5. Lister alertes
        response = self.client.get('/tasks/monitoring/alerts/', **self.auth_headers)
        self.stdout.write(f'  GET alerts: {response.status_code}')
        
        # 6. Lister workers
        response = self.client.get('/tasks/monitoring/workers/', **self.auth_headers)
        self.stdout.write(f'  GET workers: {response.status_code}')
    
    def test_persistence_endpoints(self):
        """Test des endpoints task_persistence"""
        self.stdout.write('\n💾 Testing task_persistence endpoints...')
        
        # 1. Lister jobs resumables
        response = self.client.get('/tasks/persistent-jobs/persistent-jobs/resumable/', **self.auth_headers)
        self.stdout.write(f'  GET resumable: {response.status_code}')
        
        # 2. Lister tous les persistent jobs
        response = self.client.get('/tasks/persistent-jobs/persistent-jobs/', **self.auth_headers)
        self.stdout.write(f'  GET persistent-jobs: {response.status_code}')
        
        # 3. Lister checkpoints
        response = self.client.get('/tasks/persistent-jobs/checkpoints/', **self.auth_headers)
        self.stdout.write(f'  GET checkpoints: {response.status_code}')
        
        # 4. Cleanup
        cleanup_data = {'days_old': 30}
        response = self.client.post(
            '/tasks/persistent-jobs/persistent-jobs/cleanup-old/', 
            cleanup_data, 
            content_type='application/json',
            **self.auth_headers
        )
        self.stdout.write(f'  POST cleanup-old: {response.status_code}')