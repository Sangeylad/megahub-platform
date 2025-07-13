# 🚀 MEGAHUB Tasks Infrastructure - API Documentation

## Vue d'Ensemble

L'infrastructure tasks MEGAHUB est architecturée en **4 apps spécialisées** suivant le principe de responsabilité unique, permettant une gestion complète des tâches asynchrones avec monitoring, persistence et scheduling.

### Base URLs
```
https://backoffice.humari.fr/tasks/           # Hub principal
https://backoffice.humari.fr/tasks/monitoring/  # Métriques et alertes
https://backoffice.humari.fr/tasks/persistent-jobs/  # Jobs persistants
https://backoffice.humari.fr/tasks/scheduled/    # Planification
```

---

## 📁 Architecture des Apps

### 🎯 task_core - Hub Central
**Responsabilité** : Modèle `BaseTask` central, gestion des tâches de base
- CRUD des tâches principales
- Statuts et priorités
- Retry et gestion d'erreurs
- [📖 Documentation Complète](./core.md)

### 📊 task_monitoring - Métriques & Alertes  
**Responsabilité** : Surveillance, métriques de performance, alertes
- Métriques détaillées (temps, mémoire, coût)
- Règles d'alerte configurables
- Santé des workers
- [📖 Documentation Complète](./monitoring.md)

### 💾 task_persistence - Jobs Persistants
**Responsabilité** : Tâches longues avec reprise, checkpoints
- Jobs resumables après interruption
- Système de checkpoints
- États de progression détaillés
- [📖 Documentation Complète](./persistence.md)

### ⏰ task_scheduling - Planification
**Responsabilité** : Tâches périodiques, cron jobs, calendriers
- Tâches périodiques avec expressions cron
- Jobs programmés
- Calendriers de tâches
- [📖 Documentation Complète](./scheduling.md)

---

## 🔑 Authentification

**Toutes les APIs** requièrent :
```bash
Authorization: Bearer {jwt_token}
X-Brand-ID: {brand_id}  # Scope automatique par brand
```

---

## 🎯 Endpoints Rapides

### Tâches de Base
```http
GET    /tasks/                    # Liste toutes les tâches
POST   /tasks/                    # Créer nouvelle tâche
GET    /tasks/{id}/               # Détail tâche
POST   /tasks/{id}/retry/         # Retry tâche échouée
GET    /tasks/queue-stats/        # Stats des queues
```

### Monitoring
```http
GET    /tasks/monitoring/metrics/dashboard/     # Dashboard métriques
GET    /tasks/monitoring/workers/overview/      # Vue d'ensemble workers
GET    /tasks/monitoring/alerts/                # Alertes actives
```

### Jobs Persistants
```http
GET    /tasks/persistent-jobs/persistent-jobs/resumable/  # Jobs resumables
POST   /tasks/persistent-jobs/persistent-jobs/{id}/resume/  # Reprendre job
GET    /tasks/persistent-jobs/checkpoints/      # Checkpoints
```

### Planification
```http
GET    /tasks/scheduled/periodic-tasks/ready-for-execution/  # Tâches prêtes
POST   /tasks/scheduled/periodic-tasks/validate-cron/        # Valider cron
GET    /tasks/scheduled/cron-jobs/              # Jobs planifiés
```

---

## 📈 Workflow Typique

### 1. Créer une Tâche SEO
```bash
POST /tasks/
{
  "task_type": "seo_keyword_analysis",
  "priority": "normal", 
  "description": "Analyser 500 mots-clés",
  "context_data": {
    "keyword_ids": [1,2,3,4,5],
    "analysis_depth": "full"
  }
}
```

### 2. Monitorer l'Exécution
```bash
GET /tasks/{id}/           # Progression
GET /tasks/monitoring/metrics/   # Métriques détaillées
```

### 3. Job Long avec Persistence
```bash
# Si interruption, reprendre automatiquement
POST /tasks/persistent-jobs/persistent-jobs/{id}/resume/
```

### 4. Programmer des Tâches Récurrentes
```bash
POST /tasks/scheduled/periodic-tasks/
{
  "cron_expression": "0 9 * * 1-5",  # Tous les jours ouvrés 9h
  "task_type": "daily_seo_report"
}
```

---

## 🔍 Filtres Avancés

### Filtres Cross-Apps
```http
# Tâches avec métriques spécifiques
GET /tasks/?has_metrics=true&execution_time__gte=2000

# Tâches resumables 
GET /tasks/?is_resumable=true

# Tâches périodiques actives
GET /tasks/?is_periodic=true&status=active
```

### Recherche Textuelle
```http
GET /tasks/?search=keyword_analysis
GET /tasks/monitoring/metrics/?search=high_memory
```

---

## 📊 Exemples de Réponses

### Tâche Complète
```json
{
  "id": 123,
  "task_id": "task_abc123def", 
  "task_type": "seo_keyword_analysis",
  "status": "completed",
  "priority": "normal",
  "progress_percentage": 100,
  "brand": {"id": 9, "name": "Humari"},
  "created_by": {"id": 1, "username": "martin"},
  "created_at": "2024-12-20T14:30:00Z",
  "completed_at": "2024-12-20T15:45:00Z",
  "result_data": {
    "keywords_processed": 500,
    "insights_generated": 45
  },
  "metrics": {
    "execution_time_ms": 4500,
    "memory_usage_mb": 128,
    "cost_usd": 0.034
  }
}
```

---

## 🚨 Gestion d'Erreurs

### Codes de Statut
- **200**: Succès
- **201**: Création réussie  
- **400**: Validation échouée
- **401**: Non authentifié
- **403**: Permissions insuffisantes
- **404**: Ressource non trouvée
- **500**: Erreur serveur

### Format d'Erreurs
```json
{
  "detail": "Task not found or access denied",
  "error_code": "TASK_NOT_FOUND",
  "field_errors": {
    "priority": ["Ce champ est requis"]
  }
}
```

---

## 📖 Documentation Détaillée

- **[🎯 task_core](./core.md)** - Hub central des tâches
- **[📊 task_monitoring](./monitoring.md)** - Métriques et surveillance  
- **[💾 task_persistence](./persistence.md)** - Jobs persistants
- **[⏰ task_scheduling](./scheduling.md)** - Planification
- **[�� Référence Complète](./complete-reference.md)** - Tous les endpoints

---

**Version** : 1.0 - Infrastructure complète et testée ✅
