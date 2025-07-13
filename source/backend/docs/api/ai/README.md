# 🤖 MEGAHUB AI Infrastructure - API Documentation (O3 Ready)

## Vue d'Ensemble

L'infrastructure AI MEGAHUB est architecturée en **4 apps spécialisées** suivant le principe de responsabilité unique, permettant une gestion complète des jobs IA avec monitoring, quotas et **support natif O3/GPT-4.1**.

### 🚀 Nouveautés 2024
- ✅ **Support O3 complet** : Modèles de raisonnement avancé avec auto-configuration
- ✅ **GPT-4.1 Enhanced** : Version améliorée de GPT-4 avec contexte large
- ✅ **Auto-configuration intelligente** : Paramètres adaptés automatiquement selon le modèle
- ✅ **Cost optimization** : Recommandations intelligentes par complexité de tâche
- ✅ **Quality metrics** : Métriques de performance par génération
- ✅ **Model comparison** : Analytics comparatifs O3 vs legacy

### Base URLs
```
https://backoffice.humari.fr/ai/                 # Hub principal
https://backoffice.humari.fr/ai/providers/       # Providers et credentials
https://backoffice.humari.fr/ai/openai/          # OpenAI O3/GPT-4.1
https://backoffice.humari.fr/ai/usage/           # Usage et métriques
```

---

## 📁 Architecture des Apps

### 🎯 ai_core - Hub Central
**Responsabilité** : Hub central des jobs IA, types de jobs, statuts
- CRUD des jobs IA principales
- Types de jobs et catégories  
- Statuts et workflow de progression
- **Nouveau** : Support métadonnées O3/GPT-4.1
- Dashboard central avec métriques cross-providers

[📖 Documentation Complète](./core.md)

### 🔌 ai_providers - Providers & Quotas  
**Responsabilité** : Gestion providers, credentials sécurisées, quotas
- Providers IA disponibles (OpenAI, Anthropic, Google)
- Credentials chiffrées par company avec Fernet
- Quotas et limites par provider
- **Nouveau** : Quotas spécialisés O3 (coût élevé)
- Test de connexion et monitoring health

[📖 Documentation Complète](./providers.md)

### 🟢 ai_openai - OpenAI Integration (O3 Enhanced)
**Responsabilité** : Intégration spécialisée OpenAI multi-génération
- **Support O3/O3-mini** : Modèles de raisonnement avec `reasoning_effort`
- **Support GPT-4.1** : Version enhanced avec température créative
- **Auto-configuration** : Paramètres adaptés par modèle automatiquement
- **Cost tracking** : Coûts précis par génération avec alertes
- Chat completions unifiées et assistants avancés
- **Conversion intelligente** : Messages legacy → structured automatique

[📖 Documentation Complète](./openai.md)

### 📊 ai_usage - Usage & Alertes (Enhanced)
**Responsabilité** : Tracking usage, coûts, métriques, alertes
- Usage détaillé par job et provider avec précision 6 décimales
- **Nouveau** : Métriques qualité O3 vs legacy
- **Nouveau** : Comparaison performance modèles avec ROI
- Système d'alertes quota/budget enhanced
- Analytics et recommandations automatiques
- Export CSV/Excel avec filtres avancés

[📖 Documentation Complète](./usage.md)

---

## 🔑 Authentification

**Toutes les APIs** requièrent :
```bash
Authorization: Bearer {jwt_token}
X-Brand-ID: {brand_id}  # Scope automatique par brand
```

**Brand Middleware** : Le système utilise automatiquement `request.current_brand` depuis le middleware, plus besoin de gérer manuellement les headers de brand.

---

## 🚀 Quick Start O3

### 1. Chat Completion O3 Simple
```bash
POST /ai/openai/chat/
{
  "messages": [
    {"role": "user", "content": "Analyse ce contenu marketing de façon approfondie"}
  ],
  "model": "o3",
  "reasoning_effort": "high",
  "max_completion_tokens": 2000
}
```

### 2. O3-Mini pour Optimisation Coût
```bash
POST /ai/openai/chat/
{
  "messages": [
    {"role": "user", "content": "Résume cet article SEO"}
  ],
  "model": "o3-mini",
  "reasoning_effort": "medium",
  "max_completion_tokens": 500
}
```

### 3. GPT-4.1 pour Créativité
```bash
POST /ai/openai/chat/
{
  "messages": [
    {"role": "user", "content": "Écris un article de blog engageant sur l'IA"}
  ],
  "model": "gpt-4.1",
  "temperature": 1.0,
  "max_completion_tokens": 5000
}
```

### 4. Recommandation Automatique
```bash
POST /ai/openai/recommend_model/
{
  "task_description": "Analyser 20 pages de contenu technique",
  "complexity_score": 0.8,
  "budget_constraint": 0.6,
  "quality_requirement": 0.9
}
```

---

## 🎯 Endpoints Rapides

### Jobs IA de Base
```http
GET    /ai/jobs/                    # Liste tous les jobs IA
POST   /ai/jobs/                    # Créer nouveau job IA
GET    /ai/jobs/{id}/               # Détail job IA
POST   /ai/jobs/{id}/cancel/        # Annuler job
GET    /ai/jobs/dashboard/          # Dashboard jobs IA
GET    /ai/job-types/               # Types de jobs disponibles
```

### OpenAI O3/GPT-4.1
```http
GET    /ai/openai/chat/             # 🆕 Modèles avec spécificités
POST   /ai/openai/chat/             # 🆕 Chat universal multi-modèles
GET    /ai/openai/jobs/             # Jobs OpenAI avec métriques
GET    /ai/openai/completion/job_result/?job_id=xyz  # Résultat job
POST   /ai/openai/recommend_model/  # 🆕 Recommandation intelligente
```

### Usage & Analytics Enhanced
```http
GET    /ai/usage/dashboard/?days=7  # Dashboard usage
GET    /ai/usage/model_comparison/  # 🆕 Comparaison O3 vs legacy
GET    /ai/usage/cost_breakdown/    # Breakdown coûts détaillé
GET    /ai/usage/efficiency/        # 🆕 Analyse d'efficacité modèles
GET    /ai/usage/trends/            # 🆕 Tendances temporelles
GET    /ai/alerts/                  # Alertes usage
```

### Providers & Credentials
```http
GET    /ai/providers/               # Providers disponibles
GET    /ai/credentials/quota_status/?provider=openai  # Statut quota
POST   /ai/credentials/test_connection/  # Tester connexion
GET    /ai/providers/health/        # 🆕 Health check providers
```

---

## 📈 Workflow Typique O3

### 1. Analyse Complexe avec O3
```bash
# Étape 1: Créer job d'analyse
POST /ai/openai/chat/
{
  "model": "o3",
  "reasoning_effort": "high",
  "messages": [
    {
      "role": "developer", 
      "content": [{"type": "text", "text": "Tu es un expert SEO"}]
    },
    {
      "role": "user",
      "content": [{"type": "text", "text": "Analyse approfondie de ce site..."}]
    }
  ],
  "max_completion_tokens": 3000
}

# Étape 2: Suivre progression (si async)
GET /ai/jobs/{id}/

# Étape 3: Récupérer résultat
GET /ai/openai/completion/job_result/?job_id=ai_job_abc123
```

### 2. Optimisation Coût avec O3-Mini
```bash
# Même workflow mais modèle optimisé
POST /ai/openai/chat/
{
  "model": "o3-mini",
  "reasoning_effort": "medium",  # Plus rapide
  "max_completion_tokens": 1000  # Limité pour coût
}
```

### 3. Monitoring et Optimisation
```bash
# Analyser usage par modèle
GET /ai/usage/model_comparison/?models=o3,o3-mini,gpt-4o&days=30

# Vérifier coûts O3
GET /ai/usage/cost_breakdown/?model=o3

# Alertes budget
GET /ai/alerts/active/
```

---

## 🆕 Nouvelles Fonctionnalités

### Auto-Configuration Modèles
- **Détection automatique** : Legacy vs nouvelle génération
- **Paramètres optimaux** : Configurés selon le modèle
- **Conversion intelligente** : Messages et paramètres adaptés
- **Validation** : Erreurs claires sur paramètres incompatibles

### Métriques de Qualité
```json
{
  "model": "o3",
  "quality_indicators": {
    "reasoning_steps": 47,
    "confidence_score": 0.95,
    "complexity_handled": 0.92
  },
  "performance_profile": {
    "speed": "slow",
    "quality": "highest", 
    "cost": "high"
  }
}
```

### Recommandations Intelligentes
- **Sélection automatique** selon task complexity
- **Optimisation coût** avec alternatives
- **Benchmarks performance** par use case
- **ROI analysis** O3 vs modèles classiques

---

## 🔍 Filtres Avancés

### Filtres Cross-Apps
```http
# Jobs par statut et provider avec génération
GET /ai/jobs/?status=completed&openai_job__model=o3&openai_job__generation=new

# Usage par période et coût avec modèle spécifique
GET /ai/usage/?created_at__gte=2024-01-01&total_cost__gte=1.00&model_name=o3

# Jobs avec métriques spécifiques O3
GET /ai/jobs/?usage__execution_time_seconds__gte=60&openai_job__reasoning_effort=high
```

### Filtres Spécifiques O3
```http
# Jobs par génération
GET /ai/jobs/?openai_job__generation=new&openai_job__reasoning_effort=high

# Usage par coût et efficacité
GET /ai/usage/?model_name=o3&total_cost__gte=1.00&cost_efficiency__gte=0.8

# Comparaison performance
GET /ai/usage/?generation=new&quality_score__gte=9.0
```

### Recherche Multi-Critères
```http
GET /ai/openai/jobs/?generation=new&cost_usd__gte=0.5&quality_score__gte=9.0
GET /ai/usage/?search=analysis&model_name__in=o3,o3-mini,gpt-4.1
```

---

## 📊 Dashboard Enhanced

### Métriques O3 vs Legacy
```json
{
  "generation_comparison": {
    "new_models": {
      "models": ["o3", "o3-mini", "gpt-4.1"],
      "avg_quality": 9.2,
      "avg_cost": "0.087",
      "avg_execution_time": 4.8,
      "use_cases": ["complex_analysis", "reasoning", "creative_large_context"]
    },
    "legacy_models": {
      "models": ["gpt-4o", "gpt-4-turbo"],
      "avg_quality": 8.7,
      "avg_cost": "0.023",
      "avg_execution_time": 2.1,
      "use_cases": ["general", "speed_optimized", "cost_effective"]
    }
  },
  "recommendations": {
    "cost_optimization": "Use O3-mini for 80% reasoning tasks",
    "quality_premium": "Reserve O3 for complex analysis only",
    "balanced_approach": "GPT-4.1 for creative + large context",
    "default_choice": "GPT-4o for general purpose tasks"
  }
}
```

### Dashboard Usage avec O3
```json
{
  "period": {"days": 30},
  "totals": {
    "jobs": 1247,
    "cost": "456.78",
    "avg_cost_per_job": "0.367"
  },
  "by_generation": [
    {
      "generation": "new",
      "models": ["o3", "o3-mini", "gpt-4.1"],
      "jobs": 234,
      "cost": "298.45",
      "percentage": 65.3,
      "avg_quality": 9.1
    },
    {
      "generation": "legacy", 
      "models": ["gpt-4o", "gpt-4-turbo"],
      "jobs": 1013,
      "cost": "158.33",
      "percentage": 34.7,
      "avg_quality": 8.6
    }
  ],
  "efficiency_insights": {
    "most_cost_effective": "o3-mini",
    "highest_roi": "o3-mini",
    "premium_choice": "o3",
    "fastest": "gpt-4o"
  }
}
```

---

## 🚨 Gestion d'Erreurs Enhanced

### Codes de Statut Standards
- **200**: Succès
- **201**: Création réussie  
- **400**: Validation échouée (paramètres incompatibles)
- **401**: Non authentifié
- **403**: Permissions insuffisantes / Quota dépassé
- **404**: Ressource non trouvée
- **429**: Rate limit dépassé (O3 spécifique)
- **500**: Erreur serveur

### Erreurs Spécifiques O3
```json
// Temperature sur O3
{
  "error": "O3 models don't support temperature parameter",
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
  "error": "Model gpt-4o doesn't support reasoning_effort parameter",
  "error_code": "INVALID_PARAMETER_FOR_MODEL", 
  "model": "gpt-4o",
  "invalid_params": ["reasoning_effort"],
  "suggested_params": ["temperature", "max_tokens"]
}

// Budget O3 dépassé
{
  "error": "Estimated cost exceeds daily O3 budget limit",
  "error_code": "O3_BUDGET_EXCEEDED",
  "model": "o3",
  "estimated_cost": "5.67",
  "daily_budget_remaining": "2.34",
  "suggestions": [
    "Use o3-mini for cost optimization",
    "Reduce max_completion_tokens",
    "Use reasoning_effort='low'"
  ],
  "alternatives": ["o3-mini", "gpt-4.1"]
}

// Quota reasoning O3
{
  "error": "Daily reasoning quota exceeded for O3",
  "error_code": "REASONING_QUOTA_EXCEEDED",
  "model": "o3",
  "daily_reasoning_jobs": 50,
  "daily_limit": 50,
  "reset_time": "2024-12-21T00:00:00Z",
  "alternatives": ["o3-mini", "gpt-4.1"]
}
```

### Format d'Erreurs Standard
```json
{
  "detail": "Job type 'invalid_type' non trouvé",
  "error_code": "JOB_TYPE_NOT_FOUND",
  "field_errors": {
    "job_type": ["Ce champ est requis"],
    "priority": ["Doit être: low, normal, high, urgent"]
  },
  "suggestions": ["chat_completion", "content_analysis", "text_generation"]
}
```

---

## 📖 Documentation Détaillée

- **[🎯 ai_core](./core.md)** - Hub central des jobs IA
- **[🔌 ai_providers](./providers.md)** - Providers et credentials sécurisées  
- **[🟢 ai_openai](./openai.md)** - Intégration OpenAI O3/GPT-4.1
- **[📊 ai_usage](./usage.md)** - Usage, métriques et alertes enhanced
- **[📋 Référence Complète](./complete-reference.md)** - Tous les endpoints O3
- **[🚀 Exemples](./examples/workflows.md)** - Workflows O3 d'intégration
- **[⚙️ Migration Guide](./migration/o3-upgrade.md)** - Guide migration O3

---

## 🔧 Setup et Maintenance

### Variables d'Environnement
```bash
# AI Core
AI_DEFAULT_MODEL=gpt-4o
AI_ENABLE_O3=true
AI_O3_DAILY_BUDGET=100.00

# Encryption
AI_ENCRYPTION_KEY=base64_encoded_key

# Quotas
AI_DEFAULT_MONTHLY_QUOTA=1000000
AI_O3_SPECIAL_QUOTA=50000

# Monitoring
AI_ENABLE_ALERTING=true
AI_ALERT_EMAIL=admin@megahub.fr
```

### Commandes de Gestion
```bash
# Setup complet infrastructure AI
python manage.py setup_ai_infrastructure --include-o3

# Test endpoints API avec O3
python manage.py test_ai_endpoints --test-o3 --verbose

# Setup job types avec support O3
python manage.py setup_ai_job_types --include-o3

# Migration vers O3
python manage.py migrate_to_o3_support

# Health check complet
python manage.py ai_health_check --all-providers

# Reset quotas mensuels
python manage.py reset_monthly_ai_quotas

# Audit credentials
python manage.py audit_ai_credentials --rotate-expired
```

### Tests d'Intégration
```bash
# Test suite complète
python manage.py test ai_core ai_providers ai_openai ai_usage

# Test spécifique O3
python manage.py test ai_openai.tests.test_o3_integration

# Load testing
python manage.py ai_load_test --model=o3 --concurrent=10
```

---

## 💡 Bonnes Pratiques

### Sélection de Modèle Optimal
1. **O3** : Analyse complexe, recherche approfondie, raisonnement critique
2. **O3-mini** : Raisonnement standard, optimisation coût/qualité
3. **GPT-4.1** : Contenu créatif, contexte large, brainstorming
4. **GPT-4o** : Tâches générales, rapidité, efficacité coût

### Optimisation des Coûts O3
1. **reasoning_effort='low'** pour tâches simples de raisonnement
2. **Batch processing** pour réduire les coûts fixes
3. **Cache intelligent** pour requêtes similaires  
4. **Fallback strategy** : O3 → O3-mini → GPT-4.1 → GPT-4o
5. **Budget monitoring** : Alertes à 80% du quota quotidien

### Performance et Monitoring
1. **Tracking par génération** pour analyser ROI précis
2. **Alertes préventives** sur cost spikes O3
3. **Quality metrics** pour justifier surcoût premium
4. **Usage patterns** pour optimisation continue
5. **A/B testing** modèles sur tâches similaires

### Sécurité
1. **Rotation credentials** tous les 3 mois minimum
2. **Chiffrement Fernet** pour toutes les clés API
3. **Audit trail** complet des jobs sensibles
4. **Rate limiting** spécialisé par modèle O3
5. **Isolation company** stricte avec middleware

### Développement
1. **Feature flags** pour rollout progressif O3
2. **Backward compatibility** maintenue legacy models
3. **Testing exhaustif** avant production O3
4. **Monitoring alertes** post-déploiement
5. **Documentation** tenue à jour avec exemples

---

## 🔮 Roadmap

### Q1 2025
- ✅ Support O3/O3-mini complet
- ✅ Auto-configuration intelligente
- ✅ Métriques qualité avancées
- 🔄 Fine-tuning automatique selon usage
- 🔄 Multi-provider fallback intelligent

### Q2 2025
- 📋 Support Anthropic Claude-4 (si disponible)
- 📋 Intégration Google Gemini Ultra
- 📋 Cache distributé Redis pour résultats similaires
- 📋 API GraphQL pour queries complexes
- 📋 Webhooks pour notifications temps réel

### Q3 2025
- 📋 ML-powered cost prediction
- 📋 Auto-scaling workers selon charge
- 📋 Custom models fine-tunés MEGAHUB
- 📋 Analytics prédictifs ROI
- 📋 Integration Slack/Teams notifications

---

## 📊 Métriques de Performance

### Objectifs Infrastructure
- **Latence P95** : < 2s pour O3, < 500ms pour legacy
- **Disponibilité** : 99.9% uptime
- **Coût par token** : Optimisé par auto-sélection modèle
- **Précision recommandations** : > 90% satisfaction utilisateur
- **Sécurité** : 0 breach, rotation automatique clés

### KPIs Business
- **Adoption O3** : 40% des jobs complexes d'ici Q2 2025
- **ROI O3** : Justifié par qualité supérieure vs coût
- **Cost efficiency** : 25% réduction coût total via optimisation
- **User satisfaction** : > 95% sur qualité suggestions IA
- **Time to value** : < 5min pour première completion

---

**Version** : 2.0 - Infrastructure O3 Ready, Production Tested ✅

**Dernière mise à jour** : Décembre 2024 - Support O3/GPT-4.1 complet