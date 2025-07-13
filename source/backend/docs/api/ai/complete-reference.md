# 📋 AI Infrastructure - Référence Complète des Endpoints (O3 Support)

## Vue d'Ensemble

Cette référence complète liste **tous les endpoints** de l'infrastructure AI MEGAHUB avec support **O3/GPT-4.1** et leurs paramètres exacts, réponses et codes d'erreur. Organisée par app pour une navigation optimale.

---

## 🎯 AI_CORE - Hub Central

### AIJobType Endpoints

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/ai/job-types/` | Liste types de jobs disponibles | JWT |
| GET | `/ai/job-types/{id}/` | Détail d'un type de job | JWT |

### AIJob Endpoints

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/ai/jobs/` | Liste jobs IA avec filtres | JWT + Brand |
| POST | `/ai/jobs/` | Créer nouveau job IA | JWT + Brand |
| GET | `/ai/jobs/{id}/` | Détail job avec extensions | JWT + Brand |
| PUT | `/ai/jobs/{id}/` | Modifier job IA | JWT + Brand |
| DELETE | `/ai/jobs/{id}/` | Supprimer job IA | JWT + Brand |

### Actions Spécialisées

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/ai/jobs/dashboard/` | Dashboard central IA | JWT + Brand |
| GET | `/ai/jobs/by_status/` | Jobs par statut | JWT + Brand |
| POST | `/ai/jobs/{id}/cancel/` | Annuler job | JWT + Brand |

#### Paramètres POST `/ai/jobs/`
```json
{
  "job_type": "chat_completion",       // REQUIS
  "priority": "normal",                // low, normal, high, urgent
  "description": "Description du job", // OPTIONNEL
  "input_data": {                      // REQUIS
    "messages": [...],
    "model": "o3",                     // 🆕 Support O3/GPT-4.1
    "reasoning_effort": "high"         // 🆕 Pour O3
  }
}
```

#### Filtres GET `/ai/jobs/`
```
?status=completed              # pending, running, completed, failed, cancelled
?priority=high                 # low, normal, high, urgent
?job_type=chat_completion     # Nom du job type
?created_by=1                 # ID utilisateur
?is_async=true                # true/false
?progress_percentage__gte=50  # 0-100
?created_at__gte=2024-01-01   # Date ISO
?search=keyword               # Recherche textuelle
?model=o3                     # 🆕 Filtre par modèle IA
```

---

## 🔌 AI_PROVIDERS - Providers & Credentials

### AIProvider Endpoints

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/ai/providers/` | Liste providers disponibles | JWT |
| GET | `/ai/providers/{id}/` | Détail provider | JWT |

### AICredentials Endpoints

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/ai/credentials/` | Credentials company | JWT + Company |
| POST | `/ai/credentials/` | Créer/modifier credentials | JWT + Company |
| PUT | `/ai/credentials/{id}/` | Modifier credentials | JWT + Company |
| DELETE | `/ai/credentials/{id}/` | Supprimer credentials | JWT + Company |

### Actions Spécialisées

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/ai/credentials/quota_status/` | Statut quota provider | JWT + Company |
| POST | `/ai/credentials/test_connection/` | Tester connexion | JWT + Company |

#### Paramètres POST `/ai/credentials/`
```json
{
  "openai_api_key": "sk-proj-...",      // OPTIONNEL
  "anthropic_api_key": "sk-ant-...",    // OPTIONNEL
  "google_api_key": "AIza...",          // OPTIONNEL
  "use_global_fallback": false          // OPTIONNEL
}
```

#### Paramètres GET `/ai/credentials/quota_status/`
```
?provider=openai    // REQUIS: openai, anthropic, google
```

#### Paramètres POST `/ai/credentials/test_connection/`
```json
{
  "provider": "openai"    // REQUIS
}
```

---

## 🟢 AI_OPENAI - OpenAI Integration (O3 Enhanced)

### OpenAIJob Endpoints

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/ai/openai/jobs/` | Jobs OpenAI avec métriques | JWT + Brand |
| POST | `/ai/openai/jobs/` | Créer job OpenAI direct | JWT + Brand |
| GET | `/ai/openai/jobs/{id}/` | Détail job OpenAI | JWT + Brand |
| PUT | `/ai/openai/jobs/{id}/` | Modifier job OpenAI | JWT + Brand |
| DELETE | `/ai/openai/jobs/{id}/` | Supprimer job OpenAI | JWT + Brand |

### Chat Completions (Multi-Modèles)

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/ai/openai/chat/` | Créer chat completion | JWT + Brand |
| GET | `/ai/openai/chat/` | Modèles disponibles avec specs | JWT + Brand |

### Résultats

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/ai/openai/completion/job_result/` | Résultat job | JWT + Brand |

#### Paramètres POST `/ai/openai/chat/` - Universal

**Paramètres Communs (Tous Modèles)** :
```json
{
  "messages": [                           // REQUIS
    {"role": "user", "content": "..."}
  ],
  "model": "o3",                         // 🆕 o3, o3-mini, gpt-4.1, gpt-4o
  "description": "Description",          // OPTIONNEL
  "tools": [                             // OPTIONNEL
    {"type": "file_search"}
  ],
  "tool_resources": {                    // OPTIONNEL
    "file_search": {
      "vector_store_ids": ["vs_123"]
    }
  }
}
```

**Paramètres Spécifiques O3** :
```json
{
  "model": "o3",                         // ou "o3-mini"
  "reasoning_effort": "high",            // 🆕 REQUIS: low, medium, high
  "max_completion_tokens": 2000,         // 🆕 Au lieu de max_tokens
  "response_format": {"type": "text"}
  // ❌ temperature NON supportée pour O3
}
```

**Paramètres Spécifiques GPT-4.1** :
```json
{
  "model": "gpt-4.1",
  "temperature": 1.0,                    // Défaut plus créatif
  "max_completion_tokens": 10000,        // 🆕 Limite élevée
  "top_p": 1,
  "frequency_penalty": 0,
  "presence_penalty": 0
}
```

**Paramètres Legacy (GPT-4o, etc.)** :
```json
{
  "model": "gpt-4o",
  "temperature": 0.7,                    // Défaut équilibré
  "max_tokens": 1000,                    // Format classique
  "tools": [...],
  "response_format": {...}
}
```

#### Réponse POST `/ai/openai/chat/` - Enhanced

**Réponse O3 Completion** :
```json
{
  "job_id": "ai_job_abc123",
  "status": "completed",
  "result": {
    "completion": "Analyse détaillée...",
    "finish_reason": "stop"
  },
  "usage": {
    "prompt_tokens": 125,
    "completion_tokens": 275,
    "total_tokens": 400,
    "cost_usd": "0.008000"              // 🆕 Coût O3 plus élevé
  },
  "model": "o3",
  "generation": "new",                  // 🆕 new/legacy
  "reasoning_effort": "high",           // 🆕 Effort utilisé
  "execution_time_ms": 5200,            // 🆕 Plus lent mais meilleur
  "quality_indicators": {               // 🆕 Métriques qualité O3
    "reasoning_steps": 47,
    "confidence_score": 0.95
  }
}
```

**Réponse Asynchrone** :
```json
{
  "job_id": "ai_job_def456",
  "status": "async",
  "task_id": "celery-task-789",
  "message": "Job started asynchronously with o3",
  "estimated_completion": "2024-12-20T15:05:00Z",
  "reasoning_effort": "high"            // 🆕 Pour estimation temps
}
```

#### Réponse GET `/ai/openai/chat/` - Models Enhanced

**Réponse Modèles avec Spécificités** :
```json
{
  "models": [
    {
      "id": "o3",
      "name": "O3",
      "description": "Modèle de raisonnement avancé",
      "generation": "new",              // 🆕 Indicateur génération
      "supports_reasoning": true,       // 🆕 Capacités spéciales
      "supports_temperature": false,    // 🆕 Limitations
      "input_cost_per_token": 0.000020,
      "output_cost_per_token": 0.000020,
      "context_window": 200000,
      "recommended_for": ["analysis", "reasoning", "complex_tasks"],
      "default_params": {               // 🆕 Paramètres recommandés
        "reasoning_effort": "medium",
        "max_completion_tokens": 1000
      },
      "performance_profile": {          // 🆕 Profil performance
        "speed": "slow",
        "quality": "highest",
        "cost": "high"
      }
    },
    {
      "id": "o3-mini",
      "name": "O3 Mini",
      "description": "O3 optimisé coût/performance",
      "generation": "new",
      "supports_reasoning": true,
      "supports_temperature": false,
      "input_cost_per_token": 0.000005,
      "output_cost_per_token": 0.000005,
      "recommended_for": ["simple_reasoning", "cost_optimization"],
      "performance_profile": {
        "speed": "medium",
        "quality": "high",
        "cost": "medium"
      }
    },
    {
      "id": "gpt-4.1",
      "name": "GPT-4.1",
      "description": "GPT-4 enhanced",
      "generation": "new",
      "supports_reasoning": false,
      "supports_temperature": true,
      "input_cost_per_token": 0.000004,
      "output_cost_per_token": 0.000004,
      "context_window": 200000,
      "recommended_for": ["creative", "large_context"],
      "default_params": {
        "temperature": 1.0,
        "max_completion_tokens": 10000
      },
      "performance_profile": {
        "speed": "fast",
        "quality": "high",
        "cost": "medium"
      }
    }
  ],
  "generation_info": {                  // 🆕 Info par génération
    "new": {
      "models": ["o3", "o3-mini", "gpt-4.1"],
      "features": ["structured_messages", "max_completion_tokens"],
      "limitations": ["no_temperature_for_o3"]
    },
    "legacy": {
      "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
      "features": ["temperature", "max_tokens", "proven_stability"]
    }
  },
  "selection_guide": {                  // 🆕 Guide de sélection
    "complex_analysis": "o3",
    "cost_effective_reasoning": "o3-mini",
    "creative_content": "gpt-4.1",
    "general_purpose": "gpt-4o"
  }
}
```

#### Filtres GET `/ai/openai/jobs/` - Extended
```
?model=o3                      # 🆕 Filtrer par modèle
?generation=new                # 🆕 new/legacy
?reasoning_effort=high         # 🆕 Effort de raisonnement
?temperature__gte=0.5          # Température minimum (legacy)
?total_tokens__gte=1000        # Tokens minimum
?has_tools=true                # Avec outils
?assistant_id=asst_123         # Par assistant
?ai_job__status=completed      # Status job central
?cost_usd__gte=1.00           # 🆕 Filtrer par coût
```

---

## 📊 AI_USAGE - Usage & Alertes (O3 Enhanced)

### AIJobUsage Endpoints

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/ai/usage/` | Usage détaillé avec filtres | JWT + Brand |
| POST | `/ai/usage/` | Enregistrer usage manuel | JWT + Brand |
| GET | `/ai/usage/{id}/` | Détail usage | JWT + Brand |

### Dashboards & Analytics

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/ai/usage/dashboard/` | Dashboard usage principal | JWT + Brand |
| GET | `/ai/usage/cost_breakdown/` | Breakdown coûts détaillé | JWT + Brand |
| GET | `/ai/usage/model_comparison/` | 🆕 Comparaison modèles | JWT + Brand |
| GET | `/ai/usage/performance/` | Métriques performance | JWT + Brand |
| GET | `/ai/usage/export/` | Export CSV/Excel | JWT + Brand |

### AIUsageAlert Endpoints

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/ai/alerts/` | Liste alertes | JWT + Company |
| POST | `/ai/alerts/` | Créer alerte manuelle | JWT + Company |
| GET | `/ai/alerts/{id}/` | Détail alerte | JWT + Company |
| PUT | `/ai/alerts/{id}/resolve/` | Résoudre alerte | JWT + Company |

### Actions Alertes

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/ai/alerts/active/` | Alertes actives | JWT + Company |
| POST | `/ai/alerts/check_alerts/` | Vérifier nouvelles alertes | JWT + Company |

#### Filtres GET `/ai/usage/` - Enhanced
```
?provider_name=openai              # Provider
?model_name=o3                     # 🆕 Modèle spécifique
?generation=new                    # 🆕 Génération de modèle
?total_cost__gte=1.00             # Coût minimum
?execution_time_seconds__gte=60   # Durée minimum
?success_rate__lt=1.0             # Échecs uniquement
?created_at__gte=2024-12-01       # Période
?ai_job__status=completed         # Status job
?ai_job__brand=9                  # Par brand
?reasoning_effort=high            # 🆕 Effort O3
?cost_efficiency__gte=0.8         # 🆕 Efficacité coût
```

#### Paramètres GET `/ai/usage/dashboard/` - Enhanced
```
?days=7           // OPTIONNEL: Période (défaut 30)
?brand_id=9       // OPTIONNEL: Filtrer par brand
?model=o3         // 🆕 OPTIONNEL: Filtrer par modèle
?generation=new   // 🆕 OPTIONNEL: Filtrer par génération
```

#### 🆕 GET `/ai/usage/model_comparison/`
**Comparaison Performance Modèles**

**Paramètres** :
```
?models=o3,o3-mini,gpt-4o     // Modèles à comparer
?days=30                      // Période d'analyse
?metric=cost_efficiency       // Métrique principale
```

**Réponse** :
```json
{
  "comparison_period": "30 days",
  "models_analyzed": ["o3", "o3-mini", "gpt-4o"],
  "metrics_comparison": [
    {
      "model": "o3",
      "generation": "new",
      "jobs_count": 89,
      "avg_cost_per_job": "0.156",
      "avg_execution_time": 5.2,
      "success_rate": 0.996,
      "quality_score": 9.8,        // 🆕 Score qualité
      "cost_efficiency": 0.89,     // 🆕 Efficacité
      "recommended_for": ["complex_analysis", "research"],
      "performance_profile": {
        "reasoning_quality": 9.8,
        "speed": 6.2,
        "cost_effectiveness": 7.1
      }
    },
    {
      "model": "o3-mini", 
      "generation": "new",
      "jobs_count": 156,
      "avg_cost_per_job": "0.045",
      "avg_execution_time": 3.1,
      "success_rate": 0.992,
      "quality_score": 8.9,
      "cost_efficiency": 0.94,
      "recommended_for": ["standard_reasoning", "cost_optimization"],
      "performance_profile": {
        "reasoning_quality": 8.9,
        "speed": 8.1,
        "cost_effectiveness": 9.4
      }
    }
  ],
  "recommendations": {
    "most_cost_effective": "o3-mini",
    "highest_quality": "o3",
    "best_balance": "o3-mini",
    "fastest": "gpt-4o"
  },
  "usage_optimization": {
    "simple_tasks": "gpt-4o",
    "reasoning_tasks": "o3-mini", 
    "complex_analysis": "o3",
    "creative_content": "gpt-4.1"
  }
}
```

---

## 🚨 Gestion d'Erreurs Enhanced (O3 Support)

### Codes de Réponse Standards (Inchangés)

### Erreurs Spécifiques O3/GPT-4.1

#### Erreurs de Paramètres Modèle
```json
// Temperature sur O3
{
  "detail": "O3 models don't support temperature parameter",
  "error_code": "INVALID_PARAMETER_FOR_MODEL",
  "model": "o3",
  "invalid_params": ["temperature"],
  "suggested_params": ["reasoning_effort", "max_completion_tokens"],
  "model_requirements": {
    "required": ["reasoning_effort"],
    "forbidden": ["temperature"],
    "optional": ["max_completion_tokens", "tools"]
  }
}

// Reasoning effort sur legacy
{
  "detail": "Model gpt-4o doesn't support reasoning_effort parameter",
  "error_code": "INVALID_PARAMETER_FOR_MODEL", 
  "model": "gpt-4o",
  "invalid_params": ["reasoning_effort"],
  "suggested_params": ["temperature", "max_tokens"],
  "model_requirements": {
    "required": [],
    "forbidden": ["reasoning_effort"],
    "optional": ["temperature", "max_tokens", "tools"]
  }
}
```

#### Erreurs de Coût O3
```json
// Coût O3 élevé
{
  "detail": "Estimated cost exceeds budget limits for O3 model",
  "error_code": "COST_LIMIT_EXCEEDED",
  "model": "o3",
  "estimated_cost": "5.67",
  "daily_budget_remaining": "2.34",
  "suggestions": [
    "Use o3-mini for cost optimization",
    "Reduce max_completion_tokens",
    "Use reasoning_effort='low'"
  ]
}
```

#### Erreurs de Quota Spécifiques
```json
// Quota reasoning O3
{
  "detail": "Daily reasoning quota exceeded for O3",
  "error_code": "REASONING_QUOTA_EXCEEDED",
  "model": "o3",
  "daily_reasoning_jobs": 50,
  "daily_limit": 50,
  "reset_time": "2024-12-21T00:00:00Z",
  "alternatives": ["o3-mini", "gpt-4.1"]
}
```

---

## 📊 Pagination Standards (Inchangés)

### Paramètres de Pagination
```
?page=2           # Numéro de page (défaut: 1)
?page_size=50     # Items par page (défaut: 25, max: 100)
```

---

## 🔍 Recherche et Filtres Enhanced

### Patterns de Filtrage (Enrichis)

#### Filtres Spécifiques O3
```
?model__startswith=o3         # Tous modèles O3
?reasoning_effort=high        # 🆕 Effort de raisonnement
?generation=new               # 🆕 Nouveaux modèles
?cost_usd__gte=1.00          # 🆕 Coût minimum
?quality_score__gte=9.0      # 🆕 Score qualité
```

#### Filtres Comparatifs
```
?model__in=o3,o3-mini,gpt-4o  # Comparaison modèles
?generation__in=new,legacy    # Par génération
?performance_tier=high        # Niveau performance
```

---

## 🔄 Tri et Ordering Enhanced

### Champs Triables Nouveaux

#### ai_openai.OpenAIJob (Enrichi)
- `reasoning_effort`, `max_completion_tokens`, `generation`
- `cost_usd`, `quality_score`, `reasoning_steps`
- `model`, `created_at`, `total_tokens`

#### ai_usage.AIJobUsage (Enrichi)
- `model_name`, `generation`, `reasoning_effort`
- `cost_efficiency`, `quality_score`
- `execution_time_seconds`, `total_cost`

### Tri Multi-Critères
```
?ordering=-cost_usd,quality_score      # Coût décroissant, qualité croissante
?ordering=generation,-created_at       # Génération puis date décroissante
?ordering=model,-execution_time        # Modèle puis rapidité
```

---

## 💡 Bonnes Pratiques API Enhanced

### Sélection de Modèle
1. **Analyser le task_complexity** avant sélection
2. **Considérer budget_constraints** pour O3
3. **Utiliser model_comparison** pour optimiser
4. **Monitoring cost_efficiency** continu

### Performance O3
1. **reasoning_effort='low'** pour tâches simples
2. **Batch processing** pour réduire coûts fixes
3. **Cache results** pour requêtes similaires
4. **Fallback strategy** : O3 → O3-mini → GPT-4o

### Monitoring Avancé
1. **Track par generation** pour analyser ROI
2. **Alert sur cost spikes** O3
3. **Quality metrics** pour justifier surcoût
4. **Usage patterns** pour optimisation continue

---

## 🆕 Nouveaux Endpoints Spécialisés

### Recommandations de Modèle

#### `POST /ai/openai/recommend_model/`
**Recommandation intelligente selon contexte**

**Paramètres** :
```json
{
  "task_description": "Analyser 50 pages de contenu SEO",
  "complexity_score": 0.9,        // 0.0-1.0
  "budget_constraint": 0.7,       // 0.0-1.0  
  "quality_requirement": 0.9,     // 0.0-1.0
  "speed_requirement": 0.3        // 0.0-1.0
}
```

**Réponse** :
```json
{
  "recommended_model": "o3",
  "confidence": 0.95,
  "reasoning": "High complexity and quality requirement favor O3",
  "alternatives": [
    {
      "model": "o3-mini",
      "trade_offs": "Lower cost but slightly reduced quality",
      "cost_savings": "65%"
    }
  ],
  "estimated_cost": "2.45",
  "estimated_time": "45 seconds"
}
```

---

**Cette référence complète couvre l'intégralité de l'API AI MEGAHUB avec support O3/GPT-4.1 natif. L'infrastructure auto-configure intelligemment selon le modèle, garantissant performances optimales et compatibilité totale.**