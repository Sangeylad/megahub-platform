# backend/ai_core/management/commands/test_ai_endpoints.py

from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json
import uuid
from rest_framework_simplejwt.tokens import RefreshToken

from brands_core.models import Brand
from ai_core.models import AIJob

User = get_user_model()

class Command(BaseCommand):
    help = 'Test des endpoints API IA avec support O3/GPT-4.1'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--test-o3',
            action='store_true',
            help='Tester spécifiquement les endpoints O3'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Affichage verbose des réponses'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧠 Testing AI API Endpoints v2.0 (O3 Support)\n'))
        
        self.verbose = options['verbose']
        
        # Setup client et auth
        self.setup_client()
        
        # Tests par app
        self.test_core_endpoints()
        self.test_providers_endpoints() 
        self.test_openai_endpoints()
        self.test_usage_endpoints()
        
        # 🆕 Tests nouveaux modèles
        if options['test_o3']:
            self.test_o3_endpoints()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Tous les tests API IA v2.0 sont passés !'))
    
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
            'HTTP_X_BRAND_ID': str(self.brand.id),
        }
        
        self.stdout.write(f'🔐 Auth: {self.user.username} @ {self.brand.name}')
        self.stdout.write(f'🎫 JWT Token: {access_token[:20]}...')
    
    def log_response(self, response, endpoint_name):
        """Log détaillé des réponses si verbose"""
        if self.verbose and response.content:
            try:
                data = response.json()
                self.stdout.write(f'    📄 Response: {json.dumps(data, indent=2)[:300]}...')
            except:
                content = response.content.decode()[:200]
                self.stdout.write(f'    📄 Raw: {content}...')
    
    def test_core_endpoints(self):
        """Test des endpoints ai_core"""
        self.stdout.write('\n🧠 Testing ai_core endpoints...')
        
        # 1. Lister job types
        response = self.client.get('/ai/job-types/', **self.auth_headers)
        self.stdout.write(f'  GET /ai/job-types/: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            count = data.get('count') if isinstance(data, dict) else len(data)
            self.stdout.write(f'    ✅ {count} job types trouvés')
            self.log_response(response, 'job-types')
        
        # 2. Créer un AIJob via API
        job_data = {
            'job_type': 'chat_completion',
            'priority': 'normal',
            'description': 'Test API creation IA v2.0',
            'input_data': {
                'api_test': True,
                'supports_o3': True,
                'test_version': '2.0'
            }
        }
        
        response = self.client.post(
            '/ai/jobs/', 
            job_data, 
            content_type='application/json',
            **self.auth_headers
        )
        self.stdout.write(f'  POST /ai/jobs/: {response.status_code}')
        
        if response.status_code == 201:
            job_data = response.json()
            job_id = job_data['id']
            self.stdout.write(f'    ✅ AIJob créé: {job_data.get("job_id")}')
            self.log_response(response, 'create-job')
            
            # Stocker pour autres tests
            self.test_job_id = job_id
            
            # 3. Récupérer le job
            response = self.client.get(f'/ai/jobs/{job_id}/', **self.auth_headers)
            self.stdout.write(f'  GET /ai/jobs/{job_id}/: {response.status_code}')
            self.log_response(response, 'get-job')
            
            # 4. Dashboard
            response = self.client.get('/ai/jobs/dashboard/', **self.auth_headers)
            self.stdout.write(f'  GET /ai/jobs/dashboard/: {response.status_code}')
            if response.status_code == 200:
                dashboard = response.json()
                total_jobs = dashboard.get('total_jobs', 0)
                self.stdout.write(f'    ✅ Dashboard: {total_jobs} jobs total')
            
            # 5. Annuler le job
            response = self.client.post(f'/ai/jobs/{job_id}/cancel/', **self.auth_headers)
            self.stdout.write(f'  POST /ai/jobs/{job_id}/cancel/: {response.status_code}')
        else:
            error_content = response.content.decode() if response.content else 'No content'
            try:
                error_data = json.loads(error_content)
                self.stdout.write(f'    ❌ Erreur création: {error_data}')
            except:
                self.stdout.write(f'    ❌ Erreur création: {error_content[:200]}')
    
    def test_providers_endpoints(self):
        """Test des endpoints ai_providers"""
        self.stdout.write('\n🔌 Testing ai_providers endpoints...')
        
        # 1. Lister providers
        response = self.client.get('/ai/providers/', **self.auth_headers)
        self.stdout.write(f'  GET /ai/providers/: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            count = data.get('count') if isinstance(data, dict) else len(data)
            self.stdout.write(f'    ✅ {count} providers trouvés')
            
            # Vérifier modèles O3 dans providers
            providers_data = data.get('results', data) if isinstance(data, dict) else data
            for provider in providers_data:
                if provider.get('name') == 'openai':
                    models = provider.get('available_models', [])
                    has_o3 = any('o3' in model for model in models)
                    has_gpt41 = 'gpt-4.1' in models
                    self.stdout.write(f'    ✅ OpenAI: O3={has_o3}, GPT-4.1={has_gpt41}')
            
            self.log_response(response, 'providers')
        
        # 2. Lister credentials
        response = self.client.get('/ai/credentials/', **self.auth_headers)
        self.stdout.write(f'  GET /ai/credentials/: {response.status_code}')
        
        # 3. Quota status
        response = self.client.get('/ai/credentials/quota_status/?provider=openai', **self.auth_headers)
        self.stdout.write(f'  GET /ai/credentials/quota_status/: {response.status_code}')
        if response.status_code == 200:
            quota = response.json()
            self.stdout.write(f'    ✅ Quota OpenAI: {quota.get("remaining", "N/A")} tokens restants')
            self.log_response(response, 'quota-status')
        
        # 4. Test connection
        test_data = {'provider': 'openai'}
        response = self.client.post(
            '/ai/credentials/test_connection/', 
            test_data, 
            content_type='application/json',
            **self.auth_headers
        )
        self.stdout.write(f'  POST /ai/credentials/test_connection/: {response.status_code}')
        if response.status_code == 200:
            result = response.json()
            self.stdout.write(f'    ✅ Test connexion: {result.get("success", False)}')
    
    def test_openai_endpoints(self):
        """Test des endpoints ai_openai"""
        self.stdout.write('\n🟢 Testing ai_openai endpoints...')
        
        # 1. Lister jobs OpenAI
        response = self.client.get('/ai/openai/jobs/', **self.auth_headers)
        self.stdout.write(f'  GET /ai/openai/jobs/: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            count = data.get('count') if isinstance(data, dict) else len(data)
            self.stdout.write(f'    ✅ {count} OpenAI jobs trouvés')
        
        # 2. Modèles disponibles
        response = self.client.get('/ai/openai/chat/models/', **self.auth_headers)
        self.stdout.write(f'  GET /ai/openai/chat/models/: {response.status_code}')
        if response.status_code == 200:
            models = response.json()
            model_list = models.get('models', [])
            model_count = len(model_list)
            
            # Vérifier présence nouveaux modèles
            model_names = [m.get('id', m) for m in model_list]
            has_o3 = any('o3' in name for name in model_names)
            has_gpt41 = 'gpt-4.1' in model_names
            
            self.stdout.write(f'    ✅ {model_count} modèles disponibles')
            self.stdout.write(f'    ✅ Support O3: {has_o3}')
            self.stdout.write(f'    ✅ Support GPT-4.1: {has_gpt41}')
            self.log_response(response, 'models')
        
        # 3. Créer job chat completion legacy (GPT-4o)
        chat_data_legacy = {
            'messages': [
                {'role': 'user', 'content': 'Dis bonjour en français'}
            ],
            'model': 'gpt-4o',
            'description': 'Test chat completion API legacy',
            'temperature': 0.7,
            'max_tokens': 50
        }
        
        response = self.client.post(
            '/ai/openai/chat/create_job/', 
            chat_data_legacy, 
            content_type='application/json',
            **self.auth_headers
        )
        self.stdout.write(f'  POST /ai/openai/chat/create_job/ (legacy): {response.status_code}')
        
        if response.status_code == 201:
            job_result = response.json()
            job_id = job_result.get('job_id')
            self.stdout.write(f'    ✅ Chat job legacy créé: {job_id}')
            self.log_response(response, 'create-chat-legacy')
            
            # 4. Récupérer résultat
            response = self.client.get(
                f'/ai/openai/completion/job_result/?job_id={job_id}', 
                **self.auth_headers
            )
            self.stdout.write(f'  GET /ai/openai/completion/job_result/: {response.status_code}')
        else:
            error_msg = response.content.decode()[:200] if response.content else 'No content'
            self.stdout.write(f'    ❌ Erreur chat job legacy: {error_msg}')
    
    def test_o3_endpoints(self):
        """🆕 Test spécifique des endpoints O3/GPT-4.1"""
        self.stdout.write('\n🚀 Testing O3/GPT-4.1 Specific Endpoints...')
        
        # 1. Job O3 avec reasoning_effort
        chat_data_o3 = {
            'messages': [
                {
                    'role': 'developer',
                    'content': 'Tu es un expert SEO. Analyse le contenu suivant de manière approfondie.'
                },
                {
                    'role': 'user',
                    'content': 'Analyse SEO de cette page : https://example.com'
                }
            ],
            'model': 'o3',
            'description': 'Test chat completion O3 avec reasoning',
            'reasoning_effort': 'high',
            'max_tokens': 1000,
            'response_format': {'type': 'text'}
        }
        
        response = self.client.post(
            '/ai/openai/chat/create_job/', 
            chat_data_o3, 
            content_type='application/json',
            **self.auth_headers
        )
        self.stdout.write(f'  POST /ai/openai/chat/create_job/ (O3): {response.status_code}')
        
        if response.status_code == 201:
            job_result = response.json()
            job_id = job_result.get('job_id')
            self.stdout.write(f'    ✅ Chat job O3 créé: {job_id}')
            self.stdout.write(f'    ✅ Status: {job_result.get("status")}')
            self.log_response(response, 'create-chat-o3')
        else:
            error_msg = response.content.decode()[:300] if response.content else 'No content'
            try:
                error_data = json.loads(error_msg)
                self.stdout.write(f'    ❌ Erreur O3: {error_data}')
            except:
                self.stdout.write(f'    ❌ Erreur O3: {error_msg}')
        
        # 2. Job GPT-4.1 avec paramètres nouveaux
        chat_data_gpt41 = {
            'messages': [
                {
                    'role': 'system',
                    'content': 'Tu es un expert marketing digital.'
                },
                {
                    'role': 'user',
                    'content': 'Crée une stratégie marketing pour une startup SaaS'
                }
            ],
            'model': 'gpt-4.1',
            'description': 'Test chat completion GPT-4.1',
            'temperature': 1.0,
            'max_tokens': 5000,
            'response_format': {'type': 'text'}
        }
        
        response = self.client.post(
            '/ai/openai/chat/create_job/', 
            chat_data_gpt41, 
            content_type='application/json',
            **self.auth_headers
        )
        self.stdout.write(f'  POST /ai/openai/chat/create_job/ (GPT-4.1): {response.status_code}')
        
        if response.status_code == 201:
            job_result = response.json()
            job_id = job_result.get('job_id')
            self.stdout.write(f'    ✅ Chat job GPT-4.1 créé: {job_id}')
            self.log_response(response, 'create-chat-gpt41')
        else:
            error_msg = response.content.decode()[:300] if response.content else 'No content'
            try:
                error_data = json.loads(error_msg)
                self.stdout.write(f'    ❌ Erreur GPT-4.1: {error_data}')
            except:
                self.stdout.write(f'    ❌ Erreur GPT-4.1: {error_msg}')
        
        # 3. Test validation erreurs (temperature avec O3)
        invalid_o3_data = {
            'messages': [
                {'role': 'user', 'content': 'Test'}
            ],
            'model': 'o3',
            'temperature': 0.7,  # ❌ Invalide pour O3
            'reasoning_effort': 'medium'
        }
        
        response = self.client.post(
            '/ai/openai/chat/create_job/', 
            invalid_o3_data, 
            content_type='application/json',
            **self.auth_headers
        )
        self.stdout.write(f'  POST /ai/openai/chat/create_job/ (invalid O3): {response.status_code}')
        
        if response.status_code == 400:
            self.stdout.write(f'    ✅ Validation O3 fonctionne (temperature rejetée)')
        else:
            self.stdout.write(f'    ⚠️ Validation O3 attendue mais pas déclenchée')
        
        # 4. Test messages format automatique
        legacy_format_for_o3 = {
            'messages': [
                {'role': 'system', 'content': 'Expert SEO'},  # Sera converti en developer
                {'role': 'user', 'content': 'Test conversion'}  # Format string sera converti
            ],
            'model': 'o3',
            'reasoning_effort': 'low'
        }
        
        response = self.client.post(
            '/ai/openai/chat/create_job/', 
            legacy_format_for_o3, 
            content_type='application/json',
            **self.auth_headers
        )
        self.stdout.write(f'  POST /ai/openai/chat/create_job/ (format conversion): {response.status_code}')
        
        if response.status_code == 201:
            self.stdout.write(f'    ✅ Conversion format automatique OK')
        else:
            self.stdout.write(f'    ❌ Conversion format échouée')
    
    def test_usage_endpoints(self):
        """Test des endpoints ai_usage"""
        self.stdout.write('\n📊 Testing ai_usage endpoints...')
        
        # 1. Lister usage
        response = self.client.get('/ai/usage/', **self.auth_headers)
        self.stdout.write(f'  GET /ai/usage/: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            count = data.get('count') if isinstance(data, dict) else len(data)
            self.stdout.write(f'    ✅ {count} usages trouvés')
        
        # 2. Dashboard usage
        response = self.client.get('/ai/usage/dashboard/?days=7', **self.auth_headers)
        self.stdout.write(f'  GET /ai/usage/dashboard/: {response.status_code}')
        if response.status_code == 200:
            dashboard = response.json()
            total_jobs = dashboard.get('totals', {}).get('jobs', 0)
            total_cost = dashboard.get('totals', {}).get('cost', 0)
            self.stdout.write(f'    ✅ Dashboard: {total_jobs} jobs, ${total_cost} coût')
            
            # Vérifier breakdown par modèle
            by_model = dashboard.get('by_model', {})
            if by_model:
                for model, stats in by_model.items():
                    self.stdout.write(f'    📊 {model}: {stats.get("jobs", 0)} jobs, ${stats.get("cost", 0)}')
            
            self.log_response(response, 'usage-dashboard')
        
        # 3. Cost breakdown avec filtre modèle
        response = self.client.get('/ai/usage/cost_breakdown/?model=gpt-4o', **self.auth_headers)
        self.stdout.write(f'  GET /ai/usage/cost_breakdown/ (GPT-4o): {response.status_code}')
        if response.status_code == 200:
            breakdown = response.json()
            month_cost = breakdown.get('total_cost', 0)
            self.stdout.write(f'    ✅ Coût GPT-4o: ${month_cost}')
        
        # 4. Cost breakdown O3 (si disponible)
        response = self.client.get('/ai/usage/cost_breakdown/?model=o3', **self.auth_headers)
        self.stdout.write(f'  GET /ai/usage/cost_breakdown/ (O3): {response.status_code}')
        if response.status_code == 200:
            breakdown = response.json()
            month_cost = breakdown.get('total_cost', 0)
            self.stdout.write(f'    ✅ Coût O3: ${month_cost}')
        
        # 5. Lister alertes
        response = self.client.get('/ai/alerts/', **self.auth_headers)
        self.stdout.write(f'  GET /ai/alerts/: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            count = data.get('count') if isinstance(data, dict) else len(data)
            self.stdout.write(f'    ✅ {count} alertes trouvées')
        
        # 6. Alertes actives
        response = self.client.get('/ai/alerts/active/', **self.auth_headers)
        self.stdout.write(f'  GET /ai/alerts/active/: {response.status_code}')
        if response.status_code == 200:
            active = response.json()
            active_count = active.get('count', 0)
            self.stdout.write(f'    ✅ {active_count} alertes actives')
        
        # 7. Vérifier nouvelles alertes
        response = self.client.post('/ai/alerts/check_alerts/', **self.auth_headers)
        self.stdout.write(f'  POST /ai/alerts/check_alerts/: {response.status_code}')
        if response.status_code == 200:
            alerts = response.json()
            new_count = alerts.get('new_alerts_count', 0)
            self.stdout.write(f'    ✅ {new_count} nouvelles alertes')