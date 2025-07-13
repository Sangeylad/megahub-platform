# 📊 AI Usage - Usage, Métriques & Alertes

## Vue d'Ensemble

L'app `ai_usage` fournit un **tracking complet** de l'utilisation IA, des **métriques de performance** et un **système d'alertes** pour surveiller les coûts, quotas et qualité. Elle centralise toutes les données d'usage cross-providers avec analytics avancés.

### Responsabilité
- **AIJobUsage** : Métriques détaillées par job IA
- **Usage Analytics** : Dashboards et breakdowns
- **Cost Tracking** : Suivi précis des coûts par provider/modèle
- **Alert System** : Alertes automatiques quota/budget/qualité
- **Performance Monitoring** : Métriques d'exécution et succès

### Base URL
```
https://backoffice.humari.fr/ai/usage/
https://backoffice.humari.fr/ai/alerts/
```

---

## 📊 Modèles de Données

### AIJobUsage
```python
# Tracking usage détaillé par job IA
- ai_job: OneToOne → AIJob (relation centrale)

# Métriques tokens
- input_tokens: int # Tokens d'entrée
- output_tokens: int # Tokens de sortie  
- total_tokens: int # Total tokens

# Métriques coût (précision 6 décimales)
- cost_input: Decimal # Coût tokens input
- cost_output: Decimal # Coût tokens output
- total_cost: Decimal # Coût total

# Métriques performance
- execution_time_seconds: int # Temps d'exécution
- memory_usage_mb: int # Mémoire utilisée

# Provider context
- provider_name: str # "openai", "anthropic", etc.
- model_name: str # "gpt-4o", "claude-3-5-sonnet"

# Métriques qualité
- success_rate: float # 0.0-1.0, taux de succès
- error_count: int # Nombre d'erreurs
```

### AIUsageAlert
```python
# Système d'alertes usage
- company: FK → Company
- provider_name: str # Provider concerné

# Type d'alerte
- alert_type: str # quota_warning, quota_exceeded, cost_warning, high_failure_rate, unusual_usage
- threshold_value: Decimal # Seuil de déclenchement
- current_value: Decimal # Valeur actuelle

# Contenu
- message: str # Message d'alerte
- is_resolved: bool # Alerte résolue
- resolved_at: datetime # Date résolution

# Notification
- email_sent: bool # Email envoyé
- email_sent_at: datetime # Date envoi email
```

**Contraintes** :
- Index optimisé : `['provider_name', 'created_at']`
- Index jobs : `['ai_job', 'created_at']`

---

## 🎯 Endpoints Usage

### Usage Tracking

#### `GET /ai/usage/`
**Liste des usage avec filtres avancés**

**Filtres disponibles** :
```http
?provider_name=openai              # Par provider
?model_name=gpt-4o                # Par modèle
?total_cost__gte=1.00             # Coût minimum
?execution_time_seconds__gte=60   # Durée minimum
?success_rate__lt=1.0             # Jobs avec erreurs
?created_at__gte=2024-12-01       # Depuis date
?ai_job__brand=9                  # Par brand
?ai_job__status=completed         # Par statut job
```

**Réponse paginée** :
```json
{
  "count": 1247,
  "next": "?page=2",
  "results": [
    {
      "id": 89,
      "ai_job": {
        "id": 123,
        "job_id": "ai_job_abc123",
        "job_type": "chat_completion",
        "status": "completed",
        "brand": {"id": 9, "name": "Humari"}
      },
      "input_tokens": 125,
      "output_tokens": 275,
      "total_tokens": 400,
      "cost_input": "0.000625",
      "cost_output": "0.004125", 
      "total_cost": "0.004750",
      "execution_time_seconds": 3,
      "memory_usage_mb": 64,
      "provider_name": "openai",
      "model_name": "gpt-4o",
      "success_rate": 1.0,
      "error_count": 0,
      "created_at": "2024-12-20T14:35:00Z",
      "cost_per_token": 0.000011875
    }
  ]
}
```

#### `GET /ai/usage/{id}/`
**Détail usage avec job complet**

### Dashboard Usage

#### `GET /ai/usage/dashboard/`
**Dashboard principal d'usage**

**Paramètres** :
- `?days=7` (défaut 30) : Période d'analyse
- `?provider=openai` : Filtrer par provider

**Réponse complète** :
```json
{
  "period": {
    "days": 7,
    "start_date": "2024-12-13",
    "end_date": "2024-12-20"
  },
  "totals": {
    "jobs": 156,
    "tokens": 45670,
    "cost": "67.89",
    "avg_cost_per_job": "0.435",
    "avg_execution_time": 4.2
  },
  "by_provider": [
    {
      "provider": "openai",
      "jobs": 134,
      "tokens": 39870,
      "cost": "59.12",
      "percentage": 87.1,
      "avg_cost": "0.441"
    },
    {
      "provider": "anthropic", 
      "jobs": 22,
      "tokens": 5800,
      "cost": "8.77",
      "percentage": 12.9,
      "avg_cost": "0.399"
    }
  ],
  "by_model": [
    {
      "model": "gpt-4o",
      "provider": "openai",
      "jobs": 89,
      "cost": "45.67",
      "avg_tokens": 387
    },
    {
      "model": "gpt-4-turbo",
      "provider": "openai", 
      "jobs": 45,
      "cost": "13.45",
      "avg_tokens": 298
    }
  ],
  "daily_breakdown": [
    {
      "date": "2024-12-20",
      "jobs": 28,
      "cost": "12.45",
      "tokens": 8950,
      "avg_execution_time": 3.8
    },
    {
      "date": "2024-12-19",
      "jobs": 31,
      "cost": "15.67",
      "tokens": 9870,
      "avg_execution_time": 4.1
    }
  ],
  "top_costly_jobs": [
    {
      "job_id": "ai_job_xyz789",
      "cost": "2.45",
      "tokens": 12500,
      "model": "gpt-4o",
      "description": "Analyse complète document 50 pages"
    }
  ],
  "quality_metrics": {
    "success_rate": 0.987,
    "avg_execution_time": 4.2,
    "failed_jobs": 2,
    "timeout_jobs": 0
  }
}
```

### Cost Breakdown

#### `GET /ai/usage/cost_breakdown/`
**Breakdown détaillé des coûts**

**Paramètres** :
- `?month=2024-12` : Mois spécifique (défaut : mois courant)
- `?brand=9` : Par brand

**Réponse** :
```json
{
  "period": {
    "month": "2024-12",
    "start_date": "2024-12-01",
    "end_date": "2024-12-31"
  },
  "total_cost": "234.56",
  "budget_limit": "500.00",
  "budget_used_percentage": 46.9,
  "projected_monthly_cost": "310.45",
  "by_provider": [
    {
      "provider": "openai",
      "total_cost": "189.23",
      "percentage": 80.7,
      "jobs": 1247,
      "avg_cost_per_job": "0.152"
    },
    {
      "provider": "anthropic",
      "total_cost": "45.33", 
      "percentage": 19.3,
      "jobs": 312,
      "avg_cost_per_job": "0.145"
    }
  ],
  "by_model": [
    {
      "model": "gpt-4o",
      "provider": "openai",
      "cost": "156.78",
      "jobs": 890,
      "percentage": 66.8
    },
    {
      "model": "claude-3-5-sonnet-20241022",
      "provider": "anthropic",
      "cost": "45.33",
      "jobs": 312,
      "percentage": 19.3
    }
  ],
  "by_brand": [
    {
      "brand_id": 9,
      "brand_name": "Humari",
      "cost": "189.45",
      "jobs": 1205,
      "percentage": 80.8
    },
    {
      "brand_id": 10,
      "brand_name": "Academy",
      "cost": "45.11",
      "jobs": 354,
      "percentage": 19.2
    }
  ],
  "cost_trends": [
    {
      "week": "2024-W50",
      "cost": "45.67",
      "jobs": 287,
      "avg_daily": "6.52"
    }
  ]
}
```

### Usage Statistics

#### `GET /ai/usage/stats/`
**Statistiques globales d'usage**

**Réponse** :
```json
{
  "lifetime": {
    "total_jobs": 15470,
    "total_cost": "2,456.78",
    "total_tokens": 14567890,
    "avg_cost_per_token": 0.000168
  },
  "monthly": {
    "current_month": {
      "jobs": 1559,
      "cost": "234.56",
      "tokens": 1456789
    },
    "previous_month": {
      "jobs": 1378,
      "cost": "198.45",
      "tokens": 1234567
    },
    "growth": {
      "jobs_percentage": 13.1,
      "cost_percentage": 18.2,
      "tokens_percentage": 18.0
    }
  },
  "efficiency": {
    "avg_tokens_per_job": 934,
    "avg_cost_per_job": "0.151",
    "avg_execution_time": 4.7,
    "success_rate": 0.987
  },
  "top_performers": {
    "most_efficient_model": "gpt-3.5-turbo",
    "fastest_model": "gpt-3.5-turbo", 
    "most_used_model": "gpt-4o"
  }
}
```

---

## 🚨 Système d'Alertes

### Gestion des Alertes

#### `GET /ai/alerts/`
**Liste des alertes d'usage**

**Filtres** :
```http
?alert_type=quota_warning        # Type d'alerte
?provider_name=openai           # Par provider
?is_resolved=false              # Alertes actives
?created_at__gte=2024-12-01     # Depuis date
```

**Réponse** :
```json
{
  "count": 8,
  "results": [
    {
      "id": 15,
      "company": {"id": 1, "name": "Humari"},
      "provider_name": "openai",
      "alert_type": "quota_warning",
      "threshold_value": "80.00",
      "current_value": "87.50",
      "message": "Attention : Quota OpenAI à 87.5% (87.50$ sur 100.00$ mensuel)",
      "is_resolved": false,
      "resolved_at": null,
      "email_sent": true,
      "email_sent_at": "2024-12-20T14:30:00Z",
      "created_at": "2024-12-20T14:30:00Z"
    },
    {
      "id": 14,
      "company": {"id": 1, "name": "Humari"},
      "provider_name": "openai",
      "alert_type": "high_failure_rate",
      "threshold_value": "0.05",
      "current_value": "0.08",
      "message": "Taux d'échec élevé OpenAI : 8% (seuil : 5%)",
      "is_resolved": true,
      "resolved_at": "2024-12-19T16:00:00Z",
      "email_sent": true,
      "created_at": "2024-12-19T10:15:00Z"
    }
  ]
}
```

#### `GET /ai/alerts/active/`
**Alertes actives uniquement**

**Réponse simplifiée** :
```json
{
  "count": 3,
  "alerts": [
    {
      "id": 15,
      "type": "quota_warning",
      "provider": "openai",
      "message": "Quota OpenAI à 87.5%",
      "severity": "warning",
      "created_at": "2024-12-20T14:30:00Z"
    }
  ],
  "summary": {
    "quota_warnings": 2,
    "cost_warnings": 1,
    "failure_alerts": 0
  }
}
```

#### `POST /ai/alerts/check_alerts/`
**Vérifier et générer nouvelles alertes**

**Workflow automatique** :
1. **Check quotas** : Vérifie tous les quotas company
2. **Check costs** : Vérifie budgets mensuels
3. **Check failure rates** : Analyse taux d'échec recent
4. **Check unusual patterns** : Détecte usage anormal
5. **Generate alerts** : Crée alertes si seuils dépassés
6. **Send notifications** : Envoie emails si configuré

**Réponse** :
```json
{
  "checks_performed": [
    "quota_status", "cost_limits", "failure_rates", "usage_patterns"
  ],
  "new_alerts_created": 2,
  "alerts": [
    {
      "type": "cost_warning",
      "provider": "openai",
      "message": "Budget mensuel OpenAI dépassé : 105.67$ sur 100.00$"
    },
    {
      "type": "unusual_usage",
      "provider": "anthropic", 
      "message": "Usage Anthropic inhabituel : +340% vs moyenne"
    }
  ],
  "notifications_sent": 2
}
```

#### `POST /ai/alerts/{id}/resolve/`
**Résoudre une alerte**

**Paramètres optionnels** :
```json
{
  "resolution_note": "Quota augmenté à 150$"
}
```

**Réponse** :
```json
{
  "message": "Alert resolved successfully",
  "alert": {
    "id": 15,
    "is_resolved": true,
    "resolved_at": "2024-12-20T16:45:00Z"
  }
}
```

---

## 🔍 Analytics Avancés

### Usage Trends

#### `GET /ai/usage/trends/`
**Tendances d'usage temporelles**

**Paramètres** :
- `?period=week` : week, month, quarter
- `?metric=cost` : cost, tokens, jobs

**Réponse** :
```json
{
  "metric": "cost",
  "period": "week",
  "data_points": [
    {
      "period_label": "Semaine 49",
      "start_date": "2024-12-02",
      "end_date": "2024-12-08",
      "value": "45.67",
      "jobs": 287,
      "change_percentage": -12.3
    },
    {
      "period_label": "Semaine 50",
      "start_date": "2024-12-09", 
      "end_date": "2024-12-15",
      "value": "52.34",
      "jobs": 329,
      "change_percentage": 14.6
    }
  ],
  "summary": {
    "trend": "increasing",
    "avg_growth": 8.2,
    "volatility": "moderate"
  }
}
```

### Efficiency Analysis

#### `GET /ai/usage/efficiency/`
**Analyse d'efficacité des modèles**

**Réponse** :
```json
{
  "models_comparison": [
    {
      "model": "gpt-4o",
      "provider": "openai",
      "metrics": {
        "avg_cost_per_job": "0.167",
        "avg_execution_time": 3.8,
        "success_rate": 0.995,
        "avg_tokens": 421,
        "cost_per_token": 0.000397,
        "jobs_count": 890
      },
      "efficiency_score": 8.7,
      "recommendations": [
        "Excellent pour tâches complexes",
        "Coût élevé mais qualité supérieure"
      ]
    },
    {
      "model": "gpt-3.5-turbo",
      "provider": "openai",
      "metrics": {
        "avg_cost_per_job": "0.045",
        "avg_execution_time": 2.1,
        "success_rate": 0.978,
        "avg_tokens": 287,
        "cost_per_token": 0.000157,
        "jobs_count": 445
      },
      "efficiency_score": 9.2,
      "recommendations": [
        "Très économique pour tâches simples",
        "Rapidité excellente"
      ]
    }
  ],
  "overall_insights": {
    "most_cost_effective": "gpt-3.5-turbo",
    "highest_quality": "gpt-4o",
    "fastest": "gpt-3.5-turbo",
    "recommendations": [
      "Utiliser gpt-3.5-turbo pour tâches simples",
      "Réserver gpt-4o pour analyses complexes"
    ]
  }
}
```

---

## 🔧 Services Internes

### UsageService

#### `record_usage(ai_job, **metrics)`
**Enregistrement usage après job**

```python
usage = UsageService.record_usage(
    ai_job=ai_job,
    input_tokens=125,
    output_tokens=275, 
    cost_input=Decimal("0.000625"),
    cost_output=Decimal("0.004125"),
    execution_time_seconds=3,
    provider_name="openai",
    model_name="gpt-4o"
)
```

#### `get_usage_dashboard(brand, days)`
**Dashboard data generation**

#### `get_cost_breakdown(brand, month)`
**Cost breakdown calculation**

#### `calculate_efficiency_metrics(model, provider)`
**Métriques d'efficacité par modèle**

### AlertService

#### `check_quota_alerts(company)`
**Vérification alertes quota**

```python
new_alerts = AlertService.check_quota_alerts(company)
# Retourne: [{"type": "quota_warning", ...}]
```

#### `check_failure_rate_alerts(company, days=7)`
**Vérification taux d'échec**

#### `check_cost_alerts(company)`
**Vérification dépassements budget**

#### `send_alert_notification(alert)`
**Envoi notification email**

#### `resolve_alert(alert_id, resolution_note=None)`
**Résolution d'alerte**

---

## 📈 Intégrations Cross-App

### Avec ai_core
```python
# Création automatique usage après job completion
@receiver(post_save, sender=AIJob)
def create_usage_on_completion(sender, instance, **kwargs):
    if instance.status == 'completed' and not hasattr(instance, 'usage'):
        UsageService.record_usage(instance, ...)
```

### Avec ai_providers
```python
# Mise à jour quotas après usage
usage_recorded = UsageService.record_usage(...)
QuotaService.consume_quota(
    company, provider, usage_recorded.total_tokens, usage_recorded.total_cost
)
```

### Avec ai_openai
```python
# Usage tracking automatique OpenAI
openai_job.save()  # Trigger usage recording
usage = AIJobUsage.objects.create(
    ai_job=openai_job.ai_job,
    total_tokens=openai_job.total_tokens,
    provider_name="openai",
    model_name=openai_job.model
)
```

---

## 🚨 Types d'Alertes

### Quota Alerts
```python
QUOTA_ALERT_THRESHOLDS = {
    "quota_warning": 0.8,      # 80% quota
    "quota_critical": 0.95,    # 95% quota  
    "quota_exceeded": 1.0      # 100% quota
}
```

### Cost Alerts
```python
COST_ALERT_THRESHOLDS = {
    "cost_warning": 0.8,       # 80% budget mensuel
    "cost_exceeded": 1.0,      # 100% budget
    "daily_spike": 3.0         # 300% vs moyenne
}
```

### Quality Alerts
```python
QUALITY_ALERT_THRESHOLDS = {
    "high_failure_rate": 0.05,    # 5% taux d'échec
    "slow_execution": 30,         # 30s+ temps moyen
    "high_cost_deviation": 2.0    # 200% vs coût normal
}
```

---

## 💡 Bonnes Pratiques

### Monitoring
1. **Alertes préventives** : 80% des seuils
2. **Dashboard quotidien** : Suivi régulier
3. **Trend analysis** : Anticipation des besoins
4. **Cost optimization** : Choix modèles adaptés

### Performance
1. **Indexes optimisés** : Queries rapides
2. **Pagination** : Listes longues
3. **Aggregation DB** : Stats calculées côté base
4. **Cache** : Dashboards en cache

### Alerting
1. **Seuils réalistes** : Éviter faux positifs
2. **Notifications groupées** : Éviter spam
3. **Auto-resolution** : Alertes temporaires
4. **Escalation** : Alertes critiques → admin

---

**Cette documentation couvre le système complet d'usage et alertes. Pour les configurations providers, voir [ai_providers](./providers.md).**