# API Pages - Documentation Complète MEGAHUB

## 🎯 Vue d'Ensemble

L'API Pages de MEGAHUB gère le contenu éditorial des pages web avec une architecture cross-app permettant des filtres avancés sur 7 dimensions : contenu, hiérarchie, workflow, keywords, SEO, layout et performance. Interface RESTful pure pour la gestion granulaire des pages.

### Base URL
```
https://backoffice.humari.fr/websites/pages/
```

### Authentication
Tous les endpoints nécessitent :
```bash
Authorization: Bearer {jwt_token}
X-Brand-ID: {brand_id}
Content-Type: application/json
```

## 🏗️ Architecture Cross-App

Le système pages s'appuie sur 7 apps spécialisées :

- **seo_pages_content** : Contenu éditorial de base (titre, URL, meta)
- **seo_pages_hierarchy** : Structure parent-enfant (3 niveaux max)
- **seo_pages_workflow** : États publication (draft→review→published)
- **seo_pages_seo** : Configuration SEO (sitemap, images, performance)
- **seo_pages_layout** : Page builder CSS Grid avec sections
- **seo_pages_keywords** : Associations pages ↔ mots-clés avec types
- **seo_websites_core** : Relation avec sites web (contexte parent)

---

## 📄 ENDPOINT PAGES

### URLs RESTful
```
GET    /websites/pages/              # Liste pages avec filtres cross-app
POST   /websites/pages/              # Créer nouvelle page
GET    /websites/pages/{id}/         # Détail page avec relations
PUT    /websites/pages/{id}/         # Modifier page complète
PATCH  /websites/pages/{id}/         # Modifier page partielle
DELETE /websites/pages/{id}/         # Supprimer page (soft delete)
```

### Modèle Page - Structure Complète

#### Champs Core (seo_pages_content)
```python
{
    "id": 123,
    "title": "Guide SEO Complet 2024",        # Titre de la page
    "url_path": "/blog/guide-seo-2024",       # Chemin URL unique par site
    "meta_description": "Guide complet...",   # Meta description SEO
    "website": 1,                             # ID du site parent
    "page_type": "blog",                      # Type de page
    "search_intent": "TOFU",                  # Intention de recherche
    "created_at": "2024-12-15T09:00:00Z",
    "updated_at": "2024-12-20T14:30:00Z"
}
```

#### Enrichissements Cross-App (selon contexte)
```python
{
    # Relations site (seo_websites_core)
    "website_name": "Site Humari",
    "website_url": "https://humari.fr",
    "website_domain_authority": 65,
    
    # Hiérarchie (seo_pages_hierarchy)
    "hierarchy_level": 2,                     # Niveau dans l'arbre (1-3)
    "parent_id": 45,                          # ID page parent
    "children_count": 3,                      # Nombre d'enfants
    
    # Workflow (seo_pages_workflow)
    "workflow_status": {
        "status": "published",
        "status_display": "Publié",
        "color": "#28a745",
        "changed_at": "2024-12-20T10:00:00Z",
        "changed_by": "martin"
    },
    
    # Keywords (seo_pages_keywords)
    "keywords_count": 8,
    "primary_keyword": "guide seo 2024",
    "keywords_breakdown": {
        "primary": 1,
        "secondary": 4,
        "anchor": 3
    },
    "ai_keywords_count": 5,
    
    # SEO (seo_pages_seo)
    "seo_config": {
        "sitemap_priority": 0.8,
        "sitemap_changefreq": "weekly",
        "featured_image": "https://cdn.example.com/guide-seo.jpg",
        "exclude_from_sitemap": false
    },
    
    # Layout (seo_pages_layout)
    "layout_config": {
        "render_strategy": "sections",
        "sections_count": 6,
        "has_page_builder": true
    }
}
```

### Types et Choix Disponibles

#### Types de Pages
```python
PAGE_TYPE_CHOICES = [
    ('vitrine', 'Vitrine'),                   # Page vitrine corporate
    ('blog', 'Blog'),                         # Article de blog
    ('blog_category', 'Catégorie Blog'),      # Page catégorie blog
    ('produit', 'Produit/Service'),           # Fiche produit/service
    ('landing', 'Landing Page'),              # Page d'atterrissage
    ('categorie', 'Page Catégorie'),          # Catégorie e-commerce
    ('legal', 'Page Légale'),                 # CGU, mentions légales
    ('outils', 'Outils'),                     # Outils/calculateurs
    ('autre', 'Autre')                        # Type non classifié
]
```

#### Intentions de Recherche
```python
SEARCH_INTENT_CHOICES = [
    ('TOFU', 'Top of Funnel'),               # Découverte, awareness
    ('MOFU', 'Middle of Funnel'),            # Considération, évaluation
    ('BOFU', 'Bottom of Funnel')             # Conversion, achat
]
```

#### Statuts Workflow
```python
WORKFLOW_STATUS_CHOICES = [
    ('draft', 'Brouillon'),                  # En cours d'écriture
    ('pending_review', 'En attente'),        # Soumis pour review
    ('approved', 'Approuvé'),                # Validé par admin
    ('scheduled', 'Programmé'),              # Publication programmée
    ('published', 'Publié'),                 # Live sur le site
    ('unpublished', 'Dépublié'),             # Retiré temporairement
    ('archived', 'Archivé')                  # Archivé définitivement
]
```

#### Types de Mots-Clés
```python
KEYWORD_TYPE_CHOICES = [
    ('primary', 'Primaire'),                 # Mot-clé principal (1 par page)
    ('secondary', 'Secondaire'),             # Mots-clés de support
    ('anchor', 'Ancre')                      # Mots-clés d'ancrage/longue traîne
]
```

---

## 🔍 FILTRES CROSS-APP AVANCÉS

### GET /websites/pages/ - Filtrage Multi-Dimensionnel

L'API pages propose **45+ filtres cross-app** permettant des requêtes complexes sur toutes les dimensions.

#### Exemples d'Usage Métier

**Pages à optimiser en priorité :**
```bash
GET /websites/pages/?workflow_status=published&has_meta_description=false&has_primary_keyword=false&sitemap_priority_max=0.5
```

**Contenu blog performant :**
```bash
GET /websites/pages/?page_type=blog&workflow_status=published&keywords_count_min=5&has_featured_image=true&sitemap_priority_min=0.6
```

**Pages avec page builder moderne :**
```bash
GET /websites/pages/?has_layout=true&render_strategy=sections&sections_count_min=3&workflow_status=published
```

**Audit contenu par site :**
```bash
GET /websites/pages/?website=5&has_keywords=false&workflow_status=draft&page_type=vitrine
```

### Filtres par Dimension

#### 1. Contenu de Base (seo_pages_content)
```bash
# Recherche textuelle
?title=guide                          # Titre contient
?url_path=/blog                       # URL contient
?search=seo                           # Recherche titre/URL/meta

# Classification
?website=1                            # Site spécifique
?page_type=blog                       # Type de page
?search_intent=TOFU                   # Intention recherche
?has_meta_description=true            # A meta description
```

#### 2. Hiérarchie (seo_pages_hierarchy)
```bash
# Structure arborescente
?hierarchy_level=2                    # Niveau hiérarchique (1-3)
?has_parent=true                      # A un parent
?has_children=true                    # A des enfants
?is_root_page=true                    # Page racine (niveau 1)
?parent_id=45                         # Enfants d'une page spécifique
```

#### 3. Workflow Publication (seo_pages_workflow)
```bash
# États de publication
?workflow_status=published            # Statut spécifique
?is_published=true                    # Raccourci publié
?is_scheduled=true                    # Publication programmée
?status_changed_after=2024-12-01T00:00:00Z  # Statut modifié après date

# Workflow avancé
?pending_review=true                  # En attente de validation
?approved_not_published=true          # Approuvé mais pas encore publié
```

#### 4. Mots-Clés (seo_pages_keywords)
```bash
# Présence mots-clés
?has_keywords=true                    # A des mots-clés
?keywords_count_min=5                 # Minimum mots-clés
?keywords_count_max=15                # Maximum mots-clés

# Types de mots-clés
?has_primary_keyword=true             # A mot-clé principal
?keyword_type=secondary               # Filtre par type
?is_ai_selected=true                  # Mots-clés IA

# Métriques mots-clés
?primary_keyword_volume_min=1000      # Volume mot-clé principal min
?avg_keyword_difficulty_max=0.6       # Difficulté moyenne max
```

#### 5. Configuration SEO (seo_pages_seo)
```bash
# Sitemap
?sitemap_priority_min=0.6             # Priorité minimum
?sitemap_priority_max=0.9             # Priorité maximum
?sitemap_changefreq=weekly            # Fréquence de changement
?exclude_from_sitemap=false           # Inclus dans sitemap

# Images et contenu
?has_featured_image=true              # A image featured
?featured_image_optimized=true        # Image optimisée (WebP, etc.)

# Performance
?needs_regeneration=true              # Nécessite re-rendu
?last_rendered_after=2024-12-01T00:00:00Z  # Rendu après date
```

#### 6. Page Builder / Layout (seo_pages_layout)
```bash
# Configuration layout
?has_layout=true                      # A configuration page builder
?render_strategy=sections             # Stratégie : sections/markdown/custom
?has_sections=true                    # A des sections
?sections_count_min=3                 # Minimum sections
?sections_count_max=10                # Maximum sections

# Types de sections
?section_type=hero_banner             # Contient type de section spécifique
?popular_section_types=hero_banner,cta_banner  # Plusieurs types (comma-separated)

# Templates
?template_used=blog_post              # Template spécifique utilisé
```

#### 7. Contexte Website (seo_websites_core)
```bash
# Métriques site parent
?website_name=humari                  # Nom site contient
?website_domain_authority_min=50      # DA site minimum
?website_max_competitor_kd_max=0.7    # KD concurrent max du site

# Catégorisation site
?website_category=5                   # Catégorie du site
?website_primary_category=3           # Catégorie principale site
?categorization_source=manual         # Source catégorisation site
?da_above_category=true               # Site avec DA > moyenne catégorie
```

#### 8. Performance Cross-App
```bash
# Métriques calculées
?performance_score_min=75             # Score performance min (0-100)
?seo_completeness_min=0.8             # Complétude SEO min (0.0-1.0)
?content_quality_score_min=80         # Score qualité contenu min

# Comparaisons
?above_site_average=true              # Au-dessus moyenne du site
?below_site_average=true              # En-dessous moyenne du site
```

### Tri et Pagination

#### Champs de Tri Disponibles
```bash
# Base
?ordering=title                       # Titre A-Z
?ordering=-created_at                 # Plus récent d'abord
?ordering=url_path                    # URL alphabétique

# Métriques
?ordering=-keywords_count             # Plus de mots-clés d'abord
?ordering=hierarchy_level             # Par niveau hiérarchique
?ordering=-sitemap_priority           # Priorité SEO décroissante
?ordering=workflow_status             # Par statut workflow

# Performance
?ordering=-performance_score          # Meilleur score d'abord
?ordering=last_updated               # Dernière modification
```

#### Pagination Optimisée
```bash
?page=2                              # Page suivante
?page_size=25                        # 25 résultats par page (défaut)
?page_size=50                        # Pour analyses bulk
?page_size=10                        # Pour interfaces de sélection
```

---

## 📝 ENDPOINTS CRUD

### GET /websites/pages/ - Liste avec Contexte

#### Réponse Standard
```json
{
    "count": 245,
    "next": "?page=2",
    "previous": null,
    "results": [
        {
            "id": 123,
            "title": "Guide SEO Complet 2024",
            "url_path": "/blog/guide-seo-2024",
            "website": 1,
            "website_name": "Site Humari",
            "page_type": "blog",
            "page_type_display": "Blog",
            "search_intent": "TOFU",
            "search_intent_display": "Top of Funnel",
            "created_at": "2024-12-15T09:00:00Z",
            "updated_at": "2024-12-20T14:30:00Z"
        }
    ]
}
```

#### Réponse Enrichie (avec filtres cross-app)
```json
{
    "count": 45,
    "results": [
        {
            "id": 123,
            "title": "Guide SEO Complet 2024",
            "url_path": "/blog/guide-seo-2024",
            "meta_description": "Guide complet pour débuter en SEO...",
            "website": 1,
            "website_name": "Site Humari",
            "page_type": "blog",
            "page_type_display": "Blog",
            "search_intent": "TOFU",
            "search_intent_display": "Top of Funnel",
            
            // Enrichissements conditionnels selon filtres actifs
            "hierarchy_level": 2,                # Si filtres hiérarchie
            "workflow_status": {                 # Si filtres workflow
                "status": "published",
                "status_display": "Publié",
                "color": "#28a745"
            },
            "keywords_count": 8,                 # Si filtres keywords
            "seo_config": {                      # Si filtres SEO
                "sitemap_priority": 0.8,
                "has_featured_image": true
            },
            "layout_config": {                   # Si filtres layout
                "sections_count": 6,
                "render_strategy": "sections"
            },
            
            "created_at": "2024-12-15T09:00:00Z",
            "updated_at": "2024-12-20T14:30:00Z"
        }
    ],
    
    // Stats contextuelles ajoutées automatiquement
    "context_stats": {
        "total_found": 45,
        "filters_applied": 4,
        "avg_keywords_per_page": 6.2,
        "publication_rate": 0.87,
        "avg_sitemap_priority": 0.65,
        "page_type_distribution": {
            "blog": 28,
            "vitrine": 12,
            "produit": 5
        }
    }
}
```

### POST /websites/pages/ - Création Page

#### Paramètres de Création
```json
{
    "title": "Nouveau Guide Marketing Digital",    # REQUIS - 3+ caractères
    "url_path": "/guides/marketing-digital",      # OPTIONNEL - auto-généré si vide
    "meta_description": "Guide complet...",       # OPTIONNEL - recommandé pour SEO
    "website": 1,                                 # REQUIS - ID site accessible
    "page_type": "blog",                          # OPTIONNEL - défaut 'vitrine'
    "search_intent": "TOFU",                      # OPTIONNEL - aide au SEO
    "parent_id": 45                               # OPTIONNEL - pour hiérarchie
}
```

#### Validations Automatiques
- **title** : Minimum 3 caractères, nettoyage espaces
- **url_path** : Auto-génération via slugify si vide, préfixe `/` automatique
- **website** : Vérification appartenance à la brand de l'utilisateur
- **parent_id** : Validation hiérarchie (max 3 niveaux)
- **Unicité** : url_path unique par website

#### Réponse Création Complète
```json
{
    "id": 456,
    "title": "Nouveau Guide Marketing Digital",
    "url_path": "/guides/marketing-digital",
    "meta_description": "Guide complet...",
    "website": 1,
    "website_name": "Site Humari",
    "page_type": "blog",
    "page_type_display": "Blog",
    "search_intent": "TOFU",
    "search_intent_display": "Top of Funnel",
    
    // Relations automatiquement créées
    "hierarchy_level": 2,                         # Calculé depuis parent_id
    "workflow_status": {                          # Statut initial
        "status": "draft",
        "status_display": "Brouillon",
        "color": "#6c757d"
    },
    "keywords_count": 0,                          # Aucun mot-clé initial
    "seo_config": {                               # Config SEO par défaut
        "sitemap_priority": 0.5,
        "sitemap_changefreq": "monthly",
        "exclude_from_sitemap": false
    },
    "layout_config": null,                        # Pas de layout initial
    
    "created_at": "2024-12-20T15:45:00Z",
    "updated_at": "2024-12-20T15:45:00Z"
}
```

### GET /websites/pages/{id}/ - Détail Complet

#### Réponse Détail Enrichi
```json
{
    "id": 123,
    "title": "Guide SEO Complet 2024",
    "url_path": "/blog/guide-seo-2024",
    "meta_description": "Guide complet pour débuter en SEO en 2024 avec toutes les techniques avancées et outils essentiels.",
    "website": 1,
    "website_name": "Site Humari",
    "page_type": "blog",
    "page_type_display": "Blog",
    "search_intent": "TOFU",
    "search_intent_display": "Top of Funnel",
    
    // Relations complètes chargées
    "website_context": {
        "id": 1,
        "name": "Site Humari",
        "url": "https://humari.fr",
        "domain_authority": 65,
        "brand_name": "Humari"
    },
    
    "hierarchy": {
        "level": 2,
        "parent": {
            "id": 45,
            "title": "Blog Marketing",
            "url_path": "/blog"
        },
        "children": [
            {
                "id": 124,
                "title": "SEO Technique Avancé",
                "url_path": "/blog/guide-seo-2024/seo-technique"
            }
        ]
    },
    
    "workflow": {
        "status": "published",
        "status_display": "Publié",
        "color": "#28a745",
        "published_date": "2024-12-18T09:00:00Z",
        "changed_at": "2024-12-18T08:45:00Z",
        "changed_by": {
            "id": 1,
            "username": "martin",
            "display_name": "Martin Dupont"
        }
    },
    
    "keywords": {
        "total_count": 8,
        "breakdown": {
            "primary": 1,
            "secondary": 4,
            "anchor": 3
        },
        "ai_selected_count": 5,
        "keywords_list": [
            {
                "id": 1,
                "keyword": "guide seo 2024",
                "type": "primary",
                "volume": 2400,
                "is_ai_selected": true
            }
        ]
    },
    
    "seo": {
        "sitemap_priority": 0.8,
        "sitemap_changefreq": "weekly",
        "featured_image": "https://cdn.humari.fr/guide-seo.jpg",
        "featured_image_alt": "Guide SEO 2024",
        "exclude_from_sitemap": false,
        "last_rendered_at": "2024-12-20T14:30:00Z",
        "performance_score": 85.2
    },
    
    "layout": {
        "render_strategy": "sections",
        "sections_count": 6,
        "sections": [
            {
                "id": 1,
                "type": "hero_banner",
                "order": 0,
                "data": {
                    "title": "Guide SEO 2024",
                    "subtitle": "Maîtrisez le référencement"
                }
            }
        ]
    },
    
    "created_at": "2024-12-15T09:00:00Z",
    "updated_at": "2024-12-20T14:30:00Z"
}
```

### PUT /websites/pages/{id}/ - Modification Complète

#### Paramètres de Modification
```json
{
    "title": "Guide SEO Complet 2024 - Version Mise à Jour",
    "meta_description": "Guide complet et actualisé pour débuter en SEO en 2024...",
    "page_type": "blog",
    "search_intent": "MOFU",                      # Changement d'intention
    "parent_id": 48                               # Changement de hiérarchie
}
```

#### Validations Mises à Jour
- **title** : Validation longueur et nettoyage
- **url_path** : Vérification unicité si modifié
- **parent_id** : Validation hiérarchie et prévention cycles
- **Cohérence** : Vérification compatibilité page_type + search_intent

### PATCH /websites/pages/{id}/ - Modification Partielle

#### Exemple Changement Statut
```json
{
    "workflow_status": "published"               # Changement statut uniquement
}
```

### DELETE /websites/pages/{id}/ - Suppression

#### Comportement Soft Delete
- **Soft delete** par défaut (marquage `is_deleted=true`)
- **Préservation relations** pour audit trail
- **Vérifications** : Pas d'enfants dans hiérarchie
- **Cascade intelligent** : Suppression sections page builder associées

#### Réponse Suppression
```json
{
    "id": 123,
    "message": "Page supprimée avec succès",
    "deleted_at": "2024-12-20T16:00:00Z",
    "relations_affected": {
        "keywords_removed": 8,
        "sections_removed": 6,
        "children_orphaned": 0
    }
}
```

---

## 🚀 Optimisations Performance

### Stratégie de Requêtes Conditionnelles

L'API optimise automatiquement selon les filtres utilisés pour éviter les N+1 queries.

#### 1. Optimisations de Base (Toujours Actives)
```python
queryset = queryset.select_related(
    'website',                                # Site parent
    'website__brand'                         # Brand du site
).annotate(
    keywords_count=Count('page_keywords', distinct=True)
)
```

#### 2. Optimisations Conditionnelles

**Si filtres hiérarchie actifs :**
```python
queryset = queryset.select_related('hierarchy__parent')
.prefetch_related('children_hierarchy')
```

**Si filtres workflow actifs :**
```python
queryset = queryset.select_related('workflow_status')
.prefetch_related('workflow_status__changed_by')
```

**Si filtres keywords actifs :**
```python
queryset = queryset.prefetch_related(
    'page_keywords__keyword',
    'page_keywords__source_cocoon'
)
```

**Si filtres SEO actifs :**
```python
queryset = queryset.select_related('seo_config', 'performance')
```

**Si filtres layout actifs :**
```python
queryset = queryset.select_related('layout_config')
.prefetch_related('sections')
```

### Résultats Performance
- **0 N+1 queries** même avec 10+ filtres cross-app
- **Réponse < 150ms** pour 500+ pages avec filtres complexes
- **Mémoire optimisée** via préchargements ciblés
- **Pagination efficace** avec count() optimisé

---

## 🛠️ Gestion d'Erreurs Spécialisées

### Erreurs de Validation

#### Création Page
```json
{
    "detail": "Validation échouée",
    "field_errors": {
        "title": ["Le titre doit contenir au moins 3 caractères"],
        "url_path": ["Cette URL existe déjà sur ce site"],
        "parent_id": ["Hiérarchie maximum 3 niveaux atteinte"],
        "website": ["Ce site n'appartient pas à votre brand"]
    }
}
```

#### Hiérarchie Invalide
```json
{
    "detail": "Erreur hiérarchie",
    "error_code": "HIERARCHY_VIOLATION",
    "errors": {
        "parent_id": ["Création d'un cycle détectée"],
        "hierarchy_level": ["Maximum 3 niveaux de profondeur autorisés"]
    },
    "current_hierarchy": {
        "requested_parent": 45,
        "current_level": 3,
        "max_allowed": 3
    }
}
```

#### Workflow Transition Invalide
```json
{
    "detail": "Transition workflow non autorisée",
    "error_code": "INVALID_WORKFLOW_TRANSITION", 
    "errors": {
        "workflow_status": ["Impossible de passer de 'archived' à 'published' directement"]
    },
    "allowed_transitions": ["draft", "unpublished"],
    "current_status": "archived"
}
```

### Erreurs Métier

#### Contraintes SEO
```json
{
    "detail": "Contraintes SEO non respectées",
    "error_code": "SEO_CONSTRAINTS_VIOLATION",
    "warnings": [
        "Page sans mot-clé primaire",
        "Meta description manquante",
        "Priorité sitemap faible pour page importante"
    ],
    "recommendations": [
        "Ajouter un mot-clé primaire via /websites/keywords/",
        "Rédiger une meta description de 150-160 caractères",
        "Augmenter la priorité sitemap à 0.7+"
    ]
}
```

---

## 📋 Workflows Métier Complets

### 1. Création Contenu Blog Optimisé SEO

```bash
# 1. Créer la page blog
POST /websites/pages/
{
    "title": "10 Tendances Marketing Digital 2024",
    "url_path": "/blog/tendances-marketing-2024", 
    "meta_description": "Découvrez les 10 tendances marketing digital incontournables pour 2024...",
    "website": 5,
    "page_type": "blog",
    "search_intent": "TOFU",
    "parent_id": 12
}

# 2. Vérifier création avec relations
GET /websites/pages/456/

# 3. Configurer page builder (via app layout)
POST /websites/builder/sections/
{
    "page": 456,
    "section_type": "hero_banner",
    "data": {"title": "10 Tendances Marketing Digital 2024"}
}

# 4. Associer mots-clés (via app keywords)
POST /websites/keywords/
{
    "page": 456,
    "keyword": "tendances marketing digital 2024",
    "keyword_type": "primary"
}

# 5. Finaliser et publier (via app workflow)
PATCH /websites/pages/456/
{
    "workflow_status": "published"
}
```

### 2. Audit et Optimisation Pages Existantes

```bash
# 1. Identifier pages sous-optimisées
GET /websites/pages/?website=5&workflow_status=published&has_meta_description=false&keywords_count_max=2&sitemap_priority_max=0.5

# 2. Analyser détail d'une page problématique
GET /websites/pages/234/

# 3. Pages de même type pour benchmark
GET /websites/pages/?page_type=blog&workflow_status=published&keywords_count_min=5&sitemap_priority_min=0.7

# 4. Optimiser en masse (identification)
GET /websites/pages/?website=5&has_primary_keyword=false&workflow_status=published
```

### 3. Gestion Hiérarchie et Structure Site

```bash
# 1. Pages racines d'un site
GET /websites/pages/?website=3&is_root_page=true

# 2. Construire arborescence complète
GET /websites/pages/?website=3&ordering=hierarchy_level,url_path

# 3. Pages orphelines (sans parent mais pas racines)
GET /websites/pages/?website=3&hierarchy_level=2&has_parent=false

# 4. Restructurer hiérarchie
PUT /websites/pages/125/
{
    "parent_id": 78
}
```

### 4. Workflow Publication avec Validation

```bash
# 1. Pages en attente de review
GET /websites/pages/?workflow_status=pending_review&website=2

# 2. Pages approuvées non publiées
GET /websites/pages/?workflow_status=approved&website=2

# 3. Planning publication
GET /websites/pages/?workflow_status=scheduled&website=2&ordering=scheduled_publish_date

# 4. Publier une page
PATCH /websites/pages/189/
{
    "workflow_status": "published"
}
```

---

## 🎯 Use Cases Avancés

### Analytics Cross-Page

```bash
# Distribution types de pages par site
GET /websites/pages/?website=5&include_type_stats=true

# Performance moyenne par intention recherche
GET /websites/pages/?search_intent=TOFU&include_performance_stats=true

# Pages avec meilleur ratio mots-clés/performance
GET /websites/pages/?keywords_count_min=5&sitemap_priority_min=0.7&ordering=-performance_score
```

### Détection Contenu Dupliqué

```bash
# Pages avec titres similaires
GET /websites/pages/?title__icontains=guide%20seo

# Pages avec mêmes mots-clés primaires
GET /websites/pages/?primary_keyword=guide%20seo%202024

# Vérification URL similaires
GET /websites/pages/?url_path__startswith=/blog/guide
```

### Optimisation Layout Cross-Page

```bash
# Pages avec page builder moderne
GET /websites/pages/?has_layout=true&render_strategy=sections&sections_count_min=4

# Pages sans layout à moderniser
GET /websites/pages/?workflow_status=published&has_layout=false&page_type=vitrine

# Analyse types de sections populaires
GET /websites/pages/?has_sections=true&include_sections_stats=true
```

---

## 📊 Métriques et KPIs

### Indicateurs de Qualité Calculés

```python
# Score de Performance Global (0-100)
performance_score = (
    seo_completeness * 0.4 +      # Meta, keywords, images
    content_quality * 0.3 +       # Longueur, structure
    technical_seo * 0.2 +         # Sitemap, performance
    user_engagement * 0.1         # Temps sur page, bounces
)

# Complétude SEO (0.0-1.0)
seo_completeness = (
    has_meta_description +
    has_primary_keyword + 
    has_featured_image +
    sitemap_configured
) / 4

# Score Contenu (0-100)
content_quality = (
    title_optimization +          # Longueur, mots-clés
    content_structure +           # H1-H6, paragraphes
    internal_linking +            # Liens sortants
    multimedia_presence           # Images, vidéos
)
```

### Dashboard Metrics Suggérées

```bash
# KPIs globaux par site
GET /websites/pages/?website=5&include_kpis=true

Response:
{
    "kpis": {
        "total_pages": 145,
        "published_rate": 0.87,
        "avg_keywords_per_page": 5.2,
        "avg_performance_score": 72.3,
        "seo_completeness": 0.68,
        "pages_need_attention": 23
    }
}
```

---

## 🔗 Intégrations Cross-App

### Relations avec Autres Endpoints

#### Keywords Management
```bash
# Mots-clés d'une page
GET /websites/keywords/?page=123

# Ajouter mot-clé à une page
POST /websites/keywords/
{
    "page": 123,
    "keyword": "nouveau mot-clé",
    "keyword_type": "secondary"
}
```

#### Page Builder  
```bash
# Sections d'une page
GET /websites/builder/sections/?page=123

# Ajouter section
POST /websites/builder/sections/
{
    "page": 123,
    "section_type": "cta_banner"
}
```

#### Workflow Management
```bash
# Historique workflow d'une page
GET /websites/workflow/history/?page=123

# Programmer publication
POST /websites/workflow/schedule/
{
    "page": 123,
    "scheduled_date": "2024-12-25T09:00:00Z"
}
```

---

## 💡 Bonnes Pratiques API

### Requêtes Optimisées
1. **Filtrer par website** en premier pour réduire le scope
2. **Combiner filtres** pour affiner les résultats rapidement
3. **Utiliser pagination** pour listes > 100 items
4. **Privilégier ordering** par champs indexés

### Patterns d'Usage
1. **Liste → Détail** : GET pages/ puis GET pages/{id}/
2. **Création guidée** : Valider données avant POST
3. **Modifications atomiques** : PATCH pour changements simples
4. **Bulk operations** : Filtrer puis itérer sur résultats

### Performance
1. **Cache côté client** : Réponses GET cachées 5-10min
2. **Debounce recherche** : Attendre 300ms avant requête
3. **Pagination intelligente** : page_size adapté au contexte
4. **Préchargement** : Relations chargées selon besoins interface

---

**Documentation v2.0** - API Pages MEGAHUB  

**Couverture** : 45+ filtres cross-app, workflow complet, optimisations performance