# 📊 Task Monitoring API - Métriques & Surveillance

## Vue d'Ensemble
Le module `task_monitoring` fournit un système complet de surveillance des tâches avec métriques détaillées, alertes configurables et monitoring des workers.

**Base URL**: `/tasks/monitoring/`

---

## �� Authentification
```bash
Authorization: Bearer {jwt_token}
X-Brand-ID: {brand_id}
```

---

## 📊 TaskMetrics - Métriques de Performance

### Liste des Métriques
```http
GET /tasks/monitoring/metrics/
```

**Filtres disponibles:**
```
?base_task=123
?execution_time_ms__gte=1000
?memory_usage_mb__gte=100
?cpu_usage_percent__gte=50
?error_count__gt=0
?cost_usd__gte=0.01
?api_calls_count__gte=10
?tokens_used__gte=1000
?created_after=2024-12-01T00:00:00Z
?ordering=-execution_time_ms,cost_usd
```

**Réponse 200:**
```json
{
    "count": 150,
    "results": [
        {
            "id": 45,
            "base_task": {
                "id": 123,
                "task_id": "task_abc123def",
                "task_type": "seo_keyword_analysis",
                "status": "completed"
            },
            "execution_time_ms": 4500,
            "memory_usage_mb": 128,
            "cpu_usage_percent": 45.5,
            "error_count": 0,
            "queue_wait_time_ms": 200,
            "api_calls_count": 15,
            "tokens_used": 2400,
            "cost_usd": 0.048,
            "performance_score": 8.7,
            "created_at": "2024-12-20T15:45:00Z"
        }
    ]
}
```

### Créer des Métriques
```http
POST /tasks/monitoring/metrics/
```

**Body:**
```json
{
    "base_task": 123,
    "execution_time_ms": 3200,
    "memory_usage_mb": 256,
    "cpu_usage_percent": 62.3,
    "error_count": 1,
    "queue_wait_time_ms": 150,
    "api_calls_count": 8,
    "tokens_used": 1800,
    "cost_usd": 0.036
}
```

### Dashboard Métriques
```http
GET /tasks/monitoring/metrics/dashboard/
```

**Filtres optionnels:**
```
?days=7,30,90
?task_type=seo_analysis
?brand_id=9
```

**Réponse 200:**
```json
{
    "period": "last_7_days",
    "summary": {
        "total_tasks": 450,
        "avg_execution_time_ms": 3200,
        "avg_memory_usage_mb": 180,
        "avg_cpu_usage_percent": 52.1,
        "total_cost_usd": 15.67,
        "total_tokens_used": 125000,
        "total_api_calls": 890,
        "error_rate_percent": 3.2
    },
    "trends": {
        "execution_time": [
            {"date": "2024-12-14", "avg_ms": 3100},
            {"date": "2024-12-15", "avg_ms": 3300},
            {"date": "2024-12-16", "avg_ms": 2900}
        ],
        "cost": [
            {"date": "2024-12-14", "total_usd": 2.34},
            {"date": "2024-12-15", "total_usd": 2.78},
            {"date": "2024-12-16", "total_usd": 2.12}
        ],
        "memory_usage": [
            {"date": "2024-12-14", "avg_mb": 175},
            {"date": "2024-12-15", "avg_mb": 190},
            {"date": "2024-12-16", "avg_mb": 165}
        ]
    },
    "top_expensive_tasks": [
        {
            "task_type": "ai_content_generation",
            "total_cost_usd": 8.45,
            "avg_cost_per_task": 0.094,
            "task_count": 90
        }
    ],
    "performance_by_priority": {
        "critical": {"avg_ms": 1200, "count": 12},
        "high": {"avg_ms": 2800, "count": 85},
        "normal": {"avg_ms": 3500, "count": 320},
        "low": {"avg_ms": 5200, "count": 33}
    }
}
```

### Tendances de Performance
```http
GET /tasks/monitoring/metrics/trends/
```

**Paramètres:**
```
?days=30
?task_type=seo_analysis
?metric=execution_time_ms,memory_usage_mb,cost_usd
```

**Réponse 200:**
```json
{
    "period": 30,
    "metrics": {
        "execution_time_ms": {
            "trend": "decreasing",
            "change_percent": -12.5,
            "data_points": [
                {"date": "2024-11-20", "value": 3800},
                {"date": "2024-11-21", "value": 3650},
                {"date": "2024-12-20", "value": 3200}
            ]
        },
        "cost_usd": {
            "trend": "stable",
            "change_percent": 2.1,
            "data_points": [...]
        }
    }
}
```

---

## 🚨 AlertRule - Règles d'Alerte

### Liste des Règles d'Alerte
```http
GET /tasks/monitoring/alerts/
```

**Filtres:**
```
?is_active=true
?metric_field=execution_time_ms
?condition=gt,gte,lt,lte,eq
?threshold_value__gte=1000
```

**Réponse 200:**
```json
{
    "count": 25,
    "results": [
        {
            "id": 12,
            "name": "High Execution Time Alert",
            "brand": {
                "id": 9,
                "name": "Humari"
            },
            "description": "Alerte si temps d'exécution > 5 secondes",
            "metric_field": "execution_time_ms",
            "condition": "gt",
            "threshold_value": 5000,
            "is_active": true,
            "notification_emails": [
                "admin@humari.fr",
                "tech@humari.fr"
            ],
            "cooldown_minutes": 30,
            "trigger_count": 8,
            "last_triggered_at": "2024-12-20T14:22:00Z",
            "created_at": "2024-12-01T09:00:00Z"
        }
    ]
}
```

### Créer une Règle d'Alerte
```http
POST /tasks/monitoring/alerts/
```

**Body:**
```json
{
    "name": "Memory Usage Alert",
    "description": "Alerte si utilisation mémoire > 500MB",
    "metric_field": "memory_usage_mb",
    "condition": "gt", 
    "threshold_value": 500,
    "notification_emails": ["admin@humari.fr"],
    "cooldown_minutes": 60,
    "is_active": true
}
```

### Tester une Règle d'Alerte
```http
POST /tasks/monitoring/alerts/{id}/test/
```

**Body optionnel:**
```json
{
    "test_value": 6000,
    "send_notification": false
}
```

**Réponse 200:**
```json
{
    "would_trigger": true,
    "test_value": 6000,
    "threshold_value": 5000,
    "condition": "gt",
    "message": "Alert would be triggered: 6000 > 5000"
}
```

---

## 🖥️ WorkerHealth - Santé des Workers

### Vue d'Ensemble des Workers
```http
GET /tasks/monitoring/workers/overview/
```

**Réponse 200:**
```json
{
    "total_workers": 8,
    "online_workers": 7,
    "queues": {
        "critical": {
            "workers": 2,
            "active_tasks": 3,
            "avg_load": 0.6
        },
        "high": {
            "workers": 2,
            "active_tasks": 8,
            "avg_load": 2.1
        },
        "normal": {
            "workers": 3,
            "active_tasks": 15,
            "avg_load": 1.8
        },
        "low": {
            "workers": 1,
            "active_tasks": 2,
            "avg_load": 0.4
        }
    },
    "system_health": {
        "overall_status": "healthy",
        "avg_cpu_percent": 45.2,
        "avg_memory_percent": 62.8,
        "total_active_tasks": 28,
        "avg_load_average": 1.5
    }
}
```

### Liste des Workers
```http
GET /tasks/monitoring/workers/
```

**Filtres:**
```
?is_online=true
?queue_name=normal,high
?cpu_percent__gte=50
?memory_percent__gte=70
?active_tasks__gte=5
```

**Réponse 200:**
```json
{
    "count": 8,
    "results": [
        {
            "id": 5,
            "worker_name": "worker-normal-01",
            "queue_name": "normal",
            "is_online": true,
            "cpu_percent": 45.2,
            "memory_percent": 68.5,
            "active_tasks": 5,
            "processed_tasks": 1250,
            "failed_tasks": 18,
            "load_average": 1.8,
            "last_heartbeat": "2024-12-20T16:28:00Z",
            "uptime_hours": 72.5,
            "success_rate": 98.6
        }
    ]
}
```

### Détail d'un Worker
```http
GET /tasks/monitoring/workers/{id}/
```

**Réponse 200:**
```json
{
    "id": 5,
    "worker_name": "worker-normal-01",
    "queue_name": "normal",
    "is_online": true,
    "cpu_percent": 45.2,
    "memory_percent": 68.5,
    "active_tasks": 5,
    "processed_tasks": 1250,
    "failed_tasks": 18,
    "load_average": 1.8,
    "last_heartbeat": "2024-12-20T16:28:00Z",
    "uptime_hours": 72.5,
    "success_rate": 98.6,
    "current_tasks": [
        {
            "task_id": "task_abc123",
            "task_type": "seo_analysis",
            "started_at": "2024-12-20T16:25:00Z",
            "estimated_completion": "2024-12-20T16:35:00Z"
        }
    ],
    "recent_performance": {
        "last_hour": {
            "tasks_completed": 12,
            "avg_execution_time_ms": 3200,
            "errors": 0
        },
        "last_24_hours": {
            "tasks_completed": 285,
            "avg_execution_time_ms": 3100,
            "errors": 3
        }
    }
}
```

---

## 📈 Endpoints d'Analyse Avancée

### Performance par Type de Tâche
```http
GET /tasks/monitoring/metrics/performance-by-type/
```

**Paramètres:**
```
?days=30
?min_samples=10
```

**Réponse 200:**
```json
{
    "task_types": {
        "seo_keyword_analysis": {
            "total_executions": 450,
            "avg_execution_time_ms": 3200,
            "min_execution_time_ms": 800,
            "max_execution_time_ms": 12000,
            "p95_execution_time_ms": 8500,
            "avg_memory_usage_mb": 125,
            "avg_cost_usd": 0.042,
            "success_rate": 96.2,
            "trend": "improving"
        }
    }
}
```

### Détection d'Anomalies
```http
GET /tasks/monitoring/metrics/anomalies/
```

**Paramètres:**
```
?sensitivity=low,medium,high
?days=7
?metric=execution_time_ms,memory_usage_mb
```

**Réponse 200:**
```json
{
    "anomalies_detected": 5,
    "anomalies": [
        {
            "task_id": "task_xyz789",
            "metric": "execution_time_ms",
            "value": 45000,
            "expected_range": [2000, 8000],
            "severity": "high",
            "detected_at": "2024-12-20T15:30:00Z",
            "description": "Execution time 5.6x higher than normal"
        }
    ],
    "recommendations": [
        "Investigate task_xyz789 for potential optimization",
        "Consider increasing timeout for seo_analysis tasks"
    ]
}
```

---

## 🚨 Gestion des Alertes en Temps Réel

### Alertes Actives
```http
GET /tasks/monitoring/alerts/active/
```

**Réponse 200:**
```json
{
    "active_alerts": 3,
    "alerts": [
        {
            "id": 12,
            "name": "High Execution Time Alert",
            "triggered_at": "2024-12-20T16:15:00Z",
            "current_value": 8500,
            "threshold_value": 5000,
            "severity": "medium",
            "affected_tasks": ["task_abc123", "task_def456"]
        }
    ]
}
```

### Historique des Alertes
```http
GET /tasks/monitoring/alerts/history/
```

**Paramètres:**
```
?days=30
?alert_rule=12
?severity=high,medium
```

---

## 🔧 Configuration et Optimisation

### Recommandations de Performance
```http
GET /tasks/monitoring/metrics/recommendations/
```

**Réponse 200:**
```json
{
    "recommendations": [
        {
            "type": "performance",
            "priority": "high",
            "description": "Consider increasing worker count for 'normal' queue",
            "impact": "Reduce average wait time by ~40%",
            "implementation": "Add 2 workers to normal queue"
        },
        {
            "type": "cost",
            "priority": "medium", 
            "description": "Optimize AI token usage for content generation",
            "impact": "Reduce costs by ~15%",
            "implementation": "Review prompt efficiency"
        }
    ]
}
```

---

**Documentation mise à jour** : 2024-12-20 ✅
