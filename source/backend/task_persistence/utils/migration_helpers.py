# backend/task_persistence/utils/migration_helpers.py

from typing import Dict, Any, List
from django.db import transaction
from ..services import PersistenceService

class ContentGenerationMigrator:
    """Utilitaires pour migrer ContentGenerationJob vers PersistentJob"""
    
    @staticmethod
    def migrate_content_generation_job(legacy_job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migre un ContentGenerationJob legacy vers PersistentJob
        
        Format legacy attendu:
        {
            'website_id': int,
            'target_pages': List[int],
            'pages_status': Dict[str, str],
            'custom_instructions': str,
            'brand_id': int,
            'created_by_id': int
        }
        """
        
        # Calculer les étapes
        target_pages = legacy_job_data.get('target_pages', [])
        total_steps = len(target_pages)
        pages_status = legacy_job_data.get('pages_status', {})
        
        # Compter les étapes complétées
        completed_steps = sum(
            1 for status in pages_status.values() 
            if status in ['completed', 'success']
        )
        
        # Préparer job_data pour PersistentJob
        job_data = {
            'website_id': legacy_job_data.get('website_id'),
            'target_pages': target_pages,
            'custom_instructions': legacy_job_data.get('custom_instructions', ''),
            'content_type': 'ai_generated',
            'generation_config': {
                'model': 'gpt-4-turbo',
                'temperature': 0.7
            }
        }
        
        return {
            'task_type': 'content_generation_v3',
            'brand_id': legacy_job_data['brand_id'],
            'created_by_id': legacy_job_data['created_by_id'],
            'job_data': job_data,
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'pages_status': pages_status,
            'description': f'Migration: Content generation for {len(target_pages)} pages'
        }
    
    @staticmethod
    @transaction.atomic
    def create_from_legacy(legacy_job_data: Dict[str, Any]):
        """Crée un PersistentJob à partir de données legacy"""
        
        migration_data = ContentGenerationMigrator.migrate_content_generation_job(
            legacy_job_data
        )
        
        # Créer le PersistentJob
        persistent_job = PersistenceService.create_persistent_job(
            task_type=migration_data['task_type'],
            brand_id=migration_data['brand_id'],
            created_by_id=migration_data['created_by_id'],
            job_data=migration_data['job_data'],
            total_steps=migration_data['total_steps'],
            description=migration_data['description']
        )
        
        # Mettre à jour le progrès
        if migration_data['completed_steps'] > 0:
            PersistenceService.update_progress(
                persistent_job=persistent_job,
                completed_steps=migration_data['completed_steps'],
                current_step='in_progress'
            )
        
        # Sauvegarder l'état des pages
        persistent_job.job_state.pages_status = migration_data['pages_status']
        persistent_job.job_state.save(update_fields=['pages_status'])
        
        return persistent_job
