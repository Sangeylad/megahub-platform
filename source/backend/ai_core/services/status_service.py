# backend/ai_core/services/status_service.py

import logging
from typing import Dict, Any, List
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from ..models import AIJob, AIJobStatus

logger = logging.getLogger(__name__)

class StatusService:
    """Service pour monitoring et stats jobs IA"""
    
    @staticmethod
    def get_dashboard_stats(brand=None) -> Dict[str, Any]:
        """Stats pour dashboard"""
        queryset = AIJob.objects.all()
        if brand:
            queryset = queryset.filter(brand=brand)
        
        # Stats par statut
        status_stats = queryset.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status=AIJobStatus.PENDING)),
            running=Count('id', filter=Q(status=AIJobStatus.RUNNING)),
            completed=Count('id', filter=Q(status=AIJobStatus.COMPLETED)),
            failed=Count('id', filter=Q(status=AIJobStatus.FAILED))
        )
        
        # Jobs récents
        recent_jobs = queryset.select_related(
            'job_type', 'created_by'
        ).order_by('-created_at')[:10]
        
        return {
            'stats': status_stats,
            'recent_jobs': [
                {
                    'job_id': job.job_id,
                    'type': job.job_type.name,
                    'status': job.status,
                    'progress': job.progress_percentage,
                    'created_at': job.created_at,
                    'created_by': job.created_by.username
                }
                for job in recent_jobs
            ],
            'generated_at': timezone.now()
        }
    
    @staticmethod
    def get_jobs_by_status(status: str, brand=None) -> List[Dict[str, Any]]:
        """Jobs par statut"""
        queryset = AIJob.objects.filter(status=status)
        if brand:
            queryset = queryset.filter(brand=brand)
        
        return queryset.select_related('job_type', 'created_by').values(
            'job_id', 'job_type__name', 'status', 'progress_percentage',
            'created_at', 'created_by__username', 'description'
        )
