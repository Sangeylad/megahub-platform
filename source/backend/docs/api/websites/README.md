# 📚 API Websites - Documentation Complète

## 🎯 Vue d'Ensemble

L'API Websites MEGAHUB est organisée en **8 apps spécialisées** suivant une architecture modulaire stricte. Chaque app gère un aspect précis du système de sites web et pages.

**Base URL** : `https://backoffice.humari.fr`

### 🏗️ Architecture Apps

```
seo_websites_core/          # 🌐 Sites web + métriques SEO
├── Website                 # Site principal + DA/BL/KD concurrence
└── WebsiteSyncStatus      # Sync OpenAI

seo_pages_content/         # 📄 Contenu des pages
├── Page                   # Titre, URL, meta, classification

seo_pages_hierarchy/       # 🌳 Structure parent-enfant
├── PageHierarchy          # Relations hiérarchiques (3 niveaux max)
└── PageBreadcrumb         # Cache fil d'Ariane

seo_pages_keywords/        # 🔑 Associations page ↔ mots-clés
└── PageKeyword            # primary/secondary/anchor + traçabilité IA

seo_pages_layout/          # 🎨 Page Builder CSS Grid
├── PageLayout             # Config renderer Next.js
└── PageSection            # Sections hiérarchiques

seo_pages_workflow/        # 🔄 Cycle de publication
├── PageStatus             # draft→review→published
└── PageScheduling         # Publication programmée

seo_pages_seo/            # 🎯 Métadonnées SEO
├── PageSEO               # Sitemap, images, priorités
└── PagePerformance       # Métriques rendu/cache

seo_websites_categorization/ # 📂 Classification des sites
├── WebsiteCategory        # Hiérarchie de catégories
└── WebsiteCategorization  # Association site ↔ catégorie
```

## 🔗 Navigation Documentation

### Composants Principaux
- **[Sites Web](core.md)** - Gestion des websites + 54 filtres cross-app
- **[Pages Content](pages/content.md)** - Contenu des pages + actions custom
- **[Catégorisation](categorization.md)** - Classification intelligente des sites

### Pages Spécialisées  
- **[Hiérarchie](pages/hierarchy.md)** - Structure parent-enfant
- **[Mots-clés](pages/keywords.md)** - Associations page ↔ keywords
- **[Page Builder](pages/layout.md)** - Système sections CSS Grid
- **[Workflow](pages/workflow.md)** - Cycle de publication
- **[SEO](pages/seo.md)** - Optimisation et métriques

### Guides Pratiques
- **[Référence Filtres](examples/filters-reference.md)** - Tous les filtres avec valeurs exactes
- **[Intégration](examples/integration.md)** - Cas d'usage complets
- **[Workflows](examples/workflows.md)** - Scénarios métier réels

## 🚀 Démarrage Rapide

### Headers Requis
```bash
Authorization: Bearer {jwt_token}
X-Brand-ID: {brand_id}
Content-Type: application/json
```

### Endpoints de Base
```bash
# Sites web
GET    /websites/                    # Liste avec 54 filtres cross-app
POST   /websites/                    # Création
GET    /websites/{id}/               # Détail
PUT    /websites/{id}/               # Modification
DELETE /websites/{id}/               # Suppression
GET    /websites/{id}/stats/         # Statistiques détaillées

# Pages
GET    /pages/                       # Liste avec filtres cross-app
POST   /pages/                       # Création
GET    /pages/{id}/                  # Détail
PUT    /pages/{id}/                  # Modification
DELETE /pages/{id}/                  # Suppression
GET    /pages/by-website/            # Pages groupées par site
POST   /pages/bulk-create/           # Création en masse
```

### Filtres Cross-App Populaires
```bash
# Sites avec pages publiées + catégorie manuelle + DA élevé
GET /websites/?has_published_pages=true&categorization_source=manual&da_above_category=true

# Pages niveau 2 avec mots-clés primaires sélectionnés par IA
GET /pages/?hierarchy_level=2&has_primary_keyword=true&is_ai_selected=true

# Sites avec page builder + bon SEO
GET /websites/?has_page_builder=true&avg_sitemap_priority_gte=0.6&layout_coverage_gte=0.8
```

## 📊 Fonctionnalités Clés

### 🔥 Filtrage Cross-App Intelligent
- **54 filtres websites** combinables librement
- **45+ filtres pages** avec relations complexes
- **Optimisations conditionnelles** : préchargement selon filtres actifs
- **Stats automatiques** dans les réponses selon contexte

### 🎯 Actions Métier Avancées
- **Groupement intelligent** : Pages par type, statut, site
- **Création en masse** : Validation + rollback automatique
- **Statistiques enrichies** : Métriques cross-app en temps réel
- **Performance tracking** : Ratios et scores calculés

### 🏗️ Architecture RESTful Pure
- **CRUD standard** : GET/POST/PUT/DELETE sur tous les endpoints
- **Actions groupées** : Préfixe `/action-name/` pour actions spéciales
- **Réponses cohérentes** : Format uniforme avec pagination
- **Gestion d'erreurs** : Codes HTTP appropriés + messages explicites

## 🔧 Concepts Techniques

### Optimisations Performance
- **Préchargement conditionnel** : `select_related` selon filtres
- **Annotations intelligentes** : Calculs en base selon contexte
- **Pagination adaptative** : Désactivable sur certains endpoints
- **Cache de relations** : Évite les N+1 queries

### Sécurité Multi-Tenant
- **Scope automatique** : Filtrage par brand via middleware
- **Permissions granulaires** : IsBrandMember, IsBrandAdmin
- **Validation croisée** : Vérification ownership sur relations
- **Audit trail** : Tracking des modifications sensibles

## 🎨 Exemples Concrets

### Analyse de Performance Site
```bash
# Obtenir sites sous-performants
GET /websites/?publication_ratio_max=0.6&keywords_coverage_max=0.5&da_below_category=true

# Stats détaillées d'un site
GET /websites/123/stats/
```

### Gestion Editorial
```bash
# Pages en attente de publication
GET /pages/?workflow_status=pending_review&has_keywords=true

# Création lot de pages blog
POST /pages/bulk-create/
{
  "pages": [
    {"title": "Guide SEO 2024", "url_path": "/blog/guide-seo-2024", "website": 1, "page_type": "blog"},
    {"title": "Analytics Web", "url_path": "/blog/analytics-web", "website": 1, "page_type": "blog"}
  ]
}
```

---

**⚡ Cette documentation couvre l'intégralité de l'API Websites MEGAHUB avec ses 8 apps spécialisées et plus de 100 filtres combinables.**