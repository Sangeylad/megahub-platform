# 📋 MEGAHUB Tasks - Référence Complète des Endpoints

## 🎯 Vue d'Ensemble

Cette référence complète liste **TOUS les endpoints** de l'infrastructure tasks MEGAHUB, organisés par app avec URLs complètes et méthodes HTTP.

**Base URL** : `https://backoffice.humari.fr`

---

## 🔑 Headers Requis Partout

```bash
Authorization: Bearer {jwt_token}
X-Brand-ID: {brand_id}
Content-Type: application/json
```

---

## 🎯 TASK_CORE - Hub Central

**Base URL** : `/tasks/`

### Endpoints CRUD Standard
```http
GET    /tasks/                    # Liste toutes les tâches
POST   /tasks/                    # Créer nouvelle tâche
GET    /tasks/{id}/               # Détail d'une tâche
PUT    /tasks/{id}/               # Modifier tâche complète
PATCH  /tasks/{id}/               # Modifier tâche partielle
DELETE /tasks/{id}/               # Supprimer tâche
```

### Actions Spéciales
```http
POST   /tasks/{id}/retry/         # Retry tâche échouée
POST   /tasks/{id}/cancel/        # Annuler tâche
GET    /tasks/queue-stats/        # Statistiques des queues
GET    /tasks/type-stats/         # Stats par type de tâche
```

---

## 📊 TASK_MONITORING - Métriques & Surveillance

**Base URL** : `/tasks/monitoring/`

### TaskMetrics - Métriques de Performance
```http
GET    /tasks/monitoring/metrics/                    # Liste métriques
POST   /tasks/monitoring/metrics/                    # Créer métriques
GET    /tasks/monitoring/metrics/{id}/               # Détail métriques
PUT    /tasks/monitoring/metrics/{id}/               # Modifier métriques
DELETE /tasks/monitoring/metrics/{id}/               # Supprimer métriques

# Actions spécialisées
GET    /tasks/monitoring/metrics/dashboard/          # Dashboard complet
GET    /tasks/monitoring/metrics/trends/             # Tendances performance
GET    /tasks/monitoring/metrics/performance-by-type/ # Performance par type
GET    /tasks/monitoring/metrics/anomalies/          # Détection anomalies
GET    /tasks/monitoring/metrics/recommendations/    # Recommandations
```

### AlertRule - Règles d'Alerte
```http
GET    /tasks/monitoring/alerts/                     # Liste règles d'alerte
POST   /tasks/monitoring/alerts/                     # Créer règle
GET    /tasks/monitoring/alerts/{id}/                # Détail règle
PUT    /tasks/monitoring/alerts/{id}/                # Modifier règle
DELETE /tasks/monitoring/alerts/{id}/                # Supprimer règle

# Actions spécialisées
POST   /tasks/monitoring/alerts/{id}/test/           # Tester règle
GET    /tasks/monitoring/alerts/active/              # Alertes actives
GET    /tasks/monitoring/alerts/history/             # Historique alertes
```

### WorkerHealth - Santé des Workers
```http
GET    /tasks/monitoring/workers/                    # Liste workers
POST   /tasks/monitoring/workers/                    # Enregistrer worker
GET    /tasks/monitoring/workers/{id}/               # Détail worker
PUT    /tasks/monitoring/workers/{id}/               # Modifier worker
DELETE /tasks/monitoring/workers/{id}/               # Supprimer worker

# Actions spécialisées
GET    /tasks/monitoring/workers/overview/           # Vue d'ensemble
```

---

## 💾 TASK_PERSISTENCE - Jobs Persistants

**Base URL** : `/tasks/persistent-jobs/`

### PersistentJob - Jobs Persistants
```http
GET    /tasks/persistent-jobs/persistent-jobs/       # Liste jobs
POST   /tasks/persistent-jobs/persistent-jobs/       # Créer job
GET    /tasks/persistent-jobs/persistent-jobs/{id}/  # Détail job
PUT    /tasks/persistent-jobs/persistent-jobs/{id}/  # Modifier job
DELETE /tasks/persistent-jobs/persistent-jobs/{id}/  # Supprimer job

# Actions de contrôle
POST   /tasks/persistent-jobs/persistent-jobs/{id}/resume/     # Reprendre job
POST   /tasks/persistent-jobs/persistent-jobs/{id}/pause/      # Pauser job
POST   /tasks/persistent-jobs/persistent-jobs/{id}/restart/    # Redémarrer job

# Actions bulk
GET    /tasks/persistent-jobs/persistent-jobs/resumable/       # Jobs resumables
POST   /tasks/persistent-jobs/persistent-jobs/auto-resume/     # Auto-resume
POST   /tasks/persistent-jobs/persistent-jobs/cleanup-old/     # Nettoyage
POST   /tasks/persistent-jobs/persistent-jobs/validate-config/ # Validation config
GET    /tasks/persistent-jobs/persistent-jobs/stats/           # Statistiques
```

### JobCheckpoint - Points de Sauvegarde
```http
GET    /tasks/persistent-jobs/checkpoints/           # Liste checkpoints
POST   /tasks/persistent-jobs/checkpoints/           # Créer checkpoint
GET    /tasks/persistent-jobs/checkpoints/{id}/      # Détail checkpoint
PUT    /tasks/persistent-jobs/checkpoints/{id}/      # Modifier checkpoint
DELETE /tasks/persistent-jobs/checkpoints/{id}/      # Supprimer checkpoint

# Actions spécialisées
POST   /tasks/persistent-jobs/checkpoints/optimize-storage/ # Optimiser stockage
```

---

## ⏰ TASK_SCHEDULING - Planification

**Base URL** : `/tasks/scheduled/`

### PeriodicTask - Tâches Périodiques
```http
GET    /tasks/scheduled/periodic-tasks/              # Liste tâches périodiques
POST   /tasks/scheduled/periodic-tasks/              # Créer tâche périodique
GET    /tasks/scheduled/periodic-tasks/{id}/         # Détail tâche
PUT    /tasks/scheduled/periodic-tasks/{id}/         # Modifier tâche
DELETE /tasks/scheduled/periodic-tasks/{id}/         # Supprimer tâche

# Actions de contrôle
POST   /tasks/scheduled/periodic-tasks/{id}/toggle/  # Activer/Désactiver
POST   /tasks/scheduled/periodic-tasks/{id}/execute-now/ # Exécuter maintenant

# Actions bulk et analyse
GET    /tasks/scheduled/periodic-tasks/ready-for-execution/  # Tâches prêtes
POST   /tasks/scheduled/periodic-tasks/execute-ready/        # Exécuter prêtes
POST   /tasks/scheduled/periodic-tasks/validate-cron/        # Valider cron
GET    /tasks/scheduled/periodic-tasks/cron-templates/       # Templates cron
GET    /tasks/scheduled/periodic-tasks/stats/                # Statistiques
GET    /tasks/scheduled/periodic-tasks/performance-analysis/ # Analyse performance
GET    /tasks/scheduled/periodic-tasks/timezone-info/        # Info timezones
POST   /tasks/scheduled/periodic-tasks/optimize-schedules/   # Optimiser horaires
```

### CronJob - Jobs Programmés  
```http
GET    /tasks/scheduled/cron-jobs/                   # Liste jobs cron
POST   /tasks/scheduled/cron-jobs/                   # Créer job cron
GET    /tasks/scheduled/cron-jobs/{id}/              # Détail job
PUT    /tasks/scheduled/cron-jobs/{id}/              # Modifier job
DELETE /tasks/scheduled/cron-jobs/{id}/              # Supprimer job

# Actions spécialisées
POST   /tasks/scheduled/cron-jobs/{id}/execute/      # Exécuter maintenant
```

### TaskCalendar - Calendriers
```http
GET    /tasks/scheduled/calendars/                   # Liste calendriers
POST   /tasks/scheduled/calendars/                   # Créer calendrier
GET    /tasks/scheduled/calendars/{id}/              # Détail calendrier
PUT    /tasks/scheduled/calendars/{id}/              # Modifier calendrier
DELETE /tasks/scheduled/calendars/{id}/              # Supprimer calendrier

# Événements
GET    /tasks/scheduled/calendars/{id}/events/       # Événements calendrier
```

---

## 🔍 Filtres Globaux Disponibles

### Filtres Communs (Toutes les Apps)
```
# Dates
?created_after=2024-12-01T00:00:00Z
?created_before=2024-12-31T23:59:59Z
?updated_after=2024-12-15T00:00:00Z

# Recherche
?search=keyword_analysis
?ordering=-created_at,priority

# Pagination
?page=2
?page_size=50
```

### Filtres task_core
```
?status=pending,running,completed,failed,cancelled
?priority=low,normal,high,critical  
?task_type=seo_analysis,content_generation
?has_metrics=true
?is_resumable=true
?retry_count__gte=1
```

### Filtres task_monitoring
```
# Métriques
?execution_time_ms__gte=1000
?memory_usage_mb__gte=100
?cpu_usage_percent__gte=50
?cost_usd__gte=0.01
?error_count__gt=0

# Alertes
?is_active=true
?metric_field=execution_time_ms
?condition=gt,gte,lt,lte,eq
?last_triggered_after=2024-12-01T00:00:00Z

# Workers
?is_online=true
?queue_name=normal,high,critical
?active_tasks__gte=5
```

### Filtres task_persistence
```
?can_resume=true
?current_step=processing,finalization
?progress_gte=50
?progress_lte=90
?has_checkpoints=true
```

### Filtres task_scheduling
```
# Périodiques
?is_active=true
?cron_expression=0 9 * * 1-5
?timezone=Europe/Paris
?next_run_before=2024-12-25T00:00:00Z
?last_run_status=success,failed

# Cron jobs
?frequency=daily,weekly,monthly
?task_type=backup,report,cleanup

# Calendriers
?brand=9
?has_events=true
```

---

## 📊 Structures de Réponse Types

### Réponse Liste Standard
```json
{
    "count": 25,
    "next": "?page=2",
    "previous": null,
    "results": [...]
}
```

### Réponse Tâche Complète
```json
{
    "id": 123,
    "task_id": "task_abc123def",
    "task_type": "seo_keyword_analysis", 
    "status": "completed",
    "priority": "normal",
    "description": "Analyse 500 mots-clés",
    "progress_percentage": 100,
    "brand": {"id": 9, "name": "Humari"},
    "created_by": {"id": 1, "username": "martin"},
    "created_at": "2024-12-20T14:30:00Z",
    "updated_at": "2024-12-20T15:45:00Z",
    "started_at": "2024-12-20T14:31:00Z", 
    "completed_at": "2024-12-20T15:45:00Z",
    "context_data": {...},
    "result_data": {...},
    "error_message": null,
    "retry_count": 0,
    "max_retries": 3
}
```

### Réponse Dashboard Monitoring
```json
{
    "period": "last_7_days",
    "summary": {
        "total_tasks": 450,
        "avg_execution_time_ms": 3200,
        "avg_memory_usage_mb": 180,
        "total_cost_usd": 15.67,
        "error_rate_percent": 3.2
    },
    "trends": {...},
    "top_expensive_tasks": [...],
    "performance_by_priority": {...}
}
```

### Réponse Job Persistant
```json
{
    "id": 78,
    "base_task": {...},
    "job_data": {
        "total_pages": 500,
        "processed_pages": 375,
        "target_pages": [...]
    },
    "current_step": "content_analysis",
    "total_steps": 5,
    "progress_percentage": 75,
    "can_resume": true,
    "checkpoints_count": 8,
    "estimated_completion": "2024-12-20T17:30:00Z"
}
```

---

## 🚨 Codes d'Erreur Spécifiques

### Erreurs task_core
```
TASK_NOT_FOUND - Tâche introuvable
INVALID_STATUS_TRANSITION - Transition de statut invalide  
MAX_RETRIES_EXCEEDED - Nombre max de retry dépassé
TASK_ALREADY_COMPLETED - Tâche déjà terminée
```

### Erreurs task_monitoring
```
METRIC_FIELD_INVALID - Champ de métrique invalide
THRESHOLD_OUT_OF_RANGE - Seuil hors limites
ALERT_COOLDOWN_ACTIVE - Alerte en période de cooldown
```

### Erreurs task_persistence
```
JOB_NOT_RESUMABLE - Job non resumable
CHECKPOINT_CORRUPTED - Checkpoint corrompu
INVALID_JOB_STATE - État de job invalide
```

### Erreurs task_scheduling  
```
INVALID_CRON_EXPRESSION - Expression cron invalide
SCHEDULE_IN_PAST - Planification dans le passé
FREQUENCY_NOT_SUPPORTED - Fréquence non supportée
TIMEZONE_INVALID - Timezone invalide
```

---

## 📈 Exemples de Workflows API

### 1. Créer et Monitorer une Tâche
```bash
# 1. Créer tâche
POST /tasks/
{
    "task_type": "seo_audit",
    "priority": "high",
    "context_data": {"site_id": 123}
}

# 2. Suivre progression
GET /tasks/456/

# 3. Voir métriques
GET /tasks/monitoring/metrics/?base_task=456
```

### 2. Job Persistant avec Reprise
```bash
# 1. Créer job persistant
POST /tasks/persistent-jobs/persistent-jobs/
{
    "base_task": 123,
    "job_data": {"total_items": 1000}
}

# 2. Si interruption, lister resumables
GET /tasks/persistent-jobs/persistent-jobs/resumable/

# 3. Reprendre job
POST /tasks/persistent-jobs/persistent-jobs/78/resume/
```

### 3. Planifier Tâche Récurrente
```bash
# 1. Valider expression cron
POST /tasks/scheduled/periodic-tasks/validate-cron/
{
    "cron_expression": "0 9 * * 1-5"
}

# 2. Créer tâche périodique
POST /tasks/scheduled/periodic-tasks/
{
    "base_task": 156,
    "cron_expression": "0 9 * * 1-5"
}

# 3. Monitorer exécutions
GET /tasks/scheduled/periodic-tasks/stats/
```

---

## 🔧 Configuration Recommandée

### Headers pour Performance
```bash
# Compression (si supportée)
Accept-Encoding: gzip, deflate

# Cache (pour GET statiques)
Cache-Control: max-age=300

# Format de réponse
Accept: application/json
```

### Pagination Optimale
```bash
# Pages moyennes (balance performance/UX)
?page_size=25

# Grandes listes (monitoring)
?page_size=100

# Petites listes (formulaires)  
?page_size=10
```

### Filtres Performants
```bash
# Utiliser des ranges plutôt que des valeurs exactes
?created_after=2024-12-01T00:00:00Z

# Combiner les filtres pour réduire les résultats
?status=running&priority=high&task_type=seo_analysis

# Ordonner par champs indexés
?ordering=-created_at
```

---

## 📋 Checklist Intégration

### ✅ Avant de Commencer
- [ ] Token JWT valide obtenu
- [ ] Brand ID configuré
- [ ] Base URL correcte (backoffice.humari.fr)
- [ ] Headers requis configurés

### ✅ Tests de Base
- [ ] GET /tasks/ → Liste des tâches
- [ ] POST /tasks/ → Création tâche
- [ ] GET /tasks/monitoring/metrics/dashboard/ → Dashboard
- [ ] GET /tasks/scheduled/periodic-tasks/ → Tâches périodiques

### ✅ Gestion d'Erreurs
- [ ] Gestion 401 (token expiré)
- [ ] Gestion 403 (permissions)
- [ ] Gestion 400 (validation)
- [ ] Retry logic pour 5xx

### ✅ Optimisations
- [ ] Pagination implémentée
- [ ] Filtres selon use cases
- [ ] Cache pour données statiques
- [ ] Loading states pour UX

---

**Documentation complète** - Version 1.0 - Infrastructure tasks MEGAHUB ✅
**Dernière mise à jour** : 2024-12-20
