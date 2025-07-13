# 🎯 Task Core API - Hub Central des Tâches

## Vue d'Ensemble
Le module `task_core` centralise la gestion des tâches avec le modèle `BaseTask` comme hub principal. Toutes les autres apps tasks étendent ce modèle via des relations OneToOne.

**Base URL**: `/tasks/`

---

## 🔑 Authentification
```bash
Authorization: Bearer {jwt_token}
X-Brand-ID: {brand_id}
```

---

## 📋 Endpoints Disponibles

### Liste des Tâches
```http
GET /tasks/
```

**Filtres disponibles:**
```
?status=pending,running,completed,failed,cancelled
?priority=low,normal,high,critical
?task_type=seo_analysis,content_generation,keyword_research
?created_after=2024-01-01T00:00:00Z
?created_before=2024-12-31T23:59:59Z
?search=keyword_research
?has_metrics=true
?is_resumable=true
?ordering=-created_at,priority,status
```

**Réponse 200:**
```json
{
    "count": 25,
    "next": "?page=2",
    "previous": null,
    "results": [
        {
            "id": 123,
            "task_id": "task_abc123def",
            "task_type": "seo_keyword_analysis",
            "status": "completed",
            "priority": "normal",
            "description": "Analyse 500 mots-clés pour site client",
            "progress_percentage": 100,
            "brand": {
                "id": 9,
                "name": "Humari"
            },
            "created_by": {
                "id": 1,
                "username": "martin"
            },
            "created_at": "2024-12-20T14:30:00Z",
            "updated_at": "2024-12-20T15:45:00Z",
            "started_at": "2024-12-20T14:31:00Z",
            "completed_at": "2024-12-20T15:45:00Z",
            "context_data": {
                "keyword_ids": [1, 2, 3],
                "analysis_depth": "full"
            },
            "result_data": {
                "keywords_processed": 500,
                "insights_generated": 45,
                "recommendations": [
                    "Optimiser 12 pages pour mots-clés TOFU",
                    "Créer 3 articles de blog ciblant MOFU"
                ]
            },
            "error_message": null,
            "retry_count": 0,
            "max_retries": 3
        }
    ]
}
```

### Créer une Tâche
```http
POST /tasks/
```

**Body requis:**
```json
{
    "task_type": "content_optimization",
    "priority": "normal",
    "description": "Optimiser 10 pages pour nouveaux mots-clés",
    "context_data": {
        "page_ids": [1, 2, 3, 4, 5],
        "target_keywords": ["marketing digital", "seo technique"],
        "optimization_level": "advanced",
        "include_meta_tags": true,
        "include_content_suggestions": true
    }
}
```

**Body optionnel:**
```json
{
    "task_type": "required",
    "priority": "normal|low|high|critical",
    "description": "string",
    "context_data": {},
    "scheduled_for": "2024-12-25T09:00:00Z",
    "max_retries": 3,
    "timeout_minutes": 60
}
```

**Réponse 201:**
```json
{
    "id": 124,
    "task_id": "task_xyz789abc",
    "task_type": "content_optimization",
    "status": "pending",
    "priority": "normal",
    "description": "Optimiser 10 pages pour nouveaux mots-clés",
    "progress_percentage": 0,
    "brand": {
        "id": 9,
        "name": "Humari"
    },
    "created_by": {
        "id": 1,
        "username": "martin"
    },
    "created_at": "2024-12-20T16:00:00Z",
    "context_data": {
        "page_ids": [1, 2, 3, 4, 5],
        "target_keywords": ["marketing digital", "seo technique"],
        "optimization_level": "advanced"
    }
}
```

### Détail d'une Tâche
```http
GET /tasks/{id}/
```

**Réponse 200:** Même structure que la liste, mais objet unique avec plus de détails.

### Mettre à Jour une Tâche
```http
PUT /tasks/{id}/
PATCH /tasks/{id}/
```

**Body PATCH (champs modifiables):**
```json
{
    "priority": "high",
    "description": "Description mise à jour",
    "context_data": {
        "additional_params": "new_value"
    }
}
```

### Supprimer une Tâche
```http
DELETE /tasks/{id}/
```

**Réponse 204:** No Content

---

## 🔄 Actions Spéciales

### Retry d'une Tâche
```http
POST /tasks/{id}/retry/
```

**Body optionnel:**
```json
{
    "reset_progress": true,
    "clear_errors": true,
    "new_priority": "high"
}
```

**Réponse 200:**
```json
{
    "message": "Task queued for retry",
    "task_id": "task_xyz789abc", 
    "new_status": "pending",
    "retry_count": 2,
    "max_retries": 3,
    "estimated_start": "2024-12-20T16:05:00Z"
}
```

### Annuler une Tâche
```http
POST /tasks/{id}/cancel/
```

**Réponse 200:**
```json
{
    "message": "Task cancelled successfully",
    "task_id": "task_xyz789abc",
    "previous_status": "running",
    "cancelled_at": "2024-12-20T16:10:00Z"
}
```

### Statistiques des Queues
```http
GET /tasks/queue-stats/
```

**Réponse 200:**
```json
{
    "total_tasks": 1250,
    "queues": {
        "critical": {
            "pending": 2,
            "running": 1,
            "total_today": 5
        },
        "high": {
            "pending": 8,
            "running": 3,
            "total_today": 45
        },
        "normal": {
            "pending": 25,
            "running": 12,
            "total_today": 180
        },
        "low": {
            "pending": 15,
            "running": 5,
            "total_today": 95
        }
    },
    "status_distribution": {
        "pending": 50,
        "running": 21,
        "completed": 1150,
        "failed": 25,
        "cancelled": 4
    },
    "avg_processing_time_minutes": {
        "critical": 2.5,
        "high": 8.2,
        "normal": 15.7,
        "low": 45.3
    }
}
```

### Statistiques par Type de Tâche
```http
GET /tasks/type-stats/
```

**Réponse 200:**
```json
{
    "task_types": {
        "seo_keyword_analysis": {
            "total": 450,
            "completed": 420,
            "failed": 15,
            "avg_duration_minutes": 12.5,
            "success_rate": 93.3
        },
        "content_optimization": {
            "total": 280,
            "completed": 265,
            "failed": 8,
            "avg_duration_minutes": 25.8,
            "success_rate": 94.6
        },
        "ai_content_generation": {
            "total": 180,
            "completed": 170,
            "failed": 10,
            "avg_duration_minutes": 8.2,
            "success_rate": 94.4
        }
    }
}
```

---

## 📊 Exemples de Filtrage Avancé

### Tâches par Statut et Priorité
```http
GET /tasks/?status=running,pending&priority=high,critical
```

### Tâches Récentes avec Erreurs
```http
GET /tasks/?status=failed&created_after=2024-12-01T00:00:00Z&ordering=-created_at
```

### Tâches SEO du Mois
```http
GET /tasks/?task_type__startswith=seo&created_after=2024-12-01T00:00:00Z
```

### Recherche Textuelle
```http
GET /tasks/?search=keyword%20analysis
```

---

## 🚨 Gestion d'Erreurs

### Erreurs de Validation
```json
{
    "detail": "Validation failed",
    "field_errors": {
        "task_type": ["Ce champ est requis"],
        "priority": ["Valeur invalide. Choix: low, normal, high, critical"]
    }
}
```

### Erreurs de Permissions
```json
{
    "detail": "You do not have permission to access this task",
    "error_code": "PERMISSION_DENIED"
}
```

### Erreurs de Logique Métier
```json
{
    "detail": "Cannot retry a completed task",
    "error_code": "INVALID_OPERATION",
    "current_status": "completed",
    "allowed_statuses": ["failed", "cancelled"]
}
```

---

## 📈 Types de Tâches Supportés

### SEO & Recherche
- `seo_keyword_analysis` - Analyse de mots-clés
- `seo_competitor_analysis` - Analyse concurrentielle
- `seo_content_audit` - Audit de contenu

### Contenu & IA
- `ai_content_generation` - Génération de contenu IA
- `content_optimization` - Optimisation de contenu
- `meta_tags_generation` - Génération de méta-tags

### Site Web & Pages
- `website_structure_analysis` - Analyse structure site
- `page_performance_audit` - Audit performance pages
- `sitemap_generation` - Génération sitemap

### Données & Export
- `data_export` - Export de données
- `report_generation` - Génération de rapports
- `bulk_operations` - Opérations en masse

---

## 🔗 Intégration avec Autres Apps

### Relations OneToOne Automatiques
```json
{
    "base_task": {
        "id": 123,
        "task_type": "seo_analysis"
    },
    "metrics": {
        "execution_time_ms": 4500,
        "memory_usage_mb": 128
    },
    "persistent_job": {
        "progress_percentage": 75,
        "can_resume": true
    }
}
```

### Extensions Disponibles
- **TaskMetrics** (task_monitoring) - Métriques de performance
- **PersistentJob** (task_persistence) - Jobs resumables
- **PeriodicTask** (task_scheduling) - Tâches périodiques

---

**Documentation mise à jour** : 2024-12-20 ✅
