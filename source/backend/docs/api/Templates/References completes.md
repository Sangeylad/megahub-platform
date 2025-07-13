# API Templates - Documentation Complète

## 📋 Vue d'ensemble

Le système de templates IA permet de créer, gérer et optimiser des templates pour la génération de contenu automatisé. **Chaque template est mappé à une brand spécifique**, avec support spécialisé par support (websites mappés aux sites, futures extensions pour print, Instagram, etc.).

### 🏗️ Architecture Modulaire

```
templates/
├── core/           # CRUD templates, types, configuration brand
├── insights/       # Recommandations IA et analytics avancées
├── workflow/       # Validation et processus approbation
├── storage/        # Versioning et variables dynamiques
├── seo/           # Templates SEO spécialisés (mappés aux websites)
└── categories/     # Organisation hiérarchique et tags
```

### 🎯 Scope & Mapping

- **🏢 Brand Scoped** : Tous les templates appartiennent à une brand
- **🌐 Website Mapped** : Templates SEO liés aux sites web spécifiques
- **🚀 Futures Extensions** : Support prévu pour print, Instagram, etc.

### 🧠 Principe : Actions Intelligentes d'Abord

Le système privilégie les **actions intelligentes** qui agrègent la data et fournissent de la valeur business, plutôt que de multiplier les endpoints CRUD basiques.

### 🚀 Actions Intelligentes Principales

| Action | Endpoint | Business Value |
|### 💾 Storage & Versioning (brands_template_storage)

**Base URL :** `/templates/storage/`

#### Variables Système (Lecture Seule)
```bash
GET /templates/storage/variables/
GET /templates/storage/variables/by-type/
# Variables disponibles pour tous les templates
# Types: brand, seo, user, system
```

**Variables par Type :**
```bash
GET /templates/storage/variables/by-type/
```

**Réponse :**
```json
{
  "brand": [
    {
      "id": 1,
      "name": "brand_name",
      "display_name": "Nom de la Brand",
      "description": "Nom officiel de la marque",
      "variable_type": "brand",
      "default_value": "",
      "is_required": true,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "name": "brand_sector",
      "display_name": "Secteur d'Activité",
      "description": "Secteur de la brand",
      "variable_type": "brand",
      "default_value": "",
      "is_required": false,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "seo": [
    {
      "id": 3,
      "name": "target_keyword",
      "display_name": "Mot-clé Principal",
      "description": "Mot-clé cible principal du contenu",
      "variable_type": "seo",
      "default_value": "",
      "is_required": true,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "user": [
    {
      "id": 4,
      "name": "product_name",
      "display_name": "Nom du Produit",
      "description": "Nom du produit à mettre en avant",
      "variable_type": "user",
      "default_value": "",
      "is_required": false,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "system": [
    {
      "id": 5,
      "name": "current_date",
      "display_name": "Date Courante",
      "description": "Date automatique du jour",
      "variable_type": "system",
      "default_value": "2024-01-20",
      "is_required": false,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### 🔥 Versions - Gestion Complète

```bash
# CRUD Versions
GET    /templates/storage/versions/
POST   /templates/storage/versions/
GET    /templates/storage/versions/{id}/
PUT    /templates/storage/versions/{id}/
DELETE /templates/storage/versions/{id}/

# Action Critique
POST   /templates/storage/versions/{id}/set-current/
```

**Filtres Versions :**
- Par template : `?template=5`
- Version courante : `?is_current=true`
- Par créateur : `?created_by=3`

**Liste Versions :**
```bash
GET /templates/storage/versions/?template=5
```

**Réponse :**
```json
{
  "count": 4,
  "results": [
    {
      "id": 15,
      "template": 5,
      "template_name": "Landing Page Pro",
      "version_number": 4,
      "is_current": true,
      "created_by_username": "john.doe",
      "created_at": "2024-01-20T14:15:00Z",
      "changelog": "Amélioration structure H2 et ajout variables SEO"
    },
    {
      "id": 14,
      "template": 5,
      "template_name": "Landing Page Pro", 
      "version_number": 3,
      "is_current": false,
      "created_by_username": "jane.editor",
      "created_at": "2024-01-18T10:30:00Z",
      "changelog": "Optimisation variables et call-to-action"
    }
  ]
}
```

**Détail Version :**
```bash
GET /templates/storage/versions/15/
```

**Réponse :**
```json
{
  "id": 15,
  "template": 5,
  "template_name": "Landing Page Pro",
  "version_number": 4,
  "prompt_content": "Créez une landing page exceptionnelle pour {{product_name}}...",
  "changelog": "Amélioration structure H2 et ajout variables SEO",
  "is_current": true,
  "created_by": 3,
  "created_by_username": "john.doe",
  "created_at": "2024-01-20T14:15:00Z",
  "updated_at": "2024-01-20T14:15:00Z"
}
```

**Créer Nouvelle Version :**
```bash
POST /templates/storage/versions/
{
  "template": 5,
  "prompt_content": "Nouveau contenu du template...",
  "changelog": "Refonte complète avec nouvelles variables SEO"
}
```

**Logique Automatique :**
- Auto-incrémentation `version_number`
- Nouvelle version devient `is_current=true`
- Anciennes versions passent `is_current=false`
- `created_by` automatique depuis request.user

**Définir Version Courante :**
```bash
POST /templates/storage/versions/14/set-current/
```

**Effet :**
- Version 14 devient `is_current=true`
- Toutes autres versions du template → `is_current=false`

**Réponse :**
```json
{
  "status": "Version définie comme courante"
}
```

### 📊 Quand Utiliser Storage ?

#### ✅ **Utilisez le Core `/templates/` pour :**
- Voir versions dans détail template (`current_version` dans réponse)
- Filtrer par nombre de versions (`version_count`, `has_versions`)
- Analytics versioning (`GET /templates/analytics/?breakdown=versions`)
- Templates avec/sans changelog (`has_changelog=true`)

#### ⚡ **Utilisez Storage pour :**
- **Créer nouvelle version** avec changelog détaillé
- **Changer version courante** (rollback)
- **Consulter historique complet** des versions
- **Lister variables système** disponibles
- **Grouper variables par type** pour aide à la saisie

### 🔄 Exemple Workflow Versioning

```bash
# 1. Consulter templates avec historique (CORE)
GET /templates/?has_versions=true&version_count_min=3

# 2. Voir historique d'un template (SPÉCIALISÉ)
GET /templates/storage/versions/?template=5

# 3. Créer nouvelle version (SPÉCIALISÉ)
POST /templates/storage/versions/
{
  "template": 5,
  "prompt_content": "Version améliorée...",
  "changelog": "Optimisation SEO et variables"
}

# 4. Rollback si problème (SPÉCIALISÉ)
POST /templates/storage/versions/14/set-current/

# 5. Vérifier version courante (CORE)
GET /templates/5/  # current_version dans la réponse
```

### 🎯 Variables Helper

```bash
# Lister variables pour aide template (SPÉCIALISÉ)
GET /templates/storage/variables/by-type/

# Utiliser dans template content :
"Créez du contenu pour {{product_name}} de {{brand_name}} 
ciblant {{target_keyword}} généré le {{current_date}}"
```

### 🧠 Insights & Intelligence (brands_template_insights)

**Base URL :** `/templates/insights/`

#### 🎯 Recommandations Personnalisées

```bash
# CRUD Recommandations
GET    /templates/insights/recommendations/
POST   /templates/insights/recommendations/
GET    /templates/insights/recommendations/{id}/
PUT    /templates/insights/recommendations/{id}/
DELETE /templates/insights/recommendations/{id}/

# Actions Intelligentes
POST   /templates/insights/recommendations/{id}/mark-clicked/
GET    /templates/insights/recommendations/for-user/
```

**Types de Recommandations :**
- `trending` : Tendance - Templates populaires
- `personalized` : Personnalisé - Basé sur historique user
- `similar_brands` : Marques similaires - Inspiré d'autres brands
- `performance_based` : Performance - Basé sur métriques
- `new_release` : Nouveauté - Derniers templates

**Filtres :** `?user_id=3&recommendation_type=trending&confidence_score_min=0.8`

**Réponse Recommandations :**
```json
{
  "count": 5,
  "results": [
    {
      "id": 12,
      "brand": 1,
      "brand_name": "MaBrand",
      "user": 3,
      "user_username": "john.marketer",
      "recommended_template": 8,
      "template_name": "Landing Page Conversion",
      "recommendation_type": "performance_based",
      "confidence_score": 0.92,
      "reasoning": "Ce template a généré +35% de conversions pour des brands similaires dans votre secteur",
      "priority": 85,
      "is_active": true,
      "clicked": false,
      "clicked_at": null,
      "created_at": "2024-01-20T10:30:00Z"
    }
  ]
}
```

**Marquer comme Cliqué :**
```bash
POST /templates/insights/recommendations/12/mark-clicked/
```

**Mes Recommandations :**
```bash
GET /templates/insights/recommendations/for-user/
# Top 10 recommandations pour l'utilisateur connecté
```

#### 🔍 Insights Automatiques (Lecture Seule)

```bash
GET    /templates/insights/insights/
GET    /templates/insights/insights/{id}/

# Actions Critiques
POST   /templates/insights/insights/{id}/mark-resolved/
GET    /templates/insights/insights/critical/
```

**Types d'Insights :**
- `underused` : Sous-utilisé - Template peu exploité
- `performance_drop` : Baisse performance - Dégradation métriques
- `quality_issue` : Problème qualité - Anomalies détectées
- `trending_up` : En hausse - Popularité croissante
- `optimization_needed` : Optimisation requise - Améliorations possibles

**Niveaux de Sévérité :**
- `low` : Faible - Information
- `medium` : Moyenne - Attention recommandée
- `high` : Élevée - Action conseillée
- `critical` : Critique - Action immédiate

**Filtres :** `?template=5&insight_type=performance_drop&severity=high&is_resolved=false`

**Réponse Insights :**
```json
{
  "count": 3,
  "results": [
    {
      "id": 25,
      "template": 5,
      "template_name": "Landing Page Pro",
      "insight_type": "performance_drop",
      "title": "Baisse significative du taux d'engagement",
      "description": "Le template montre une baisse de 23% du taux d'engagement sur les 14 derniers jours. Analyse des variables et structure recommandée.",
      "severity": "high",
      "data_source": {
        "engagement_rate_before": 0.78,
        "engagement_rate_current": 0.60,
        "analysis_period": "14_days",
        "sample_size": 156
      },
      "is_resolved": false,
      "resolved_at": null,
      "auto_generated": true,
      "created_at": "2024-01-19T15:45:00Z"
    }
  ]
}
```

**Insights Critiques :**
```bash
GET /templates/insights/insights/critical/
# Insights sévérité 'critical' non résolus
```

**Résoudre Insight :**
```bash
POST /templates/insights/insights/25/mark-resolved/
```

#### 💡 Suggestions d'Optimisation

```bash
# CRUD Suggestions
GET    /templates/insights/optimizations/
POST   /templates/insights/optimizations/
GET    /templates/insights/optimizations/{id}/
PUT    /templates/insights/optimizations/{id}/
DELETE /templates/insights/optimizations/{id}/

# Actions Impact
POST   /templates/insights/optimizations/{id}/mark-implemented/
GET    /templates/insights/optimizations/high-impact/
```

**Types de Suggestions :**
- `content_improvement` : Amélioration contenu - Structure, clarté
- `variable_optimization` : Optimisation variables - Réduction/ajout
- `performance_boost` : Boost performance - Métriques conversion
- `user_experience` : Expérience utilisateur - Facilité usage
- `seo_enhancement` : Amélioration SEO - Optimisation moteurs

**Difficulté d'Implémentation :**
- `easy` : Facile - 1-2h de travail
- `medium` : Moyen - Demi-journée
- `hard` : Difficile - Plusieurs jours

**Impact Estimé :**
- `low` : Faible - Amélioration marginale
- `medium` : Moyen - Amélioration notable  
- `high` : Élevé - Impact significatif

**Réponse Suggestions :**
```json
{
  "count": 4,
  "results": [
    {
      "id": 18,
      "template": 5,
      "template_name": "Landing Page Pro",
      "suggestion_type": "variable_optimization",
      "title": "Réduire le nombre de variables pour simplifier l'usage",
      "description": "Le template utilise 12 variables. Analyser lesquelles sont réellement utilisées et merger certaines pour simplifier la saisie utilisateur.",
      "implementation_difficulty": "medium",
      "estimated_impact": "high",
      "supporting_data": {
        "current_variables": 12,
        "recommended_variables": 8,
        "unused_variables": ["secondary_cta", "footer_note"],
        "usage_complexity_score": 78
      },
      "is_implemented": false,
      "implemented_at": null,
      "created_at": "2024-01-18T11:20:00Z"
    }
  ]
}
```

**Suggestions Fort Impact :**
```bash
GET /templates/insights/optimizations/high-impact/
# Suggestions estimated_impact='high' non implémentées
```

**Marquer comme Implémenté :**
```bash
POST /templates/insights/optimizations/18/mark-implemented/
```

#### 📈 Analyses de Tendances (Lecture Seule)

```bash
GET    /templates/insights/trends/
GET    /templates/insights/trends/{id}/
GET    /templates/insights/trends/latest-trends/
```

**Types d'Analyses :**
- `usage_trends` : Tendances usage - Fréquence utilisation
- `performance_trends` : Tendances performance - Métriques évolution
- `popularity_shifts` : Évolution popularité - Adoption/abandon
- `category_analysis` : Analyse catégories - Performance par type
- `seasonal_patterns` : Patterns saisonniers - Cyclicité usage

**Scope :**
- `global` : Global - Toutes brands
- `brand` : Par brand - Brand spécifique
- `category` : Par catégorie - Type de templates
- `template_type` : Par type - Type technique

**Réponse Tendances :**
```json
{
  "count": 8,
  "results": [
    {
      "id": 5,
      "analysis_type": "usage_trends",
      "scope": "brand",
      "scope_id": 1,
      "period_start": "2024-01-01",
      "period_end": "2024-01-20",
      "trend_direction": "increasing",
      "trend_strength": 0.87,
      "key_findings": {
        "growth_rate": "+34%",
        "peak_usage_day": "tuesday",
        "most_used_template_type": "landing_pages",
        "user_adoption_rate": 0.73
      },
      "visualization_data": {
        "daily_usage": [12, 15, 18, 22, 25, 28, 31],
        "template_type_distribution": {
          "landing_pages": 45,
          "email_campaigns": 32,
          "social_posts": 23
        }
      },
      "created_at": "2024-01-20T09:00:00Z"
    }
  ]
}
```

**Dernières Tendances :**
```bash
GET /templates/insights/trends/latest-trends/
```

**Réponse Latest Trends :**
```json
{
  "usage_trends": {
    "id": 5,
    "analysis_type": "usage_trends",
    "trend_direction": "increasing",
    "trend_strength": 0.87,
    "key_findings": { "growth_rate": "+34%" }
  },
  "performance_trends": {
    "id": 7,
    "analysis_type": "performance_trends", 
    "trend_direction": "stable",
    "trend_strength": 0.65,
    "key_findings": { "avg_performance": "78%" }
  },
  "popularity_shifts": {
    "id": 9,
    "analysis_type": "popularity_shifts",
    "trend_direction": "volatile", 
    "trend_strength": 0.43,
    "key_findings": { "trending_templates": ["landing", "email"] }
  }
}
```

### 📊 Quand Utiliser Insights ?

#### ✅ **Utilisez le Core `/templates/` pour :**
- Filtrer templates avec insights (`has_insights`, `insight_type`, `is_trending`)
- Voir nombre de recommandations (`recommendations_count` dans liste)
- Analytics insights (`GET /templates/analytics/?breakdown=insights`)
- Templates nécessitant optimisation (`needs_optimization=true`)

#### ⚡ **Utilisez Insights pour :**
- **Marquer actions** (clicked, resolved, implemented)
- **Consulter recommandations personnalisées** par utilisateur
- **Analyser insights critiques** non résolus
- **Gérer suggestions** d'optimisation avec priorité
- **Consulter tendances** et analyses avancées

### 🔄 Exemple Workflow Intelligence

```bash
# 1. Dashboard insights critiques (SPÉCIALISÉ)
GET /templates/insights/insights/critical/

# 2. Mes recommandations personnalisées (SPÉCIALISÉ)  
GET /templates/insights/recommendations/for-user/

# 3. Cliquer sur recommandation (SPÉCIALISÉ)
POST /templates/insights/recommendations/12/mark-clicked/

# 4. Consulter template recommandé (CORE)
GET /templates/8/

# 5. Suggestions d'optimisation fort impact (SPÉCIALISÉ)
GET /templates/insights/optimizations/high-impact/

# 6. Implémenter suggestion (SPÉCIALISÉ)
POST /templates/insights/optimizations/18/mark-implemented/

# 7. Analyser tendances récentes (SPÉCIALISÉ)
GET /templates/insights/trends/latest-trends/
```

---

## 🗺️ Mapping & Scope

### 🏢 Brand Isolation
**Tous les templates sont isolés par brand :**
- Filtrage automatique par `request.current_brand`
- Impossibilité d'accéder aux templates d'autres brands
- Validation unicité par `(brand, name, template_type)`

### 🌐 Website Mapping (Templates SEO)
**Les templates SEO sont mappés aux websites spécifiques :**
- `SEOWebsiteTemplate` lie template à un site web
- Permet personnalisation SEO par site
- Gestion multi-sites par brand

### 🚀 Futures Extensions
**Architecture prévue pour support multi-canal :**
- **Print Templates** : Mappés aux supports print
- **Instagram Templates** : Mappés aux comptes Instagram  
- **Email Templates** : Mappés aux campagnes email
- **Video Templates** : Mappés aux chaînes vidéo

--------|----------|----------------|
| **Analytics** | `GET /templates/analytics/` | Métriques avancées avec breakdowns |
| **Tendances** | `GET /templates/trending/` | Templates populaires basés sur insights |
| **Mes Templates** | `GET /templates/my-templates/` | Vue personnalisée utilisateur |
| **Groupement** | `GET /templates/by-type/` | Organisation par type avec stats |
| **Duplication** | `POST /templates/{id}/duplicate/` | Clonage intelligent |
| **Actions Masse** | `POST /templates/bulk-update/` | Modification batch sécurisée |

### 🎯 CRUD Core (si nécessaire)

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/templates/` | GET, POST | Liste avec filtres + Création |
| `/templates/{id}/` | GET, PUT, PATCH, DELETE | Détail et modifications |
| `/templates/types/` | GET | Types disponibles (lookup) |
| `/templates/brand-configs/` | GET, POST, PUT | Limites et config brand |

### 📊 Règles Business

#### Scope et Sécurité
- **Brand Isolation** : Templates isolés par brand automatiquement
- **Permission Granulaire** : Lecture/écriture selon rôle user
- **Website Mapping** : Templates SEO liés aux sites spécifiques

#### Limites et Validation
- **Quotas Brand** : Respect `max_templates_per_type` et `max_variables_per_template`
- **Validation Stricte** : Format variables `{{var}}`, longueur contenu, unicité
- **Workflow Conditionnel** : Approbation requise selon configuration

---

## 🔧 Endpoints Détaillés

### 1. Templates Types (Lecture seule)

#### GET `/templates/types/`
Types de templates disponibles avec compteurs.

**Réponse :**
```json
[
  {
    "id": 1,
    "name": "website",
    "display_name": "Website Content",
    "description": "Templates pour contenu web",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "templates_count": 25,
    "active_templates_count": 18
  }
]
```

### 2. Configuration Brand

#### GET `/templates/brand-configs/`
Configuration templates par brand avec métriques.

**Réponse :**
```json
[
  {
    "id": 1,
    "brand": 1,
    "brand_name": "MaBrand",
    "max_templates_per_type": 50,
    "max_variables_per_template": 20,
    "allow_custom_templates": true,
    "default_template_style": "professional",
    "current_templates_count": 12,
    "usage_percentage": 24.0,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:15:00Z"
  }
]
```

### 3. Templates CRUD

#### GET `/templates/`
Liste des templates avec filtres avancés.

**Paramètres de filtrage :**

##### Filtres de base
- `name` (string) : Recherche dans le nom
- `description` (string) : Recherche dans la description
- `template_type` (int) : ID du type de template
- `is_active` (bool) : Templates actifs/inactifs
- `is_public` (bool) : Templates publics/privés

##### Filtres brand & user
- `brand` (int) : ID de la brand
- `brand_name` (string) : Nom de la brand
- `created_by` (int) : ID du créateur
- `created_by_me` (bool) : Mes templates uniquement

##### Filtres temporels
- `created_after` (datetime) : Créés après cette date
- `created_before` (datetime) : Créés avant cette date
- `last_week` (bool) : Créés la semaine dernière
- `last_month` (bool) : Créés le mois dernier
- `recent` (bool) : Modifiés dans les 3 derniers jours

##### Filtres contenu
- `has_variables` (bool) : Utilise des variables {{}}
- `variable_count` (range) : Nombre de variables estimé
- `content_length` (range) : Longueur du contenu

##### Filtres versioning (si app storage disponible)
- `has_versions` (bool) : Templates avec historique
- `version_count` (range) : Nombre de versions
- `current_version` (int) : Version courante spécifique
- `has_changelog` (bool) : Avec changelog détaillé

##### Filtres insights (si app insights disponible)
- `has_recommendations` (bool) : Avec recommandations
- `recommendation_type` : 
  - `trending` : Tendance
  - `personalized` : Personnalisé  
  - `similar_brands` : Marques similaires
  - `performance_based` : Performance
  - `new_release` : Nouveauté
- `confidence_score_min` (float) : Score confiance minimum
- `has_insights` (bool) : Avec insights automatiques
- `insight_type` : 
  - `underused` : Sous-utilisé
  - `performance_drop` : Baisse performance
  - `quality_issue` : Problème qualité
  - `trending_up` : En hausse
  - `optimization_needed` : Optimisation requise
- `insight_severity` : 
  - `low` : Faible
  - `medium` : Moyenne
  - `high` : Élevée
  - `critical` : Critique
- `unresolved_insights` (bool) : Insights non résolus
- `is_trending` (bool) : Templates en tendance
- `is_underused` (bool) : Templates sous-utilisés
- `needs_optimization` (bool) : Nécessitant optimisation

##### Filtres workflow (si app workflow disponible)
- `workflow_status` : 
  - `draft` : Brouillon
  - `pending_review` : En attente de review
  - `approved` : Approuvé
  - `rejected` : Rejeté
  - `published` : Publié
- `is_approved` (bool) : Templates approuvés
- `is_pending_review` (bool) : En attente de review
- `needs_approval` (bool) : Nécessitant approbation
- `reviewed_by` (int) : ID du reviewer
- `validation_status` : `passed`, `failed`, `pending`
- `has_validation_errors` (bool) : Avec erreurs de validation

##### Filtres SEO (si app SEO disponible)
- `has_seo_config` (bool) : Avec configuration SEO
- `seo_page_type` : 
  - `landing` : Landing Page
  - `vitrine` : Page Vitrine
  - `service` : Page Service
  - `produit` : Page Produit
  - `blog` : Article Blog
  - `category` : Page Catégorie
- `search_intent` : 
  - `TOFU` : Top of Funnel
  - `MOFU` : Middle of Funnel
  - `BOFU` : Bottom of Funnel
  - `BRAND` : Brand
- `target_word_count` (range) : Nombre de mots cible
- `keyword_density_target` (range) : Densité mots-clés cible (%)

##### Filtres performance
- `usage_count` (range) : Nombre d'utilisations
- `performance_score` (range) : Score de performance
- `is_popular` (bool) : Templates populaires
- `recently_used` (bool) : Utilisés récemment

##### Recherche globale
- `search` (string) : Recherche dans nom, description, contenu, type, créateur

**Exemples d'usage :**
```bash
# Templates actifs d'un type spécifique
GET /templates/?template_type=1&is_active=true

# Mes templates récents avec insights
GET /templates/?created_by_me=true&last_week=true&has_insights=true

# Templates en tendance avec score élevé
GET /templates/?is_trending=true&performance_score_min=80

# Recherche globale
GET /templates/?search=landing&workflow_status=approved
```

**Réponse (Liste) :**
```json
{
  "count": 156,
  "next": "http://api.example.com/templates/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Landing Page Pro",
      "description": "Template professionnel pour landing pages",
      "template_type_name": "Website Content",
      "brand_name": "MaBrand",
      "is_active": true,
      "is_public": false,
      "created_by_username": "john.doe",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-20T14:15:00Z",
      "has_variables": true,
      "is_recent": false,
      "content_preview": "Créez une landing page exceptionnelle pour {{product_name}} qui convertit vos visiteurs...",
      "versions_count": 3,
      "recommendations_count": 2
    }
  ]
}
```

#### GET `/templates/{id}/`
Détail complet d'un template.

**Réponse :**
```json
{
  "id": 1,
  "name": "Landing Page Pro",
  "description": "Template professionnel pour landing pages",
  "template_type": 1,
  "template_type_name": "Website Content",
  "brand": 1,
  "brand_name": "MaBrand",
  "prompt_content": "Créez une landing page exceptionnelle pour {{product_name}} qui convertit vos visiteurs en clients. \n\n## Titre Principal\n{{main_headline}} - {{brand_name}}\n\n## Proposition de Valeur\n{{value_proposition}}\n\n## Call-to-Action\n{{cta_text}}",
  "is_active": true,
  "is_public": false,
  "created_by": 1,
  "created_by_username": "john.doe",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:15:00Z",
  "content_analysis": {
    "character_count": 245,
    "word_count": 42,
    "variable_count": 5,
    "detected_variables": ["product_name", "main_headline", "brand_name", "value_proposition", "cta_text"],
    "has_conditionals": false,
    "complexity_score": 54
  },
  "usage_metrics": {
    "total_generations": 0,
    "last_used": null,
    "avg_rating": 0.0,
    "popularity_rank": 0
  },
  "current_version": {
    "version_number": 3,
    "created_at": "2024-01-20T14:15:00Z",
    "changelog": "Amélioration de la structure et ajout de nouvelles variables..."
  },
  "workflow_status": {
    "status": "approved",
    "status_display": "Approuvé",
    "submitted_at": "2024-01-18T09:00:00Z",
    "reviewed_at": "2024-01-19T16:30:00Z"
  },
  "seo_config": {
    "page_type": "landing",
    "search_intent": "BOFU",
    "target_word_count": 800
  },
  "performance_score": 75
}
```

#### POST `/templates/`
Création d'un nouveau template.

**Body :**
```json
{
  "name": "Template Email Marketing",
  "description": "Template pour campagnes email marketing",
  "template_type": 2,
  "prompt_content": "Créez un email marketing pour {{campaign_name}} ciblant {{target_audience}}.\n\n## Objet\n{{email_subject}}\n\n## Corps\n{{email_body}}",
  "is_active": true,
  "is_public": false
}
```

**Validation :**
- `name` : minimum 3 caractères
- `prompt_content` : minimum 10 caractères, max 10000
- Variables bien formées `{{variable}}`
- Unicité nom par brand + type
- Respect limites brand config

**Réponse :** Template créé (format détail)

#### PUT/PATCH `/templates/{id}/`
Modification d'un template existant.

**Body :** Même format que création

**Features :**
- Log automatique des changements de contenu
- Validation stricte identique à création
- Exclusion instance courante pour unicité

### 4. Actions Avancées

#### POST `/templates/{id}/duplicate/`
Duplication d'un template.

**Body :**
```json
{
  "name": "Nouveau nom (optionnel)"
}
```

**Réponse :**
```json
{
  "id": 25,
  "name": "Landing Page Pro (Copie)",
  "description": "Template professionnel pour landing pages",
  "template_type": 1,
  "brand": 1,
  "prompt_content": "...",
  "is_active": false,
  "is_public": false,
  "created_by": 1,
  "created_at": "2024-01-21T10:30:00Z"
}
```

#### GET `/templates/by-type/`
Templates groupés par type avec statistiques.

**Réponse :**
```json
{
  "total_types": 3,
  "templates_by_type": {
    "Website Content": {
      "type_id": 1,
      "total_count": 12,
      "active_count": 10,
      "public_count": 3,
      "templates": [
        {
          "id": 1,
          "name": "Landing Page Pro",
          "description": "Template professionnel...",
          "template_type_name": "Website Content",
          "brand_name": "MaBrand",
          "is_active": true,
          "is_public": false,
          "created_by_username": "john.doe",
          "created_at": "2024-01-15T10:30:00Z",
          "updated_at": "2024-01-20T14:15:00Z",
          "has_variables": true,
          "is_recent": false,
          "content_preview": "Créez une landing page...",
          "versions_count": 3,
          "recommendations_count": 2
        }
      ]
    },
    "Email Marketing": {
      "type_id": 2,
      "total_count": 8,
      "active_count": 6,
      "public_count": 1,
      "templates": [...]
    }
  }
}
```

#### GET `/templates/analytics/`
Analytics intelligentes avec breakdowns.

**Paramètres :**
- `period` : `7d`, `30d`, `90d` (défaut: 30d)
- `breakdown` : `type`, `status`, `brand` (défaut: type)

**Réponse :**
```json
{
  "period": "30d",
  "summary": {
    "total_templates": 156,
    "active_templates": 124,
    "public_templates": 18,
    "recent_templates": 23,
    "activity_rate": 14.74
  },
  "breakdown": {
    "Website Content": {
      "count": 45,
      "active": 38
    },
    "Email Marketing": {
      "count": 32,
      "active": 28
    },
    "Social Media": {
      "count": 29,
      "active": 25
    }
  }
}
```

#### GET `/templates/my-templates/`
Templates de l'utilisateur courant avec stats.

**Réponse :**
```json
{
  "summary": {
    "total": 12,
    "active": 10,
    "public": 2,
    "recent_count": 3
  },
  "recent_templates": [
    {
      "id": 23,
      "name": "Template récent",
      "description": "...",
      "template_type_name": "Website Content",
      "brand_name": "MaBrand",
      "is_active": true,
      "is_public": false,
      "created_by_username": "john.doe",
      "created_at": "2024-01-19T10:30:00Z",
      "updated_at": "2024-01-20T14:15:00Z",
      "has_variables": true,
      "is_recent": true,
      "content_preview": "Template créé récemment...",
      "versions_count": 1,
      "recommendations_count": 0
    }
  ],
  "all_templates": [...]
}
```

#### GET `/templates/trending/`
Templates en tendance avec intelligence adaptive.

**Paramètres :**
- `limit` : nombre de résultats (défaut: 10)

**Réponse :**
```json
{
  "count": 10,
  "templates": [
    {
      "id": 5,
      "name": "Template Viral",
      "description": "Template très populaire",
      "template_type_name": "Social Media",
      "brand_name": "TrendBrand",
      "is_active": true,
      "is_public": true,
      "created_by_username": "trend.maker",
      "created_at": "2024-01-10T10:30:00Z",
      "updated_at": "2024-01-20T14:15:00Z",
      "has_variables": true,
      "is_recent": false,
      "content_preview": "Créez du contenu viral avec...",
      "versions_count": 5,
      "recommendations_count": 12
    }
  ],
  "note": "Basé sur activité récente et popularité"
}
```

#### POST `/templates/bulk-update/`
Actions en masse sur plusieurs templates.

**Body :**
```json
{
  "template_ids": [1, 2, 3, 4],
  "action": "activate"
}
```

**Actions disponibles :**
- `activate` : Activer les templates
- `deactivate` : Désactiver les templates  
- `make_public` : Rendre publics
- `make_private` : Rendre privés

**Réponse :**
```json
{
  "updated_count": 3,
  "total_requested": 4,
  "errors": [
    "Template 2: Permission denied"
  ]
}
```

---

## 🔗 Apps Spécialisées & Intégrations

Le système de templates est extensible via des apps spécialisées qui enrichissent automatiquement les données et filtres disponibles.

### 🧠 Insights (brands_template_insights)

#### TemplateRecommendation
Recommandations personnalisées avec scoring de confiance.

**Types de recommandations :**
- `trending` : Tendance - Templates populaires du moment
- `personalized` : Personnalisé - Basé sur l'historique utilisateur  
- `similar_brands` : Marques similaires - Inspiré d'autres brands
- `performance_based` : Performance - Basé sur métriques de conversion
- `new_release` : Nouveauté - Derniers templates disponibles

#### TemplateInsight
Insights automatiques détectés par IA sur les templates.

**Types d'insights :**
- `underused` : Sous-utilisé - Template peu exploité
- `performance_drop` : Baisse performance - Dégradation des métriques
- `quality_issue` : Problème qualité - Détection d'anomalies
- `trending_up` : En hausse - Popularité croissante
- `optimization_needed` : Optimisation requise - Améliorations possibles

**Niveaux de sévérité :**
- `low` : Faible - Information
- `medium` : Moyenne - Attention recommandée
- `high` : Élevée - Action conseillée
- `critical` : Critique - Action immédiate requise

#### OptimizationSuggestion
Suggestions d'amélioration basées sur la data.

**Types de suggestions :**
- `content_improvement` : Amélioration contenu - Structure, clarté
- `variable_optimization` : Optimisation variables - Réduction/ajout
- `performance_boost` : Boost performance - Métriques de conversion
- `user_experience` : Expérience utilisateur - Facilité d'usage
- `seo_enhancement` : Amélioration SEO - Optimisation moteurs

**Difficulté d'implémentation :**
- `easy` : Facile - 1-2h de travail
- `medium` : Moyen - Demi-journée 
- `hard` : Difficile - Plusieurs jours

**Impact estimé :**
- `low` : Faible - Amélioration marginale
- `medium` : Moyen - Amélioration notable
- `high` : Élevé - Impact significatif

### 🔄 Workflow (brands_template_workflow)

#### TemplateApproval
Processus d'approbation avec tracking complet.

**Statuts de workflow :**
- `draft` : Brouillon - En cours de rédaction
- `pending_review` : En attente de review - Soumis pour validation
- `approved` : Approuvé - Validé par reviewer
- `rejected` : Rejeté - Refusé avec commentaires
- `published` : Publié - Actif et utilisable

#### TemplateValidationRule
Règles de validation automatiques.

**Types de règles :**
- `security` : Sécurité - Validation injection, XSS
- `quality` : Qualité - Structure, cohérence
- `format` : Format - Syntaxe, variables
- `content` : Contenu - Longueur, pertinence

### 🎯 SEO Templates (seo_websites_ai_templates_content)

#### SEOWebsiteTemplate
Templates spécialisés pour contenu SEO **mappés aux websites**.

**Types de pages :**
- `landing` : Landing Page - Pages de conversion
- `vitrine` : Page Vitrine - Présentation brand/produit
- `service` : Page Service - Description services
- `produit` : Page Produit - Fiches produits détaillées
- `blog` : Article Blog - Contenu éditorial
- `category` : Page Catégorie - Navigation taxonomique

**Intentions de recherche :**
- `TOFU` : Top of Funnel - Découverte, sensibilisation
- `MOFU` : Middle of Funnel - Considération, comparaison
- `BOFU` : Bottom of Funnel - Conversion, achat
- `BRAND` : Brand - Recherches marque spécifique

#### SEOTemplateConfig
Configuration SEO avancée avec templates prédéfinis.

**Structures par défaut :**
```json
{
  "h1_structure": "{{target_keyword}} - {{brand_name}}",
  "h2_pattern": "## {{secondary_keyword}}\n\n{{content_section}}",
  "meta_title_template": "{{target_keyword}} | {{brand_name}}",
  "meta_description_template": "{{description_intro}} {{target_keyword}} {{brand_name}}. {{cta_phrase}}"
}
```

#### KeywordIntegrationRule
Règles d'intégration automatique des mots-clés.

**Types de mots-clés :**
- `primary` : Principal - Mot-clé cible principal
- `secondary` : Secondaire - Variations sémantiques
- `anchor` : Ancre - Textes de liens internes
- `semantic` : Sémantique - Champ lexical élargi

### 💾 Storage (brands_template_storage)

#### TemplateVariable
Variables système disponibles pour les templates.

**Types de variables :**
- `brand` : Brand Data - Informations brand (nom, secteur, etc.)
- `seo` : SEO Data - Données référencement (mots-clés, métas)
- `user` : User Input - Saisies utilisateur personnalisées
- `system` : System Generated - Variables auto-générées

#### TemplateVersion
Historique complet des versions avec changelog.

**Features :**
- Auto-incrémentation des versions
- Changelog détaillé des modifications
- Rollback possible vers versions antérieures
- Tracking utilisateur par version

---

## 🛡️ Sécurité & Permissions

### Brand Isolation Totale
- **Scope automatique** : Tous les endpoints filtrés par `request.current_brand`
- **Cross-brand protection** : Impossibilité d'accéder aux templates d'autres brands
- **Actions bulk sécurisées** : Respect du scope brand même en masse

### Website Mapping Sécurisé
- **Templates SEO** : Accès limité aux websites de la brand
- **Validation croisée** : Vérification cohérence brand ↔ website
- **Isolation multi-sites** : Templates séparés par site

### Validation Stricte Multi-Niveaux
- **Unicité** : `(brand, name, template_type)` unique
- **Quotas brand** : Respect `max_templates_per_type` et `max_variables_per_template`  
- **Format** : Variables `{{variable}}` bien formées
- **Contenu** : 10-10000 caractères, validation injection
- **Workflow** : Approbation conditionnelle selon config

### Permissions Granulaires
- **IsAuthenticated** : Accès authentifié requis
- **IsBrandMember** : Membre de la brand obligatoire
- **Role-based** : Création/modification selon rôle
- **Templates publics** : Lecture inter-brands autorisée

### Audit Trail Complet
- **Versioning** : Historique complet des modifications
- **User tracking** : Traçabilité par utilisateur
- **Workflow logging** : Processus approbation tracé
- **Change detection** : Log automatique des changements critiques

---

## 📊 Performance

### Optimisations QuerySet
- `select_related()` automatique sur relations fréquentes
- Annotations conditionnelles selon apps disponibles
- Index optimisés pour filtres fréquents

### Serializers Adaptatifs
- **Liste** : Données essentielles uniquement
- **Détail** : Données complètes avec analyses
- **Écriture** : Validation stricte

### Caching Intelligent
- Annotations calculées une fois par requête
- Compteurs optimisés avec annotations DB
- Métriques mises en cache côté client

---

## 🚀 Exemples d'Usage

### Workflow Complet de Création

```bash
# 1. Vérifier types disponibles
GET /templates/types/

# 2. Vérifier config brand
GET /templates/brand-configs/

# 3. Créer template
POST /templates/
{
  "name": "Mon Template",
  "template_type": 1,
  "prompt_content": "Template pour {{product_name}}...",
  "description": "Description détaillée"
}

# 4. Dupliquer pour variante
POST /templates/5/duplicate/
{
  "name": "Mon Template - Variante"
}
```

### Recherche Avancée

```bash
# Templates performants récents
GET /templates/?is_trending=true&last_month=true&performance_score_min=70

# Mes templates avec insights critiques  
GET /templates/?created_by_me=true&insight_severity=critical&unresolved_insights=true

# Templates SEO landing pages
GET /templates/?has_seo_config=true&seo_page_type=landing&search_intent=BOFU
```

### Analytics Détaillées

```bash
# Vue d'ensemble 90 jours
GET /templates/analytics/?period=90d&breakdown=type

# Mes templates personnels
GET /templates/my-templates/

# Tendances du moment
GET /templates/trending/?limit=5
```

---

## ⚡ Actions Spécialisées (Usage Ponctuel)

> **🎯 Principe :** Le core `/templates/` avec ses filtres ultra-complets couvre 90% des besoins. Ces endpoints spécialisés ne sont utilisés que pour des **actions métier spécifiques** impossibles via les filtres.

### 🔄 Workflow (brands_template_workflow)

**Base URL :** `/templates/workflow/`

#### Règles de Validation (Admin Only)
```bash
GET /templates/workflow/validation-rules/
# Liste des règles de validation système
# Types: security, quality, format, content
# is_blocking: true = bloque publication si échec
```

**Réponse :**
```json
[
  {
    "id": 1,
    "name": "Variable Security Check",
    "description": "Validation sécurité des variables",
    "rule_type": "security",
    "validation_function": "validate_template_security",
    "is_active": true,
    "is_blocking": true,
    "error_message": "Variables non sécurisées détectées",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

#### Résultats de Validation (Lecture Seule)
```bash
GET /templates/workflow/validation-results/
# Historique complet des validations par template
# Filtres: template, validation_rule, is_valid
```

#### 🔥 Approbations - Actions Critiques

```bash
# CRUD Approbations
GET    /templates/workflow/approvals/
POST   /templates/workflow/approvals/
GET    /templates/workflow/approvals/{id}/
PUT    /templates/workflow/approvals/{id}/

# Actions Workflow Critiques
POST   /templates/workflow/approvals/{id}/submit-for-review/
POST   /templates/workflow/approvals/{id}/approve/
POST   /templates/workflow/approvals/{id}/reject/
```

**Actions Workflow :**

##### Submit for Review
```bash
POST /templates/workflow/approvals/5/submit-for-review/
```
**Conditions :** Status = 'draft' uniquement
**Effet :** Status → 'pending_review', submitted_by/at renseignés

**Réponse :**
```json
{
  "status": "Soumis pour review"
}
```

##### Approve Template
```bash
POST /templates/workflow/approvals/5/approve/
```
**Conditions :** Status = 'pending_review' uniquement
**Effet :** Status → 'approved', reviewed_by/at renseignés

##### Reject Template
```bash
POST /templates/workflow/approvals/5/reject/
{
  "rejection_reason": "Variables mal définies, revoir la structure"
}
```
**Conditions :** Status = 'pending_review' uniquement
**Effet :** Status → 'rejected', rejection_reason enregistrée

#### Reviews et Commentaires
```bash
GET    /templates/workflow/reviews/
POST   /templates/workflow/reviews/
GET    /templates/workflow/reviews/{id}/
PUT    /templates/workflow/reviews/{id}/
DELETE /templates/workflow/reviews/{id}/
```

**Création Review :**
```bash
POST /templates/workflow/reviews/
{
  "approval": 5,
  "comment": "Template excellent, juste ajuster le call-to-action",
  "rating": 4,
  "review_type": "suggestion"
}
```

**Types de reviews :**
- `comment` : Commentaire général
- `suggestion` : Suggestion d'amélioration
- `approval` : Commentaire d'approbation
- `rejection` : Justification de rejet

**Réponse Review :**
```json
{
  "id": 12,
  "approval": 5,
  "approval_template_name": "Landing Page Pro",
  "reviewer": 3,
  "reviewer_username": "john.reviewer",
  "comment": "Template excellent, juste ajuster le call-to-action", 
  "rating": 4,
  "review_type": "suggestion",
  "created_at": "2024-01-20T14:30:00Z"
}
```

### 📊 Quand Utiliser Ces Endpoints ?

#### ✅ **Utilisez le Core `/templates/` pour :**
- Afficher templates avec statut workflow (filtres `workflow_status`, `is_approved`)
- Analytics des approbations (`GET /templates/analytics/?breakdown=status`)
- Lister templates en attente (`GET /templates/?is_pending_review=true`)
- Dashboard workflow (`GET /templates/my-templates/` avec filtres)

#### ⚡ **Utilisez les Actions Spécialisées pour :**
- **Changer le statut** d'approbation (submit/approve/reject)
- **Ajouter des reviews** avec commentaires détaillés
- **Configurer les règles** de validation (admin)
- **Consulter l'historique** de validation détaillé

### 🔒 Permissions Workflow

- **Validation Rules** : `IsCompanyAdmin` uniquement
- **Validation Results** : `IsBrandMember` (lecture seule)
- **Approvals** : `IsBrandMember` (CRUD + actions)
- **Reviews** : `IsBrandMember` (CRUD)

### 📈 Exemple Workflow Complet

```bash
# 1. Consulter templates en attente (CORE)
GET /templates/?is_pending_review=true

# 2. Approuver template spécifique (SPÉCIALISÉ)
POST /templates/workflow/approvals/5/approve/

# 3. Ajouter commentaire d'approbation (SPÉCIALISÉ)
POST /templates/workflow/reviews/
{
  "approval": 5,
  "comment": "Template validé, prêt pour production",
  "review_type": "approval"
}

# 4. Vérifier templates approuvés (CORE)
GET /templates/?workflow_status=approved&recent=true
```

### 🏷️ Organisation & Catégories (brands_template_categories)

**Base URL :** `/templates/categories/`

#### 📁 Catégories Hiérarchiques

```bash
# CRUD Catégories
GET    /templates/categories/list/
POST   /templates/categories/list/
GET    /templates/categories/list/{id}/
PUT    /templates/categories/list/{id}/
DELETE /templates/categories/list/{id}/

# Actions Organisation
GET    /templates/categories/list/tree/
GET    /templates/categories/list/{id}/breadcrumb/
```

**Structure Hiérarchique :**
- **Niveau 1** : Marketing, Sales, Support
- **Niveau 2** : Email Marketing, Content Marketing, SEO
- **Niveau 3** : Newsletter, Campaigns, Landing Pages

**Auto-calcul Niveau :**
- `parent=null` → `level=1`  
- Enfant d'un niveau N → `level=N+1`
- Max 3 niveaux de profondeur

**Réponse Catégories :**
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "name": "marketing",
      "display_name": "Marketing Digital",
      "description": "Templates pour marketing digital",
      "parent": null,
      "parent_name": null,
      "level": 1,
      "sort_order": 10,
      "is_active": true,
      "icon_name": "target",
      "children_count": 3,
      "full_path": "Marketing Digital",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 5,
      "name": "email_marketing",
      "display_name": "Email Marketing",
      "description": "Templates pour campagnes email",
      "parent": 1,
      "parent_name": "Marketing Digital",
      "level": 2,
      "sort_order": 20,
      "is_active": true,
      "icon_name": "mail",
      "children_count": 2,
      "full_path": "Marketing Digital > Email Marketing",
      "created_at": "2024-01-15T11:00:00Z",
      "updated_at": "2024-01-15T11:00:00Z"
    }
  ]
}
```

**Arbre Hiérarchique Complet :**
```bash
GET /templates/categories/list/tree/
```

**Réponse Tree :**
```json
[
  {
    "id": 1,
    "name": "marketing",
    "display_name": "Marketing Digital",
    "level": 1,
    "icon_name": "target",
    "children_count": 3,
    "children": [
      {
        "id": 5,
        "name": "email_marketing",
        "display_name": "Email Marketing",
        "level": 2,
        "icon_name": "mail",
        "children": [
          {
            "id": 12,
            "name": "newsletters",
            "display_name": "Newsletters",
            "level": 3,
            "icon_name": "newspaper",
            "children_count": 0
          }
        ]
      }
    ]
  }
]
```

**Fil d'Ariane :**
```bash
GET /templates/categories/list/12/breadcrumb/
```

**Réponse Breadcrumb :**
```json
[
  {
    "id": 1,
    "name": "Marketing Digital", 
    "level": 1
  },
  {
    "id": 5,
    "name": "Email Marketing",
    "level": 2
  },
  {
    "id": 12,
    "name": "Newsletters",
    "level": 3
  }
]
```

#### 🏷️ Tags Libres

```bash
# CRUD Tags
GET    /templates/categories/tags/
POST   /templates/categories/tags/
GET    /templates/categories/tags/{id}/
PUT    /templates/categories/tags/{id}/
DELETE /templates/categories/tags/{id}/

# Actions Tags
GET    /templates/categories/tags/popular/
```

**Couleurs Disponibles :** `blue`, `green`, `red`, `yellow`, `purple`, `pink`, `gray`

**Réponse Tags :**
```json
{
  "count": 25,
  "results": [
    {
      "id": 8,
      "name": "conversion",
      "display_name": "Conversion",
      "description": "Templates orientés conversion",
      "color": "green",
      "is_active": true,
      "usage_count": 156,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 12,
      "name": "landing_page",
      "display_name": "Landing Page",
      "description": "Templates de pages d'atterrissage",
      "color": "blue",
      "is_active": true,
      "usage_count": 143,
      "created_at": "2024-01-15T11:15:00Z"
    }
  ]
}
```

**Tags Populaires :**
```bash
GET /templates/categories/tags/popular/
# Top 20 tags avec usage_count > 0
```

#### 🔐 Permissions par Plan

```bash
GET /templates/categories/permissions/
# Permissions d'accès par catégorie selon plan
```

**Types de Permissions :**
- `view` : Voir - Consulter catégorie
- `create` : Créer - Créer templates dans catégorie
- `edit` : Modifier - Modifier templates existants
- `admin` : Administration - Gestion complète

**Plans Requis :**
- `free` : Gratuit - Accès limité
- `starter` : Starter - Fonctionnalités de base
- `pro` : Pro - Fonctionnalités avancées
- `enterprise` : Enterprise - Accès complet

**Réponse Permissions :**
```json
[
  {
    "id": 5,
    "category": 1,
    "category_name": "Marketing Digital",
    "permission_type": "view",
    "required_plan": "free",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": 6,
    "category": 1,
    "category_name": "Marketing Digital",
    "permission_type": "create",
    "required_plan": "starter",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": 18,
    "category": 8,
    "category_name": "AI Advanced",
    "permission_type": "view",
    "required_plan": "enterprise",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### 📊 Quand Utiliser Categories ?

#### ✅ **Utilisez le Core `/templates/` pour :**
- Filtrer par catégorie assignée (si relation ajoutée au BaseTemplate)
- Analytics par type (`GET /templates/analytics/?breakdown=category`)
- Recherche avec tags

#### ⚡ **Utilisez Categories pour :**
- **Construire navigation** hiérarchique (tree)
- **Afficher fil d'Ariane** (breadcrumb)
- **Gérer tags populaires** pour autocomplete
- **Vérifier permissions** utilisateur par plan
- **Organiser templates** par catégories/tags

### 🔄 Exemple Workflow Organisation

```bash
# 1. Construire navigation (SPÉCIALISÉ)
GET /templates/categories/list/tree/

# 2. User clique sur catégorie, afficher breadcrumb (SPÉCIALISÉ)
GET /templates/categories/list/12/breadcrumb/

# 3. Filtrer templates de cette catégorie (CORE)
GET /templates/?category=12

# 4. Autocomplete tags pour création template (SPÉCIALISÉ)
GET /templates/categories/tags/popular/

# 5. Vérifier permissions user (SPÉCIALISÉ)
GET /templates/categories/permissions/

# 6. Créer template avec tags (CORE)
POST /templates/
{
  "name": "Newsletter Promo",
  "category": 12,
  "tags": ["conversion", "email", "promo"]
}
```

### 🎯 SEO Templates (seo_websites_ai_templates_content)

**Base URL :** `/templates/seo/`

> **🌐 Mapping Important :** Ces templates sont **mappés aux websites spécifiques** via la relation OneToOne avec BaseTemplate. Permet personnalisation SEO par site web.

#### 📄 Templates SEO Spécialisés

```bash
# CRUD SEO Templates
GET    /templates/seo/seo-templates/
POST   /templates/seo/seo-templates/
GET    /templates/seo/seo-templates/{id}/
PUT    /templates/seo/seo-templates/{id}/
DELETE /templates/seo/seo-templates/{id}/

# Actions SEO Intelligentes
GET    /templates/seo/seo-templates/by-page-type/
GET    /templates/seo/seo-templates/by-intent/
```

**Types de Pages :**
- `landing` : Landing Page - Pages de conversion
- `vitrine` : Page Vitrine - Présentation brand/produit
- `service` : Page Service - Description services
- `produit` : Page Produit - Fiches produits détaillées
- `blog` : Article Blog - Contenu éditorial
- `category` : Page Catégorie - Navigation taxonomique

**Intentions de Recherche :**
- `TOFU` : Top of Funnel - Découverte, sensibilisation
- `MOFU` : Middle of Funnel - Considération, comparaison
- `BOFU` : Bottom of Funnel - Conversion, achat
- `BRAND` : Brand - Recherches marque spécifique

**Filtres :** `?page_type=landing&search_intent=BOFU&target_word_count_min=800`

**Réponse Liste SEO Templates :**
```json
{
  "count": 12,
  "results": [
    {
      "id": 8,
      "template_name": "Landing Page Conversion Pro",
      "template_type": "Website Content",
      "category_name": "Marketing Digital",
      "brand_name": "MaBrand",
      "page_type": "landing",
      "search_intent": "BOFU",
      "target_word_count": 1200,
      "created_at": "2024-01-18T14:30:00Z"
    }
  ]
}
```

**Détail SEO Template :**
```bash
GET /templates/seo/seo-templates/8/
```

**Réponse :**
```json
{
  "id": 8,
  "base_template": 15,
  "template_name": "Landing Page Conversion Pro",
  "template_content": "Créez une landing page {{target_keyword}} pour {{brand_name}}...",
  "template_type": "Website Content",
  "category": 5,
  "category_name": "Marketing Digital",
  "brand_name": "MaBrand",
  "page_type": "landing",
  "search_intent": "BOFU",
  "target_word_count": 1200,
  "keyword_density_target": 2.1,
  "created_at": "2024-01-18T14:30:00Z",
  "updated_at": "2024-01-20T10:15:00Z",
  "keyword_rules_count": 4,
  "has_advanced_config": true
}
```

**Groupement par Type de Page :**
```bash
GET /templates/seo/seo-templates/by-page-type/
```

**Réponse :**
```json
{
  "landing": [
    {
      "id": 8,
      "template_name": "Landing Page Conversion Pro",
      "page_type": "landing",
      "search_intent": "BOFU",
      "target_word_count": 1200
    }
  ],
  "blog": [
    {
      "id": 12,
      "template_name": "Article Blog SEO Optimisé",
      "page_type": "blog", 
      "search_intent": "TOFU",
      "target_word_count": 800
    }
  ],
  "produit": [
    {
      "id": 16,
      "template_name": "Fiche Produit E-commerce",
      "page_type": "produit",
      "search_intent": "BOFU",
      "target_word_count": 600
    }
  ]
}
```

**Groupement par Intention :**
```bash
GET /templates/seo/seo-templates/by-intent/
```

**Réponse :**
```json
{
  "TOFU": [
    {
      "id": 12,
      "template_name": "Article Blog SEO Optimisé",
      "page_type": "blog",
      "search_intent": "TOFU"
    }
  ],
  "BOFU": [
    {
      "id": 8,
      "template_name": "Landing Page Conversion Pro",
      "page_type": "landing",
      "search_intent": "BOFU"
    },
    {
      "id": 16,
      "template_name": "Fiche Produit E-commerce",
      "page_type": "produit", 
      "search_intent": "BOFU"
    }
  ]
}
```

#### ⚙️ Configuration SEO Avancée

```bash
# CRUD Config SEO
GET    /templates/seo/seo-configs/
POST   /templates/seo/seo-configs/
GET    /templates/seo/seo-configs/{id}/
PUT    /templates/seo/seo-configs/{id}/
DELETE /templates/seo/seo-configs/{id}/
```

**Structures Prédéfinies avec Variables :**

**Réponse Config SEO :**
```json
{
  "id": 5,
  "seo_template": 8,
  "template_name": "Landing Page Conversion Pro",
  "h1_structure": "{{target_keyword}} - {{brand_name}} | Solution {{service_type}}",
  "h2_pattern": "## {{secondary_keyword}} : {{benefit_description}}\n\n{{content_section}}",
  "meta_title_template": "{{target_keyword}} : {{value_proposition}} | {{brand_name}}",
  "meta_description_template": "{{description_intro}} {{target_keyword}} avec {{brand_name}}. {{unique_selling_point}} {{cta_phrase}}",
  "internal_linking_rules": {
    "min_internal_links": 3,
    "max_internal_links": 8,
    "anchor_variation": true,
    "related_pages": ["services", "about", "contact"],
    "avoid_over_optimization": true
  },
  "schema_markup_type": "Organization",
  "created_at": "2024-01-18T15:00:00Z",
  "updated_at": "2024-01-20T11:30:00Z"
}
```

**Création Config SEO :**
```bash
POST /templates/seo/seo-configs/
{
  "seo_template": 8,
  "h1_structure": "{{target_keyword}} - {{brand_name}}",
  "meta_title_template": "{{target_keyword}} | {{brand_name}}",
  "meta_description_template": "{{description_intro}} {{target_keyword}} {{brand_name}}. {{cta_phrase}}",
  "schema_markup_type": "WebPage"
}
```

#### 🎯 Règles d'Intégration Mots-Clés

```bash
# CRUD Keyword Rules
GET    /templates/seo/keyword-rules/
POST   /templates/seo/keyword-rules/
GET    /templates/seo/keyword-rules/{id}/
PUT    /templates/seo/keyword-rules/{id}/
DELETE /templates/seo/keyword-rules/{id}/
```

**Types de Mots-Clés :**
- `primary` : Principal - Mot-clé cible principal
- `secondary` : Secondaire - Variations sémantiques
- `anchor` : Ancre - Textes de liens internes
- `semantic` : Sémantique - Champ lexical élargi

**Filtres :** `?seo_template=8&keyword_type=primary&natural_variations=true`

**Réponse Keyword Rules :**
```json
{
  "count": 4,
  "results": [
    {
      "id": 15,
      "seo_template": 8,
      "template_name": "Landing Page Conversion Pro",
      "keyword_type": "primary",
      "placement_rules": {
        "h1": {
          "required": true,
          "max_occurrences": 1,
          "position": "beginning"
        },
        "h2": {
          "required": true,
          "max_occurrences": 2,
          "position": "natural"
        },
        "paragraphs": {
          "first_paragraph": true,
          "last_paragraph": true,
          "distribute": true
        }
      },
      "density_min": 1.0,
      "density_max": 2.5,
      "natural_variations": true,
      "created_at": "2024-01-18T15:30:00Z"
    },
    {
      "id": 16,
      "seo_template": 8,
      "template_name": "Landing Page Conversion Pro",
      "keyword_type": "secondary",
      "placement_rules": {
        "h2": {
          "required": false,
          "max_occurrences": 3,
          "position": "natural"
        },
        "paragraphs": {
          "distribute": true,
          "avoid_stuffing": true
        }
      },
      "density_min": 0.5,
      "density_max": 1.5,
      "natural_variations": true,
      "created_at": "2024-01-18T15:45:00Z"
    }
  ]
}
```

#### 📋 Templates Prédéfinis par Type (Lecture Seule)

```bash
GET    /templates/seo/page-type-templates/
GET    /templates/seo/page-type-templates/{id}/
GET    /templates/seo/page-type-templates/by-type/
```

**Réponse Page Type Templates :**
```json
{
  "count": 6,
  "results": [
    {
      "id": 3,
      "name": "Landing Page Standard",
      "page_type": "landing",
      "template_structure": "# {{h1_title}}\n\n{{hero_section}}\n\n## {{benefit_title}}\n{{benefits_list}}\n\n## {{social_proof_title}}\n{{testimonials}}\n\n{{cta_section}}",
      "default_sections": [
        "hero_section",
        "benefits_section", 
        "social_proof_section",
        "cta_section"
      ],
      "required_variables": [
        "h1_title",
        "hero_section",
        "cta_section"
      ],
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Templates par Type :**
```bash
GET /templates/seo/page-type-templates/by-type/
```

**Réponse :**
```json
{
  "landing": [
    {
      "id": 3,
      "name": "Landing Page Standard",
      "page_type": "landing",
      "required_variables": ["h1_title", "hero_section", "cta_section"]
    },
    {
      "id": 4,
      "name": "Landing Page E-commerce",
      "page_type": "landing",
      "required_variables": ["product_name", "price", "benefits", "cta"]
    }
  ],
  "blog": [
    {
      "id": 8,
      "name": "Article Blog SEO",
      "page_type": "blog",
      "required_variables": ["title", "introduction", "conclusion"]
    }
  ]
}
```

### 📊 Quand Utiliser SEO Templates ?

#### ✅ **Utilisez le Core `/templates/` pour :**
- Voir config SEO dans détail (`seo_config` dans réponse)
- Filtrer templates SEO (`has_seo_config`, `seo_page_type`, `search_intent`)
- Analytics SEO (`GET /templates/analytics/?breakdown=seo`)
- Templates par intention (`search_intent=BOFU`)

#### ⚡ **Utilisez SEO pour :**
- **Configurer templates SEO** spécifiques aux websites
- **Gérer structures H1/H2** avec variables
- **Définir règles mots-clés** par type (primary/secondary)
- **Utiliser templates prédéfinis** par type de page
- **Optimiser densité** et placement keywords

### 🔄 Exemple Workflow SEO Complet

```bash
# 1. Consulter templates prédéfinis (SPÉCIALISÉ)
GET /templates/seo/page-type-templates/by-type/

# 2. Créer template SEO pour landing page (CORE)
POST /templates/
{
  "name": "Landing SaaS Conversion",
  "template_type": 1,
  "prompt_content": "Structure basée sur template prédéfini..."
}

# 3. Ajouter config SEO au template (SPÉCIALISÉ)
POST /templates/seo/seo-templates/
{
  "base_template": 25,
  "page_type": "landing",
  "search_intent": "BOFU",
  "target_word_count": 1000
}

# 4. Configurer structures SEO avancées (SPÉCIALISÉ)
POST /templates/seo/seo-configs/
{
  "seo_template": 9,
  "h1_structure": "{{target_keyword}} - {{brand_name}}",
  "meta_title_template": "{{target_keyword}} | {{brand_name}}"
}

# 5. Définir règles mots-clés (SPÉCIALISÉ)
POST /templates/seo/keyword-rules/
{
  "seo_template": 9,
  "keyword_type": "primary",
  "density_min": 1.0,
  "density_max": 2.5
}

# 6. Vérifier template final (CORE)
GET /templates/25/  # seo_config inclus dans réponse

# 7. Analytics templates SEO (CORE)
GET /templates/?has_seo_config=true&search_intent=BOFU
```

### 🎯 Website Mapping

Les templates SEO sont **mappés aux websites spécifiques** :
- Relation `OneToOne` avec `BaseTemplate`
- Permet configuration SEO différente par site web
- Architecture prête pour extensions futures (print, social, etc.)

---

Cette documentation couvre l'ensemble du système de templates avec tous les filtres, actions et intégrations disponibles selon votre architecture modulaire.