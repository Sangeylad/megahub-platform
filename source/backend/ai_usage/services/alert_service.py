# backend/ai_usage/services/alert_service.py

import logging
from decimal import Decimal
from typing import List, Dict, Any
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from ..models import AIUsageAlert, AIJobUsage
from ai_providers.models import AIQuota
from ai_providers.services import QuotaService

logger = logging.getLogger(__name__)

class AlertService:
   """Service gestion alertes usage IA"""
   
   @staticmethod
   def check_quota_alerts(company) -> List[AIUsageAlert]:
       """Vérifier et créer alertes quota"""
       alerts_created = []
       
       # Vérifier chaque provider
       for provider_name in ['openai', 'anthropic', 'google']:
           quota_status = QuotaService.get_quota_status(company, provider_name)
           
           if not quota_status.get('has_quota'):
               continue
           
           # Alert 80% tokens
           tokens_percentage = (quota_status['tokens_used'] / 
                              (quota_status['tokens_used'] + quota_status['tokens_remaining']))
           
           if tokens_percentage >= 0.8:
               alert = AlertService._create_alert_if_not_exists(
                   company=company,
                   provider_name=provider_name,
                   alert_type='quota_warning',
                   threshold_value=Decimal('0.8'),
                   current_value=Decimal(str(tokens_percentage)),
                   message=f"Quota tokens {provider_name} à {tokens_percentage:.1%}"
               )
               if alert:
                   alerts_created.append(alert)
           
           # Alert coût dépassé
           if quota_status.get('is_over_limit'):
               alert = AlertService._create_alert_if_not_exists(
                   company=company,
                   provider_name=provider_name,
                   alert_type='quota_exceeded',
                   threshold_value=Decimal(str(quota_status['cost_used'] + quota_status['cost_remaining'])),
                   current_value=Decimal(str(quota_status['cost_used'])),
                   message=f"Quota {provider_name} dépassé: ${quota_status['cost_used']:.2f}"
               )
               if alert:
                   alerts_created.append(alert)
       
       return alerts_created
   
   @staticmethod
   def check_failure_rate_alerts(company, days: int = 7) -> List[AIUsageAlert]:
       """Vérifier taux d'échec élevé"""
       alerts_created = []
       start_date = timezone.now() - timedelta(days=days)
       
       # Jobs récents par provider
       for provider_name in ['openai', 'anthropic', 'google']:
           recent_usage = AIJobUsage.objects.filter(
               ai_job__brand__company=company,
               provider_name=provider_name,
               created_at__gte=start_date
           )
           
           if recent_usage.count() < 10:  # Pas assez de données
               continue
           
           failed_jobs = recent_usage.filter(success_rate__lt=1.0).count()
           total_jobs = recent_usage.count()
           failure_rate = failed_jobs / total_jobs
           
           if failure_rate > 0.2:  # Plus de 20% d'échec
               alert = AlertService._create_alert_if_not_exists(
                   company=company,
                   provider_name=provider_name,
                   alert_type='high_failure_rate',
                   threshold_value=Decimal('0.2'),
                   current_value=Decimal(str(failure_rate)),
                   message=f"Taux d'échec élevé {provider_name}: {failure_rate:.1%} ({failed_jobs}/{total_jobs})"
               )
               if alert:
                   alerts_created.append(alert)
       
       return alerts_created
   
   @staticmethod
   def check_unusual_usage_alerts(company, days: int = 7) -> List[AIUsageAlert]:
       """Détecter usage inhabituel"""
       alerts_created = []
       
       # Usage récent vs moyenne
       end_date = timezone.now()
       recent_start = end_date - timedelta(days=days)
       baseline_start = recent_start - timedelta(days=days * 4)  # 4 semaines avant
       
       recent_usage = AIJobUsage.objects.filter(
           ai_job__brand__company=company,
           created_at__gte=recent_start
       ).aggregate(
           total_cost=Sum('total_cost'),
           total_tokens=Sum('total_tokens')
       )
       
       baseline_usage = AIJobUsage.objects.filter(
           ai_job__brand__company=company,
           created_at__gte=baseline_start,
           created_at__lt=recent_start
       ).aggregate(
           total_cost=Sum('total_cost'),
           total_tokens=Sum('total_tokens')
       )
       
       if (recent_usage['total_cost'] and baseline_usage['total_cost'] and
           recent_usage['total_cost'] > baseline_usage['total_cost'] * 3):
           
           alert = AlertService._create_alert_if_not_exists(
               company=company,
               provider_name='all',
               alert_type='unusual_usage',
               threshold_value=baseline_usage['total_cost'] * 3,
               current_value=recent_usage['total_cost'],
               message=f"Usage inhabituel détecté: coût x3 vs baseline (${recent_usage['total_cost']:.2f})"
           )
           if alert:
               alerts_created.append(alert)
       
       return alerts_created
   
   @staticmethod
   def _create_alert_if_not_exists(
       company,
       provider_name: str,
       alert_type: str,
       threshold_value: Decimal,
       current_value: Decimal,
       message: str
   ) -> AIUsageAlert:
       """Créer alerte si pas déjà existante"""
       
       # Vérifier si alerte similaire existe (dernières 24h)
       recent_alert = AIUsageAlert.objects.filter(
           company=company,
           provider_name=provider_name,
           alert_type=alert_type,
           is_resolved=False,
           created_at__gte=timezone.now() - timedelta(hours=24)
       ).first()
       
       if recent_alert:
           return None  # Pas de spam d'alertes
       
       alert = AIUsageAlert.objects.create(
           company=company,
           provider_name=provider_name,
           alert_type=alert_type,
           threshold_value=threshold_value,
           current_value=current_value,
           message=message
       )
       
       logger.warning(f"Alerte créée: {company.name} - {alert_type} - {message}")
       return alert
   
   @staticmethod
   def resolve_alert(alert_id: int, resolved_by=None) -> bool:
       """Résoudre une alerte"""
       try:
           alert = AIUsageAlert.objects.get(id=alert_id)
           alert.is_resolved = True
           alert.resolved_at = timezone.now()
           alert.save()
           
           logger.info(f"Alerte résolue: {alert_id}")
           return True
       except AIUsageAlert.DoesNotExist:
           return False
