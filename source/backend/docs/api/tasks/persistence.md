# 💾 Task Persistence API - Jobs Persistants & Reprise

## Vue d'Ensemble
Le module `task_persistence` gère les tâches longues qui peuvent être interrompues et reprises, avec un système de checkpoints pour sauvegarder l'état de progression.

**Base URL**: `/tasks/persistent-jobs/`

---

## 🔑 Authentification
```bash
Authorization: Bearer {jwt_token}
X-Brand-ID: {brand_id}
```

---

## 💾 PersistentJob - Jobs Persistants

### Liste des Jobs Persistants
```http
GET /tasks/persistent-jobs/persistent-jobs/
```

**Filtres disponibles:**
```
?base_task=123
?can_resume=true
?status=pending,running,paused,completed,failed
?current_step=initialization,processing,finalization
?progress_gte=50
?progress_lte=90
?has_checkpoints=true
?created_after=2024-12-01T00:00:00Z
?ordering=-created_at,progress_percentage
```

**Réponse 200:**
```json
{
    "count": 45,
    "results": [
        {
            "id": 78,
            "base_task": {
                "id": 123,
                "task_id": "task_abc123def",
                "task_type": "bulk_content_analysis",
                "status": "running",
                "priority": "normal"
            },
            "job_data": {
                "total_pages": 500,
                "processed_pages": 375,
                "target_pages": [1, 2, 3, "...500"],
                "analysis_config": {
                    "include_seo_analysis": true,
                    "include_content_quality": true,
                    "depth": "full"
                }
            },
            "current_step": "content_analysis",
            "total_steps": 5,
            "progress_percentage": 75,
            "can_resume": true,
            "last_checkpoint_at": "2024-12-20T16:15:00Z",
            "checkpoints_count": 8,
            "estimated_completion": "2024-12-20T17:30:00Z",
            "created_at": "2024-12-20T14:00:00Z",
            "updated_at": "2024-12-20T16:15:00Z"
        }
    ]
}
```

### Créer un Job Persistant
```http
POST /tasks/persistent-jobs/persistent-jobs/
```

**Body:**
```json
{
    "base_task": 123,
    "job_data": {
        "total_pages": 1000,
        "processed_pages": 0,
        "target_pages": [1, 2, 3, "... jusqu'à 1000"],
        "analysis_config": {
            "include_seo_analysis": true,
            "include_keyword_analysis": true,
            "include_competitor_analysis": false,
            "output_format": "detailed"
        },
        "batch_size": 50,
        "max_concurrent": 5
    },
    "current_step": "initialization",
    "total_steps": 6,
    "can_resume": true
}
```

**Réponse 201:**
```json
{
    "id": 79,
    "base_task": {
        "id": 123,
        "task_id": "task_new456def"
    },
    "job_data": {...},
    "current_step": "initialization",
    "total_steps": 6,
    "progress_percentage": 0,
    "can_resume": true,
    "checkpoints_count": 0,
    "created_at": "2024-12-20T16:30:00Z"
}
```

### Détail d'un Job Persistant
```http
GET /tasks/persistent-jobs/persistent-jobs/{id}/
```

**Réponse 200:** Structure complète avec checkpoints récents et état détaillé.

---

## 🔄 Actions de Contrôle des Jobs

### Reprendre un Job
```http
POST /tasks/persistent-jobs/persistent-jobs/{id}/resume/
```

**Body optionnel:**
```json
{
    "from_checkpoint": "step_3_checkpoint_2",
    "reset_current_step": false,
    "priority_boost": "high"
}
```

**Réponse 200:**
```json
{
    "message": "Job resumed successfully",
    "job_id": 78,
    "resumed_from": "step_3_checkpoint_2",
    "current_step": "content_analysis",
    "progress_percentage": 60,
    "estimated_completion": "2024-12-20T18:00:00Z",
    "resumed_at": "2024-12-20T16:45:00Z"
}
```

### Pauser un Job
```http
POST /tasks/persistent-jobs/persistent-jobs/{id}/pause/
```

**Réponse 200:**
```json
{
    "message": "Job paused successfully",
    "job_id": 78,
    "paused_at": "2024-12-20T16:50:00Z",
    "current_progress": 75,
    "checkpoint_created": true,
    "can_resume": true
}
```

### Redémarrer un Job
```http
POST /tasks/persistent-jobs/persistent-jobs/{id}/restart/
```

**Body optionnel:**
```json
{
    "preserve_checkpoints": true,
    "reset_progress": false,
    "from_step": "initialization"
}
```

---

## 🔍 Jobs Resumables

### Liste des Jobs Resumables
```http
GET /tasks/persistent-jobs/persistent-jobs/resumable/
```

**Filtres spéciaux:**
```
?priority=high,critical
?interrupted_before=2024-12-20T12:00:00Z
?progress_gte=25
?has_recent_checkpoint=true
```

**Réponse 200:**
```json
{
    "resumable_jobs": 12,
    "jobs": [
        {
            "id": 75,
            "base_task": {
                "task_id": "task_interrupted_123",
                "task_type": "bulk_seo_audit"
            },
            "progress_percentage": 65,
            "last_checkpoint": {
                "step_name": "page_analysis_batch_13",
                "created_at": "2024-12-20T11:45:00Z",
                "checkpoint_data": {
                    "processed_batches": 13,
                    "current_batch_progress": 0.8
                }
            },
            "interruption_reason": "worker_restart",
            "estimated_resume_time_minutes": 5,
            "priority": "high"
        }
    ],
    "recommendations": [
        "Resume job_75 first (high priority, 65% complete)",
        "Jobs interrupted > 4h ago may need data refresh"
    ]
}
```

### Auto-Resume des Jobs
```http
POST /tasks/persistent-jobs/persistent-jobs/auto-resume/
```

**Body optionnel:**
```json
{
    "max_jobs": 5,
    "priority_threshold": "normal",
    "min_progress_percentage": 10,
    "max_interruption_hours": 24
}
```

**Réponse 200:**
```json
{
    "resumed_jobs": 3,
    "skipped_jobs": 2,
    "results": [
        {
            "job_id": 75,
            "status": "resumed",
            "message": "Successfully resumed from checkpoint"
        },
        {
            "job_id": 76,
            "status": "skipped",
            "reason": "Interrupted > 24h ago, needs manual review"
        }
    ]
}
```

---

## 📍 JobCheckpoint - Points de Sauvegarde

### Liste des Checkpoints
```http
GET /tasks/persistent-jobs/checkpoints/
```

**Filtres:**
```
?persistent_job=78
?step_name=content_analysis
?created_after=2024-12-20T10:00:00Z
?has_large_data=true
?ordering=-created_at
```

**Réponse 200:**
```json
{
    "count": 25,
    "results": [
        {
            "id": 156,
            "persistent_job": {
                "id": 78,
                "base_task_id": 123
            },
            "step_name": "content_analysis_batch_8",
            "checkpoint_data": {
                "processed_pages": 400,
                "current_batch": 8,
                "batch_progress": 0.6,
                "processed_batches": [1, 2, 3, 4, 5, 6, 7],
                "failed_pages": [45, 123, 289],
                "analysis_results": {
                    "avg_seo_score": 7.2,
                    "issues_found": 156,
                    "optimizations_suggested": 89
                },
                "next_batch_start": 401,
                "estimated_remaining_time_minutes": 45
            },
            "data_size_bytes": 245760,
            "created_at": "2024-12-20T16:15:00Z"
        }
    ]
}
```

### Créer un Checkpoint
```http
POST /tasks/persistent-jobs/checkpoints/
```

**Body:**
```json
{
    "persistent_job": 78,
    "step_name": "manual_checkpoint_before_critical_step",
    "checkpoint_data": {
        "current_state": "ready_for_finalization",
        "processed_items": 475,
        "remaining_items": 25,
        "intermediate_results": {
            "total_issues": 234,
            "critical_issues": 12,
            "optimizations_ready": 89
        },
        "notes": "Checkpoint avant étape critique de finalisation"
    }
}
```

### Détail d'un Checkpoint
```http
GET /tasks/persistent-jobs/checkpoints/{id}/
```

**Réponse 200:** Structure complète avec données de checkpoint et contexte du job.

---

## 📊 JobState - État Détaillé des Jobs

### État d'un Job
```http
GET /tasks/persistent-jobs/job-states/?persistent_job=78
```

**Réponse 200:**
```json
{
    "count": 1,
    "results": [
        {
            "id": 45,
            "persistent_job": {
                "id": 78,
                "current_step": "content_analysis"
            },
            "pages_status": {
                "page_1": "completed",
                "page_2": "completed", 
                "page_3": "in_progress",
                "page_4": "pending",
                "page_5": "failed",
                "page_6": "retrying"
            },
            "error_details": [
                {
                    "page_id": 5,
                    "error": "Timeout during content analysis",
                    "timestamp": "2024-12-20T16:10:00Z",
                    "retry_count": 2
                }
            ],
            "retry_count": 1,
            "max_retries": 3,
            "last_error_message": "Timeout during content analysis for page 5",
            "can_retry": true,
            "state_data": {
                "current_batch": 8,
                "batch_size": 50,
                "failed_pages_count": 3,
                "retry_queue": [5, 12, 27]
            },
            "updated_at": "2024-12-20T16:15:00Z"
        }
    ]
}
```

---

## 🧹 Maintenance et Nettoyage

### Nettoyage des Anciens Jobs
```http
POST /tasks/persistent-jobs/persistent-jobs/cleanup-old/
```

**Body:**
```json
{
    "days_old": 30,
    "preserve_failed": true,
    "preserve_with_checkpoints": true,
    "dry_run": false
}
```

**Réponse 200:**
```json
{
    "cleanup_summary": {
        "jobs_reviewed": 150,
        "jobs_deleted": 45,
        "jobs_preserved": 105,
        "checkpoints_deleted": 234,
        "storage_freed_mb": 156.7
    },
    "preserved_reasons": {
        "failed_jobs": 25,
        "recent_jobs": 60,
        "has_checkpoints": 20
    },
    "deleted_job_types": {
        "completed_old": 30,
        "cancelled_old": 15
    }
}
```

### Optimisation du Stockage
```http
POST /tasks/persistent-jobs/checkpoints/optimize-storage/
```

**Body optionnel:**
```json
{
    "compress_old_checkpoints": true,
    "days_old_threshold": 7,
    "max_checkpoints_per_job": 20
}
```

**Réponse 200:**
```json
{
    "optimization_results": {
        "checkpoints_compressed": 45,
        "storage_saved_mb": 89.3,
        "old_checkpoints_archived": 12,
        "total_checkpoints_processed": 156
    }
}
```

---

## 📈 Statistiques et Monitoring

### Statistiques de Persistence
```http
GET /tasks/persistent-jobs/persistent-jobs/stats/
```

**Paramètres:**
```
?days=30
?include_trends=true
```

**Réponse 200:**
```json
{
    "period": "last_30_days",
    "totals": {
        "persistent_jobs_created": 145,
        "jobs_completed": 120,
        "jobs_failed": 8,
        "jobs_resumed": 23,
        "checkpoints_created": 567,
        "avg_completion_time_hours": 2.8
    },
    "resume_stats": {
        "successful_resumes": 21,
        "failed_resumes": 2,
        "avg_resume_time_minutes": 3.5,
        "resume_success_rate": 91.3
    },
    "checkpoint_stats": {
        "avg_checkpoints_per_job": 3.9,
        "avg_checkpoint_size_kb": 45.7,
        "most_checkpointed_step": "content_analysis"
    },
    "failure_analysis": {
        "timeout_failures": 3,
        "memory_failures": 2,
        "network_failures": 1,
        "other_failures": 2
    }
}
```

---

## 🔧 Configuration Avancée

### Validation de Configuration Job
```http
POST /tasks/persistent-jobs/persistent-jobs/validate-config/
```

**Body:**
```json
{
    "job_data": {
        "total_pages": 10000,
        "batch_size": 100,
        "max_concurrent": 10
    },
    "estimated_duration_hours": 8,
    "checkpoint_frequency": "every_batch"
}
```

**Réponse 200:**
```json
{
    "valid": true,
    "recommendations": [
        "Consider reducing batch_size to 50 for better checkpoint granularity",
        "Estimated memory usage: ~2GB per worker"
    ],
    "warnings": [
        "Job duration > 6h, ensure adequate checkpoint strategy"
    ],
    "estimated_checkpoints": 100,
    "estimated_storage_mb": 245
}
```

---

**Documentation mise à jour** : 2024-12-20 ✅
