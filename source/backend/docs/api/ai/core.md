# 🎯 AI Core - Hub Central des Jobs IA

## Vue d'Ensemble

L'app `ai_core` est le **hub central** de toute l'infrastructure IA MEGAHUB. Elle gère les jobs IA principales, leurs types, statuts et workflows de progression. Toutes les autres apps IA (providers, openai, usage) référencent les jobs créés ici.

### Responsabilité
- **AIJob** : Modèle central référencé par toutes extensions
- **AIJobType** : Types de jobs disponibles avec catégories
- **Workflow statuts** : Gestion du cycle de vie des jobs
- **Dashboard central** : Vue d'ensemble de l'activité IA

### Base URL
```
https://backoffice.humari.fr/ai/
```

---

## 📊 Modèles de Données

### AIJobType
```python
# Types de jobs IA disponibles
- name: str (unique) # "chat_completion", "text_generation"
- description: str # Description détaillée
- category: str # "chat", "assistant", "upload", "analysis", "generation"
- estimated_duration_seconds: int # Durée estimée
- requires_async: bool # Nécessite traitement async
```

### AIJob (Modèle Central)
```python
# Job IA principal - référencé par extensions
- job_id: str (unique) # Identifiant unique généré
- job_type: FK → AIJobType
- brand: FK → Brand # Scope automatique
- created_by: FK → User # Utilisateur créateur

# Workflow
- status: str # pending, running, completed, failed, cancelled, timeout
- priority: str # low, normal, high, urgent
- progress_percentage: int # 0-100

# Données
- input_data: JSON # Paramètres d'entrée
- result_data: JSON # Résultats de sortie
- error_message: str # Message d'erreur si échec

# Tracking
- started_at: datetime
- completed_at: datetime
- task_id: str # Intégration task_core si async
- is_async: bool

# Métadonnées
- description: str # Description du job
```

**Relations** :
- **OneToOne** avec `ai_openai.OpenAIJob` (si job OpenAI)
- **OneToOne** avec `ai_usage.AIJobUsage` (tracking usage)
- **Référencé par** tous les providers spécialisés

---

## 🎯 Endpoints

### AIJobType Management

#### `GET /ai/job-types/`
**Liste des types de jobs disponibles**

**Réponse** :
```json
[
  {
    "id": 1,
    "name": "chat_completion",
    "description": "Conversation interactive avec l'IA",
    "category": "chat",
    "estimated_duration_seconds": 10,
    "requires_async": false
  },
  {
    "id": 2,
    "name": "content_analysis",
    "description": "Analyse de contenu existant",
    "category": "analysis",
    "estimated_duration_seconds": 45,
    "requires_async": true
  }
]
```

### AIJob Management

#### `GET /ai/jobs/`
**Liste des jobs IA avec filtres avancés**

**Filtres disponibles** :
```http
?status=completed              # Par statut
?priority=high                 # Par priorité
?job_type=chat_completion     # Par type de job
?created_by=1                 # Par utilisateur
?is_async=true                # Jobs asynchrones
?progress_percentage__gte=50  # Progression minimum
?created_at__gte=2024-01-01   # Depuis une date
?search=keyword_analysis      # Recherche textuelle
```

**Réponse paginée** :
```json
{
  "count": 156,
  "next": "?page=2",
  "previous": null,
  "results": [
    {
      "id": 123,
      "job_id": "ai_job_abc123def",
      "job_type": {
        "id": 1,
        "name": "chat_completion",
        "category": "chat"
      },
      "status": "completed",
      "priority": "normal",
      "progress_percentage": 100,
      "brand": {"id": 9, "name": "Humari"},
      "created_by": {"id": 1, "username": "martin"},
      "created_at": "2024-12-20T14:30:00Z",
      "completed_at": "2024-12-20T15:45:00Z",
      "description": "Analyse SEO de contenu",
      "input_data": {
        "messages": [{"role": "user", "content": "Analyse..."}],
        "model": "gpt-4o"
      },
      "result_data": {
        "completion": "Réponse IA...",
        "finish_reason": "stop"
      },
      "error_message": "",
      "execution_time_seconds": 75
    }
  ]
}
```

#### `POST /ai/jobs/`
**Créer un nouveau job IA**

**Paramètres requis** :
```json
{
  "job_type": "chat_completion",     // Nom du type de job
  "priority": "normal",              // low, normal, high, urgent
  "description": "Analyse contenu SEO",
  "input_data": {
    "messages": [
      {"role": "user", "content": "Analyse ce contenu..."}
    ],
    "model": "gpt-4o",
    "max_tokens": 500
  }
}
```

**Auto-assignation** :
- `brand` : Depuis `request.current_brand` (middleware)
- `created_by` : Depuis `request.user` 
- `job_id` : Généré automatiquement
- `status` : "pending" par défaut

**Réponse** :
```json
{
  "id": 124,
  "job_id": "ai_job_def456ghi",
  "job_type": {
    "name": "chat_completion",
    "category": "chat"
  },
  "status": "pending",
  "priority": "normal",
  "progress_percentage": 0,
  "brand": {"id": 9, "name": "Humari"},
  "created_by": {"id": 1, "username": "martin"},
  "created_at": "2024-12-20T16:00:00Z",
  "description": "Analyse contenu SEO",
  "input_data": {
    "messages": [{"role": "user", "content": "Analyse ce contenu..."}],
    "model": "gpt-4o",
    "max_tokens": 500
  }
}
```

#### `GET /ai/jobs/{id}/`
**Détail complet d'un job IA**

Inclut toutes les extensions (OpenAI, usage) via relations OneToOne :
```json
{
  "id": 123,
  "job_id": "ai_job_abc123def",
  // ... données de base ...
  
  // Extensions automatiques
  "openai_job": {
    "model": "gpt-4o",
    "temperature": 0.7,
    "total_tokens": 150,
    "completion_tokens": 75,
    "prompt_tokens": 75
  },
  "usage": {
    "total_cost": "0.004500",
    "execution_time_seconds": 2,
    "provider_name": "openai",
    "success_rate": 1.0
  }
}
```

#### `PUT /ai/jobs/{id}/`
**Mise à jour d'un job IA**

**Champs modifiables** :
- `description`
- `priority` 
- `input_data` (si status = pending)
- `progress_percentage` (pour jobs async)

#### `DELETE /ai/jobs/{id}/`
**Suppression d'un job IA**

**Restrictions** :
- Jobs en cours (`running`) ne peuvent pas être supprimés
- Utiliser `POST /ai/jobs/{id}/cancel/` pour annuler

---

## 🎛️ Actions Spécialisées

### Dashboard

#### `GET /ai/jobs/dashboard/`
**Dashboard central des jobs IA**

**Réponse** :
```json
{
  "stats": {
    "total_jobs": 1547,
    "jobs_today": 23,
    "pending": 5,
    "running": 3,
    "completed": 1520,
    "failed": 14,
    "cancelled": 5
  },
  "recent_jobs": [
    // 10 derniers jobs
  ],
  "top_job_types": [
    {"name": "chat_completion", "count": 890},
    {"name": "content_analysis", "count": 445},
    {"name": "text_generation", "count": 212}
  ],
  "daily_activity": [
    {"date": "2024-12-20", "jobs": 23, "total_cost": "1.45"},
    {"date": "2024-12-19", "jobs": 31, "total_cost": "2.12"}
  ],
  "brand_breakdown": [
    {"brand_name": "Humari", "jobs": 1200, "cost": "45.67"},
    {"brand_name": "Academy", "jobs": 347, "cost": "12.34"}
  ]
}
```

### Filtrage par Statut

#### `GET /ai/jobs/by_status/?status=pending`
**Jobs filtrés par statut spécifique**

**Paramètres** :
- `status` (requis) : pending, running, completed, failed, cancelled, timeout

**Réponse** :
```json
{
  "jobs": [
    {
      "id": 125,
      "job_id": "ai_job_ghi789jkl",
      "job_type": {"name": "content_analysis"},
      "priority": "high",
      "created_at": "2024-12-20T16:15:00Z",
      "description": "Analyse urgente contenu blog"
    }
  ],
  "count": 5
}
```

### Annulation de Job

#### `POST /ai/jobs/{id}/cancel/`
**Annuler un job en cours**

**Conditions** :
- Job doit être en statut `pending` ou `running`
- Utilisateur doit avoir accès à la brand du job

**Réponse** :
```json
{
  "message": "Job cancelled successfully",
  "job": {
    "id": 125,
    "job_id": "ai_job_ghi789jkl", 
    "status": "cancelled",
    "cancelled_at": "2024-12-20T16:20:00Z"
  }
}
```

**Erreurs** :
```json
// Si job ne peut pas être annulé
{
  "error": "Job cannot be cancelled",
  "current_status": "completed"
}
```

---

## 🔄 Workflow des Statuts

### Cycle de Vie Standard
```
pending → running → completed
         ↓
      cancelled
         ↓
      timeout
         ↓
      failed
```

### Transitions Autorisées
- **pending** → running, cancelled
- **running** → completed, failed, timeout, cancelled  
- **completed/failed/cancelled/timeout** → (états finaux)

### Gestion Auto des Timestamps
- **started_at** : Mis à jour automatiquement sur passage à `running`
- **completed_at** : Mis à jour sur passage à état final
- **progress_percentage** : Peut être mis à jour pendant `running`

---

## 🔗 Intégrations Cross-App

### Extension OpenAI
```python
# Si job utilise OpenAI
POST /ai/jobs/ → Créé AIJob central
POST /ai/openai/chat/ → Créé OpenAIJob lié + exécute
```

### Tracking Usage
```python
# Automatic lors completion
AIJob.status = 'completed' → Trigger création AIJobUsage
```

### Task Core Integration
```python
# Jobs asynchrones
AIJob.requires_async = True → Création task dans task_core
AIJob.task_id = 'task_xyz' → Liaison avec infrastructure tasks
```

---

## 📊 Analytics et Monitoring

### Métriques Automatiques
- **Temps d'exécution** : `completed_at - started_at`
- **Taux de succès** : `completed / total`
- **Distribution priorités** : Breakdown par priority
- **Usage par brand** : Agrégation automatique

### Requêtes Optimisées
```python
# Dans les ViewSets
.select_related('job_type', 'brand', 'created_by')
.prefetch_related('openai_job', 'usage')
```

### Indexes Performants
```python
# Indexes DB stratégiques
['status', 'created_at']      # Dashboard
['brand', 'status']           # Filtrage brand
['job_id']                    # Lookups rapides
```

---

## 🚨 Gestion d'Erreurs

### Validation Création
```python
# Job type validation
if job_type not in available_types:
    raise ValidationError("Job type 'xyz' non trouvé")

# Brand access validation (middleware)
if not request.current_brand:
    raise PermissionDenied("Brand access required")
```

### Erreurs Fréquentes
```json
// Job type invalide
{
  "detail": "Job type 'invalid_type' non trouvé",
  "error_code": "JOB_TYPE_NOT_FOUND"
}

// Quota dépassé (provider)
{
  "detail": "Monthly quota exceeded for OpenAI",
  "error_code": "QUOTA_EXCEEDED",
  "remaining_quota": 0
}

// Job en cours non modifiable
{
  "detail": "Cannot modify running job",
  "error_code": "JOB_RUNNING",
  "current_status": "running"
}
```

---

## 🔧 Services Internes

### JobService
```python
# Gestion lifecycle jobs
JobService.create_job(job_type, input_data, user, brand)
JobService.start_job(job_id)
JobService.complete_job(job_id, result_data)
JobService.fail_job(job_id, error_message)
```

### StatusService  
```python
# Analytics et stats
StatusService.get_dashboard_stats(brand=None)
StatusService.get_jobs_by_status(status, brand=None)
StatusService.get_brand_breakdown()
```

---

## 💡 Bonnes Pratiques

### Création de Jobs
1. **Toujours spécifier job_type** valide
2. **Description claire** pour traçabilité  
3. **input_data structuré** selon le provider
4. **Gestion priority** selon urgence business

### Extensions Providers
1. **OneToOne relation** avec AIJob
2. **Données spécialisées** dans extension
3. **Status sync** avec job central
4. **Usage tracking** automatique

### Performance
1. **Pagination** sur toutes les listes
2. **Filtres DB** plutôt que Python
3. **select_related** pour relations fréquentes
4. **Indexes** sur champs de tri/filtrage

---

**Cette documentation couvre l'ensemble du hub central ai_core. Pour les intégrations spécialisées, voir [ai_openai](./openai.md), [ai_providers](./providers.md) et [ai_usage](./usage.md).**