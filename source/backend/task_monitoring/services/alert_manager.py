# backend/task_monitoring/services/alert_manager.py

from typing import Dict, List, Any
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import requests
import logging
from ..models import AlertRule, TaskMetrics

logger = logging.getLogger('task_monitoring')

class AlertManager:
    """Gestionnaire d'alertes pour le monitoring"""
    
    @staticmethod
    def check_alerts_for_task(base_task) -> List[Dict[str, Any]]:
        """Vérifie les alertes pour une tâche donnée"""
        
        triggered_alerts = []
        
        try:
            metrics = base_task.metrics
        except TaskMetrics.DoesNotExist:
            return triggered_alerts
        
        # Récupérer les règles actives pour cette brand
        active_rules = AlertRule.objects.filter(
            brand=base_task.brand,
            is_active=True
        )
        
        for rule in active_rules:
            # Vérifier si la règle s'applique à ce type de tâche
            if rule.task_types and base_task.task_type not in rule.task_types:
                continue
            
            # Vérifier le cooldown
            if rule.last_triggered_at:
                time_since_last = timezone.now() - rule.last_triggered_at
                if time_since_last.total_seconds() < (rule.cooldown_minutes * 60):
                    continue
            
            # Évaluer la condition
            if AlertManager._evaluate_condition(metrics, rule):
                triggered_alerts.append({
                    'rule': rule,
                    'task': base_task,
                    'metrics': metrics,
                    'triggered_at': timezone.now()
                })
                
                # Déclencher la notification
                AlertManager._trigger_alert(rule, base_task, metrics)
                
                # Mettre à jour le timestamp
                rule.last_triggered_at = timezone.now()
                rule.save(update_fields=['last_triggered_at'])
        
        return triggered_alerts
    
    @staticmethod
    def _evaluate_condition(metrics: TaskMetrics, rule: AlertRule) -> bool:
        """Évalue une condition d'alerte"""
        
        # Récupérer la valeur de la métrique
        metric_value = getattr(metrics, rule.metric_field, None)
        if metric_value is None:
            return False
        
        threshold = float(rule.threshold_value)
        
        # Évaluer selon la condition
        conditions = {
            'gt': lambda x, y: x > y,
            'gte': lambda x, y: x >= y,
            'lt': lambda x, y: x < y,
            'lte': lambda x, y: x <= y,
            'eq': lambda x, y: x == y,
        }
        
        condition_func = conditions.get(rule.condition)
        if not condition_func:
            return False
        
        return condition_func(float(metric_value), threshold)
    
    @staticmethod
    def _trigger_alert(rule: AlertRule, base_task, metrics: TaskMetrics):
        """Déclenche une alerte (email + webhook)"""
        
        alert_data = {
            'rule_name': rule.name,
            'task_id': base_task.task_id,
            'task_type': base_task.task_type,
            'metric_field': rule.metric_field,
            'metric_value': getattr(metrics, rule.metric_field),
            'threshold': float(rule.threshold_value),
            'brand': base_task.brand.name,
            'triggered_at': timezone.now().isoformat()
        }
        
        # Email notification
        if rule.notification_emails:
            try:
                AlertManager._send_email_alert(rule, alert_data)
            except Exception as e:
                logger.error(f"Failed to send email alert: {e}")
        
        # Webhook notification
        if rule.webhook_url:
            try:
                AlertManager._send_webhook_alert(rule, alert_data)
            except Exception as e:
                logger.error(f"Failed to send webhook alert: {e}")
    
    @staticmethod
    def _send_email_alert(rule: AlertRule, alert_data: Dict[str, Any]):
        """Envoie une alerte par email"""
        
        subject = f"🚨 MEGAHUB Alert: {rule.name}"
        
        message = f"""
        Alert triggered: {rule.name}
        
        Task Details:
        - Task ID: {alert_data['task_id']}
        - Task Type: {alert_data['task_type']}
        - Brand: {alert_data['brand']}
        
        Metric:
        - Field: {alert_data['metric_field']}
        - Value: {alert_data['metric_value']}
        - Threshold: {alert_data['threshold']}
        
        Time: {alert_data['triggered_at']}
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=rule.notification_emails,
            fail_silently=False
        )
    
    @staticmethod
    def _send_webhook_alert(rule: AlertRule, alert_data: Dict[str, Any]):
        """Envoie une alerte via webhook"""
        
        payload = {
            'alert_type': 'task_monitoring',
            'rule': {
                'id': rule.id,
                'name': rule.name,
                'description': rule.description
            },
            'alert_data': alert_data
        }
        
        response = requests.post(
            rule.webhook_url,
            json=payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        response.raise_for_status()
