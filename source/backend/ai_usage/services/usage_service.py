# backend/ai_usage/services/usage_service.py

import logging
from decimal import Decimal
from typing import Dict, Any, Optional
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta, date

from ..models import AIJobUsage
from ai_core.models import AIJob

logger = logging.getLogger(__name__)

class UsageService:
   """Service tracking usage et métriques IA"""
   
   @staticmethod
   def record_usage(
       ai_job: AIJob,
       input_tokens: int = 0,
       output_tokens: int = 0,
       cost_input: Decimal = Decimal('0'),
       cost_output: Decimal = Decimal('0'),
       execution_time_seconds: int = 0,
       provider_name: str = 'openai',
       model_name: str = 'gpt-4o',
       memory_usage_mb: int = 0
   ) -> AIJobUsage:
       """Enregistrer usage d'un job"""
       
       total_tokens = input_tokens + output_tokens
       total_cost = cost_input + cost_output
       
       usage, created = AIJobUsage.objects.get_or_create(
           ai_job=ai_job,
           defaults={
               'input_tokens': input_tokens,
               'output_tokens': output_tokens,
               'total_tokens': total_tokens,
               'cost_input': cost_input,
               'cost_output': cost_output,
               'total_cost': total_cost,
               'execution_time_seconds': execution_time_seconds,
               'provider_name': provider_name,
               'model_name': model_name,
               'memory_usage_mb': memory_usage_mb
           }
       )
       
       if not created:
           # Mise à jour si existe déjà
           usage.input_tokens = input_tokens
           usage.output_tokens = output_tokens
           usage.total_tokens = total_tokens
           usage.cost_input = cost_input
           usage.cost_output = cost_output
           usage.total_cost = total_cost
           usage.execution_time_seconds = execution_time_seconds
           usage.memory_usage_mb = memory_usage_mb
           usage.save()
       
       logger.info(f"Usage enregistré: {ai_job.job_id} - {total_tokens} tokens, ${total_cost}")
       return usage
   
   @staticmethod
   def get_usage_dashboard(brand=None, days: int = 30) -> Dict[str, Any]:
        """Dashboard usage pour une brand"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Base queryset
        queryset = AIJobUsage.objects.filter(
            created_at__gte=start_date
        ).select_related('ai_job')
        
        if brand:
            queryset = queryset.filter(ai_job__brand=brand)
        
        # ✅ FIX : Agrégations sans conflit
        totals = queryset.aggregate(
            total_jobs=Count('id'),
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('total_cost'),
            avg_execution_time=Avg('execution_time_seconds')
            # ❌ SUPPRIMÉ : avg_tokens_per_job=Avg('total_tokens')
        )
        
        # ✅ CALCUL MANUEL de la moyenne
        avg_tokens_per_job = 0
        if totals['total_jobs'] and totals['total_tokens']:
            avg_tokens_per_job = totals['total_tokens'] / totals['total_jobs']
        
        # Par provider
        by_provider = list(queryset.values('provider_name').annotate(
            jobs_count=Count('id'),
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('total_cost')
        ).order_by('-total_cost'))
        
        # Par modèle
        by_model = list(queryset.values('model_name').annotate(
            jobs_count=Count('id'),
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('total_cost')
        ).order_by('-jobs_count'))
        
        # Usage quotidien (7 derniers jours)
        daily_usage = []
        for i in range(7):
            day = end_date - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            day_stats = queryset.filter(
                created_at__gte=day_start,
                created_at__lt=day_end
            ).aggregate(
                jobs=Count('id'),
                tokens=Sum('total_tokens'),
                cost=Sum('total_cost')
            )
            
            daily_usage.append({
                'date': day.date().isoformat(),
                'jobs': day_stats['jobs'] or 0,
                'tokens': day_stats['tokens'] or 0,
                'cost': float(day_stats['cost'] or 0)
            })
        
        return {
            'period': f"{start_date.date()} to {end_date.date()}",
            'totals': {
                'jobs': totals['total_jobs'] or 0,
                'tokens': totals['total_tokens'] or 0,
                'cost': float(totals['total_cost'] or 0),
                'avg_execution_time': totals['avg_execution_time'] or 0,
                'avg_tokens_per_job': avg_tokens_per_job  # ✅ Calcul manuel
            },
            'by_provider': by_provider,
            'by_model': by_model,
            'daily_usage': list(reversed(daily_usage)),
            'generated_at': timezone.now()
        }
   
   
   @staticmethod
   def get_cost_breakdown(brand=None, month: Optional[date] = None) -> Dict[str, Any]:
    """Répartition coûts par mois"""
    if not month:
        month = date.today().replace(day=1)
    
    start_date = timezone.datetime.combine(month, timezone.datetime.min.time())
    start_date = timezone.make_aware(start_date)
    
    # Fin du mois
    if month.month == 12:
        end_month = month.replace(year=month.year + 1, month=1)
    else:
        end_month = month.replace(month=month.month + 1)
    end_date = timezone.datetime.combine(end_month, timezone.datetime.min.time())
    end_date = timezone.make_aware(end_date)
    
    queryset = AIJobUsage.objects.filter(
        created_at__gte=start_date,
        created_at__lt=end_date
    )
    
    if brand:
        queryset = queryset.filter(ai_job__brand=brand)
    
    # ✅ FIX : Coûts par type de job SANS Avg
    by_job_type = list(queryset.values('ai_job__job_type__name').annotate(
        total_cost=Sum('total_cost'),
        jobs_count=Count('id')
        # ❌ SUPPRIMÉ : avg_cost=Avg('total_cost')
    ).order_by('-total_cost'))
    
    # ✅ CALCUL MANUEL de avg_cost pour chaque type
    for item in by_job_type:
        if item['jobs_count'] > 0:
            item['avg_cost'] = float(item['total_cost']) / item['jobs_count']
        else:
            item['avg_cost'] = 0.0
    
    # Coûts par utilisateur (top 10)
    by_user = list(queryset.values(
        'ai_job__created_by__username'
    ).annotate(
        total_cost=Sum('total_cost'),
        jobs_count=Count('id')
    ).order_by('-total_cost')[:10])
    
    total_cost = queryset.aggregate(
        total=Sum('total_cost')
    )['total'] or Decimal('0')
    
    return {
        'month': month.isoformat(),
        'total_cost': float(total_cost),
        'by_job_type': by_job_type,
        'by_user': by_user
    }

