# backend/ai_core/management/commands/setup_ai_job_types.py

from django.core.management.base import BaseCommand
from ai_core.models import AIJobType
from ai_providers.models import AIProvider

class Command(BaseCommand):
    help = 'Initialise les job types IA de base pour test infrastructure'
    
    def handle(self, *args, **options):
        self.stdout.write('🧠 Setup job types IA (infrastructure test)...')
        
        # ✅ Job types de base - vrais wording prod
        job_types = [
            {
                'name': 'chat_completion',
                'description': 'Conversation interactive avec l\'IA',
                'category': 'chat',
                'estimated_duration_seconds': 10,
                'requires_async': False
            },
            {
                'name': 'text_generation',
                'description': 'Génération de texte sur mesure',
                'category': 'generation',
                'estimated_duration_seconds': 30,
                'requires_async': False
            },
            {
                'name': 'content_analysis',
                'description': 'Analyse de contenu existant',
                'category': 'analysis',
                'estimated_duration_seconds': 45,
                'requires_async': True
            }
        ]
        
        for job_data in job_types:
            job_type, created = AIJobType.objects.get_or_create(
                name=job_data['name'],
                defaults=job_data
            )
            status = "✅ Créé" if created else "⚠️  Existe"
            self.stdout.write(f'  {status}: {job_type.name} ({job_type.category})')
        
        # Provider OpenAI minimal
        try:
            openai_provider, created = AIProvider.objects.get_or_create(
                name='openai',
                defaults={
                    'display_name': 'OpenAI',
                    'api_base_url': 'https://api.openai.com/v1',
                    'is_active': True,
                    'supported_models': ['gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo']
                }
            )
            status = "✅ Créé" if created else "⚠️  Existe"
            self.stdout.write(f'  {status}: Provider OpenAI')
        except Exception as e:
            self.stdout.write(f'  ❌ Erreur provider: {e}')
        
        self.stdout.write(self.style.SUCCESS('✅ Infrastructure IA prête !'))