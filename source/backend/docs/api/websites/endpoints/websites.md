# API Websites - Documentation Complète MEGAHUB

## 🎯 Vue d'Ensemble

L'API Websites de MEGAHUB gère l'ensemble de l'écosystème des sites web et leurs pages avec une architecture modulaire de 8 apps spécialisées. Cette documentation couvre les endpoints principaux `/websites/` et `/websites/pages/` avec leurs filtres cross-app avancés.

### Base URL
```
https://backoffice.humari.fr/websites/
```

### Authentication
Tous les endpoints nécessitent :
```bash
Authorization: Bearer {jwt_token}
X-Brand-ID: {brand_id}
Content-Type: application/json
```

## 🏗️ Architecture Modulaire

Le système websites est organisé en 8 apps spécialisées :

- **seo_websites_core** : Sites web et métriques de base
- **seo_pages_content** : Contenu éditorial des pages  
- **seo_pages_hierarchy** : Structure hiérarchique parent-enfant
- **seo_pages_workflow** : États de publication (draft→published)
- **seo_pages_seo** : Configuration SEO et performance
- **seo_pages_layout** : Page builder et sections CSS Grid
- **seo_pages_keywords** : Association pages ↔ mots-clés
- **seo_websites_categorization** : Catégorisation des sites

---

## 🌐 ENDPOINT WEBSITES

### URLs de Base
```
GET    /websites/              # Liste sites avec filtres avancés
POST   /websites/              # Créer nouveau site
GET    /websites/{id}/         # Détail site complet
PUT    /websites/{id}/         # Modifier site
DELETE /websites/{id}/         # Supprimer site
GET    /websites/{id}/stats/   # Statistiques détaillées site
```

### Modèle Website

#### Champs de Base
```python
{
    "id": 1,
    "name": "Site Humari",                    # Nom du site
    "url": "https://humari.fr",               # URL principale
    "domain_authority": 65,                   # DA du site (0-100)
    "max_competitor_backlinks": 50000,        # Backlinks max concurrence
    "max_competitor_kd": 0.8,                 # KD max acceptable
    "brand": 9,                               # ID de la brand propriétaire
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-12-20T14:45:00Z"
}
```

#### Relations Calculées (selon contexte)
```python
{
    "brand_name": "Humari",                   # Nom de la brand
    "pages_count": 45,                        # Nombre total de pages
    "total_keywords": 350,                    # Total mots-clés (si filtres actifs)
    "unique_keywords": 280,                   # Mots-clés uniques
    "published_pages": 38,                    # Pages publiées
    "avg_sitemap_priority": 0.7,              # Priorité sitemap moyenne
    "total_sections": 120,                    # Sections page builder
    "keywords_ratio": 7.8,                    # Ratio mots-clés/pages
    "publication_ratio": 0.84,                # Ratio publication
    "performance_score": 78.5                 # Score global (0-100)
}
```

### GET /websites/ - Liste avec Filtres Cross-App

#### Exemples d'Usage

**Sites performants avec bon SEO :**
```bash
GET /websites/?keywords_coverage_min=0.8&meta_description_coverage_min=0.7&has_primary_keywords=true&publication_ratio_min=0.6
```

**Sites nécessitant attention :**
```bash
GET /websites/?publication_ratio_max=0.5&keywords_coverage_max=0.3&needs_openai_sync=true
```

**Sites avec page builder moderne :**
```bash
GET /websites/?has_page_builder=true&render_strategy=sections&layout_coverage_min=0.5
```

#### Filtres Disponibles (54 filtres cross-app)

##### Base & Brand
```bash
?name=marketing                        # Nom contient
?url=humari                           # URL contient
?domain_authority_min=50              # DA minimum
?domain_authority_max=80              # DA maximum
?brand_name=humari                    # Nom brand contient
?has_chatgpt_key=true                 # Brand avec clé ChatGPT
?has_gemini_key=true                  # Brand avec clé Gemini
```

##### Pages Content
```bash
?pages_count_min=20                   # Minimum pages
?pages_count_max=100                  # Maximum pages
?has_pages=true                       # A des pages
?page_types=vitrine,blog              # Types de pages (comma-separated)
?search_intents=TOFU,MOFU             # Intentions (comma-separated)
?has_vitrine_pages=true               # A pages vitrine
?has_blog_pages=true                  # A pages blog
?has_product_pages=true               # A pages produit
```

##### Workflow Publication
```bash
?has_published_pages=true             # A pages publiées
?has_draft_pages=true                 # A brouillons
?has_scheduled_pages=true             # A pages programmées
?published_pages_count_min=10         # Min pages publiées
?publication_ratio_min=0.7            # Ratio publication min (0.0-1.0)
?publication_ratio_max=0.9            # Ratio publication max
```

##### Keywords
```bash
?has_keywords=true                    # A des mots-clés
?total_keywords_count_min=100         # Min mots-clés total
?unique_keywords_count_min=80         # Min mots-clés uniques
?keywords_coverage_min=0.8            # Coverage min (0.0-1.0)
?has_primary_keywords=true            # A mots-clés primaires
?ai_keywords_ratio_min=0.3            # Ratio IA min (0.0-1.0)
?avg_keyword_volume_min=1000          # Volume moyen min
```

##### SEO
```bash
?has_seo_config=true                  # A config SEO
?has_featured_images=true             # A images featured
?avg_sitemap_priority_min=0.6         # Priorité sitemap min
?excluded_from_sitemap_count_max=5    # Max pages exclues sitemap
?meta_description_coverage_min=0.8    # Coverage meta description
```

##### Page Builder / Layout
```bash
?has_page_builder=true                # A page builder
?sections_count_min=50                # Min sections
?layout_coverage_min=0.6              # Coverage layout (0.0-1.0)
?popular_section_types=hero_banner,cta_banner  # Types sections
?render_strategy=sections             # Stratégie : sections/markdown/custom
```

##### Catégorisation
```bash
?website_category=5                   # ID catégorie
?primary_category=3                   # ID catégorie principale
?category_level=1                     # Niveau catégorie (0=racine)
?categorization_source=manual         # Source : manual/automatic/ai_suggested
?has_primary_category=true            # A catégorie principale
```

##### Performance vs Catégorie
```bash
?da_above_category=true               # DA > moyenne catégorie
?da_below_category=true               # DA < moyenne catégorie
?pages_above_category=true            # Pages > moyenne catégorie
?performance_vs_category=above        # Performance : above/typical/below
```

##### Synchronisation OpenAI
```bash
?needs_openai_sync=true               # Nécessite sync
?last_synced_after=2024-12-01T00:00:00Z  # Sync après date
?sync_version=5                       # Version sync
```

##### Recherche & Tri
```bash
?search=marketing                     # Recherche nom/URL/brand
?ordering=-created_at                 # Tri : name/domain_authority/pages_count
?include_stats=true                   # Inclure stats globales
```

#### Réponse GET /websites/

**Structure Standard :**
```json
{
    "count": 45,
    "next": "?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Site Humari",
            "url": "https://humari.fr",
            "brand_name": "Humari",
            "domain_authority": 65,
            "max_competitor_backlinks": 50000,
            "max_competitor_kd": 0.8,
            "pages_count": 45,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-12-20T14:45:00Z"
        }
    ]
}
```

**Avec Filtres Cross-App (champs conditionnels ajoutés) :**
```json
{
    "count": 12,
    "results": [
        {
            "id": 1,
            "name": "Site Humari",
            "url": "https://humari.fr",
            "brand_name": "Humari",
            "domain_authority": 65,
            "pages_count": 45,
            "total_keywords": 350,           # ← Ajouté si filtres keywords
            "unique_keywords": 280,          # ← Ajouté si filtres keywords
            "published_pages": 38,           # ← Ajouté si filtres workflow
            "avg_sitemap_priority": 0.7,     # ← Ajouté si filtres SEO
            "total_sections": 120,           # ← Ajouté si filtres layout
            "keywords_ratio": 7.8,           # ← Stats calculées
            "publication_ratio": 0.84,       # ← Stats calculées
            "performance_score": 78.5        # ← Score global calculé
        }
    ],
    "search_stats": {                        # ← Stats globales ajoutées
        "total_found": 12,
        "filters_applied": 3,
        "avg_domain_authority": 58.3,
        "avg_pages_per_site": 42.1,
        "da_range": {"min": 35, "max": 78},
        "keywords_stats": {
            "avg_total_keywords": 312.5,
            "avg_unique_keywords": 245.2
        }
    }
}
```

### POST /websites/ - Création

#### Paramètres Requis
```json
{
    "name": "Nouveau Site",                  # REQUIS - 3+ caractères
    "url": "https://example.com",            # REQUIS - Format URL valide
    "brand": 9,                              # REQUIS - ID brand accessible
    "domain_authority": 45,                  # OPTIONNEL - 0-100
    "max_competitor_backlinks": 25000,       # OPTIONNEL - > 0
    "max_competitor_kd": 0.6                 # OPTIONNEL - 0.0-1.0
}
```

#### Validations
- **name** : Minimum 3 caractères, unique par brand
- **url** : Format URL valide, ajout automatique https:// si absent
- **brand** : Doit appartenir à la company de l'utilisateur
- **domain_authority** : Entre 0 et 100
- **max_competitor_kd** : Entre 0.0 et 1.0
- **Cohérence** : DA faible + KD max élevé = erreur

#### Réponse Création
```json
{
    "id": 15,
    "name": "Nouveau Site",
    "url": "https://example.com",
    "brand": 9,
    "brand_name": "Humari",
    "domain_authority": 45,
    "max_competitor_backlinks": 25000,
    "max_competitor_kd": 0.6,
    "pages_count": 0,
    "created_at": "2024-12-20T15:30:00Z",
    "updated_at": "2024-12-20T15:30:00Z"
}
```

### GET /websites/{id}/ - Détail Complet

#### Réponse Enrichie
```json
{
    "id": 1,
    "name": "Site Humari",
    "url": "https://humari.fr", 
    "domain_authority": 65,
    "max_competitor_backlinks": 50000,
    "max_competitor_kd": 0.8,
    "brand": 9,
    "brand_name": "Humari",
    "brand_id": 9,
    "brand_chatgpt_key": true,              # Boolean sécurisé
    "brand_gemini_key": false,
    "brand_admin_name": "martin",
    "company_name": "Humari SAS",
    "pages_count": 45,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-12-20T14:45:00Z"
}
```

### GET /websites/{id}/stats/ - Statistiques Détaillées

#### Réponse Stats Complètes
```json
{
    "website_id": 1,
    "website_name": "Site Humari",
    "website_url": "https://humari.fr",
    "brand_name": "Humari",
    "total_pages": 45,
    "pages_by_type": {
        "vitrine": 12,
        "blog": 25,
        "produit": 6,
        "landing": 2
    },
    "pages_by_status": {
        "published": 38,
        "draft": 5,
        "scheduled": 2
    },
    "domain_authority": 65,
    "competitor_metrics": {
        "max_backlinks": 50000,
        "max_kd": 0.8
    },
    "performance_ratios": {
        "publication_rate": 0.84,           # Pages publiées / total
        "completion_rate": 0.89             # Pages non-draft / total
    }
}
```

---

## 📄 ENDPOINT PAGES

### URLs de Base
```
GET    /websites/pages/              # Liste pages avec filtres cross-app
POST   /websites/pages/              # Créer nouvelle page
GET    /websites/pages/{id}/         # Détail page complet  
PUT    /websites/pages/{id}/         # Modifier page
DELETE /websites/pages/{id}/         # Supprimer page
```

### Modèle Page

#### Champs de Base
```python
{
    "id": 123,
    "title": "Guide SEO Complet 2024",        # Titre de la page
    "url_path": "/blog/guide-seo-2024",       # Chemin URL (auto-généré si vide)
    "meta_description": "Guide complet...",   # Meta description SEO
    "website": 1,                             # ID du site parent
    "page_type": "blog",                      # Type de page
    "search_intent": "TOFU",                  # Intention de recherche
    "created_at": "2024-12-15T09:00:00Z",
    "updated_at": "2024-12-20T14:30:00Z"
}
```

#### Types de Pages Disponibles
```python
PAGE_TYPE_CHOICES = [
    'vitrine',        # Page vitrine
    'blog',           # Article de blog
    'blog_category',  # Catégorie blog
    'produit',        # Produit/Service
    'landing',        # Landing page
    'categorie',      # Page catégorie
    'legal',          # Page légale
    'outils',         # Outils
    'autre'           # Autre
]
```

#### Intentions de Recherche
```python
SEARCH_INTENT_CHOICES = [
    'TOFU',    # Top of Funnel (découverte)
    'MOFU',    # Middle of Funnel (considération)
    'BOFU'     # Bottom of Funnel (conversion)
]
```

#### Relations Étendues (selon contexte)
```python
{
    "website_name": "Site Humari",           # Nom du site
    "page_type_display": "Blog",             # Libellé type
    "search_intent_display": "Top of Funnel", # Libellé intention
    "hierarchy_level": 2,                     # Niveau hiérarchique (1-3)
    "workflow_status": {                      # Statut workflow
        "status": "published",
        "status_display": "Publié", 
        "color": "#28a745"
    },
    "keywords_count": 8                       # Nombre mots-clés
}
```

### GET /websites/pages/ - Liste avec Filtres Cross-App

#### Exemples d'Usage

**Pages blog publiées avec mots-clés :**
```bash
GET /websites/pages/?page_type=blog&workflow_status=published&has_keywords=true
```

**Pages sans SEO à optimiser :**
```bash
GET /websites/pages/?has_meta_description=false&sitemap_priority_max=0.5&has_primary_keyword=false
```

**Pages avec page builder :**
```bash
GET /websites/pages/?has_layout=true&render_strategy=sections&sections_count_min=3
```

#### Filtres Disponibles (40+ filtres cross-app)

##### Base Content
```bash
?title=seo                            # Titre contient
?url_path=/blog                       # URL contient
?website=1                            # ID site
?page_type=blog                       # Type de page
?search_intent=TOFU                   # Intention recherche
?has_meta_description=true            # A meta description
```

##### Hiérarchie
```bash
?hierarchy_level=2                    # Niveau (1-3)
?has_parent=true                      # A un parent
?has_children=true                    # A des enfants
?is_root_page=true                    # Page racine (niveau 1)
```

##### Workflow
```bash
?workflow_status=published            # Statut workflow
?is_published=true                    # Est publié
?is_scheduled=true                    # Programmé
?status_changed_after=2024-12-01T00:00:00Z  # Statut changé après
```

##### Keywords
```bash
?has_keywords=true                    # A des mots-clés
?keywords_count_min=5                 # Min mots-clés
?keywords_count_max=15                # Max mots-clés
?has_primary_keyword=true             # A mot-clé principal
?keyword_type=primary                 # Type mot-clé
?is_ai_selected=true                  # Mots-clés sélectionnés par IA
```

##### SEO
```bash
?sitemap_priority_min=0.6             # Priorité sitemap min
?sitemap_changefreq=weekly            # Fréquence : always/hourly/daily/weekly/monthly/yearly/never
?has_featured_image=true              # A image featured
?exclude_from_sitemap=false           # Pas exclu du sitemap
```

##### Layout / Page Builder
```bash
?has_layout=true                      # A configuration layout
?render_strategy=sections             # Stratégie : sections/markdown/custom
?has_sections=true                    # A des sections
?sections_count_min=3                 # Min sections
?section_type=hero_banner             # Type de section spécifique
```

##### Performance
```bash
?needs_regeneration=true              # Nécessite re-rendu
?last_rendered_after=2024-12-01T00:00:00Z  # Rendu après date
```

##### Website Context (cross-app)
```bash
?website_name=humari                  # Nom site contient
?website_domain_authority_min=50      # DA site min
?website_category=5                   # Catégorie site
?categorization_source=manual         # Source catégorisation
```

##### Recherche & Tri
```bash
?search=guide                         # Recherche titre/URL/meta
?ordering=-created_at                 # Tri par champ
```

#### Réponse GET /websites/pages/

**Liste Standard :**
```json
{
    "count": 125,
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

### POST /websites/pages/ - Création

#### Paramètres Requis
```json
{
    "title": "Nouveau Guide SEO",           # REQUIS - 3+ caractères
    "url_path": "/guides/nouveau-seo",     # OPTIONNEL - auto-généré si vide
    "meta_description": "Description...",   # OPTIONNEL
    "website": 1,                          # REQUIS - ID site accessible
    "page_type": "blog",                   # OPTIONNEL - défaut 'vitrine'
    "search_intent": "TOFU"                # OPTIONNEL
}
```

#### Validations
- **title** : Minimum 3 caractères, obligatoire
- **url_path** : Auto-généré depuis title si vide, préfixé par /
- **website** : Doit appartenir à la brand de l'utilisateur
- **Unicité** : url_path unique par website

#### Réponse Création
```json
{
    "id": 245,
    "title": "Nouveau Guide SEO",
    "url_path": "/guides/nouveau-seo",
    "meta_description": "Description...",
    "website": 1,
    "website_name": "Site Humari",
    "page_type": "blog",
    "page_type_display": "Blog",
    "search_intent": "TOFU",
    "search_intent_display": "Top of Funnel",
    "hierarchy_level": 1,
    "workflow_status": {
        "status": "draft",
        "status_display": "Brouillon",
        "color": "#6c757d"
    },
    "keywords_count": 0,
    "created_at": "2024-12-20T15:45:00Z",
    "updated_at": "2024-12-20T15:45:00Z"
}
```

### GET /websites/pages/{id}/ - Détail Complet

#### Réponse Enrichie
```json
{
    "id": 123,
    "title": "Guide SEO Complet 2024",
    "url_path": "/blog/guide-seo-2024",
    "meta_description": "Guide complet pour débuter en SEO en 2024...",
    "website": 1,
    "website_name": "Site Humari",
    "page_type": "blog",
    "page_type_display": "Blog",
    "search_intent": "TOFU",
    "search_intent_display": "Top of Funnel",
    "hierarchy_level": 2,                   # Calculé depuis hiérarchie
    "workflow_status": {                    # Depuis app workflow
        "status": "published",
        "status_display": "Publié",
        "color": "#28a745"
    },
    "keywords_count": 8,                    # Depuis app keywords
    "created_at": "2024-12-15T09:00:00Z",
    "updated_at": "2024-12-20T14:30:00Z"
}
```

---

## 🔧 Optimisations Performance

### Stratégie de Requêtes Intelligentes

L'API optimise automatiquement les requêtes selon les filtres utilisés :

#### 1. Base Optimizations (Toujours)
```python
queryset = queryset.select_related('brand', 'website')
.annotate(pages_count=Count('pages', distinct=True))
```

#### 2. Conditional Optimizations (Selon filtres)

**Si filtres keywords actifs :**
```python
queryset = queryset.prefetch_related('pages__page_keywords__keyword')
.annotate(
    total_keywords=Count('pages__page_keywords', distinct=True),
    unique_keywords=Count('pages__page_keywords__keyword', distinct=True)
)
```

**Si filtres SEO actifs :**
```python
queryset = queryset.prefetch_related('pages__seo_config')
.annotate(
    avg_sitemap_priority=Avg('pages__seo_config__sitemap_priority')
)
```

**Si filtres workflow actifs :**
```python
queryset = queryset.prefetch_related('pages__workflow_status')
.annotate(
    published_pages=Count('pages', filter=Q(pages__workflow_status__status='published'))
)
```

### Résultat Performance
- **0 N+1 queries** même avec filtres complexes
- **Réponse < 200ms** pour listes de 100+ sites avec 20+ filtres
- **Mémoire optimisée** avec préchargements ciblés uniquement

---

## 🚨 Gestion d'Erreurs

### Codes de Statut HTTP

| Code | Description | Exemple |
|------|-------------|---------|
| 200 | Succès | Liste/détail récupéré |
| 201 | Créé | Site/page créé avec succès |
| 400 | Validation échouée | Paramètres invalides |
| 401 | Non authentifié | Token JWT manquant/expiré |
| 403 | Permissions insuffisantes | Brand non accessible |
| 404 | Ressource non trouvée | Site/page n'existe pas |
| 500 | Erreur serveur | Erreur interne |

### Format d'Erreur Standard
```json
{
    "detail": "Description de l'erreur",
    "field_errors": {
        "name": ["Ce champ est requis"],
        "url": ["Format d'URL invalide"]
    }
}
```

### Erreurs Spécifiques

#### Validation Website
```json
{
    "detail": "Validation échouée",
    "field_errors": {
        "url": ["Cette URL est déjà utilisée par le site 'Site Concurrent'"],
        "max_competitor_kd": ["KD max élevé incohérent avec un DA faible"]
    }
}
```

#### Validation Page
```json
{
    "detail": "Validation échouée", 
    "field_errors": {
        "url_path": ["Cette URL existe déjà sur ce site"],
        "title": ["Le titre doit contenir au moins 3 caractères"]
    }
}
```

---

## 📋 Exemples de Workflows Complets

### 1. Audit SEO d'un Portfolio de Sites

```bash
# 1. Identifier sites avec problèmes SEO
GET /websites/?meta_description_coverage_max=0.5&keywords_coverage_max=0.3&publication_ratio_max=0.6

# 2. Analyser pages problématiques d'un site spécifique  
GET /websites/pages/?website=1&has_meta_description=false&has_primary_keyword=false&workflow_status=draft

# 3. Statistiques détaillées pour plan d'action
GET /websites/1/stats/
```

### 2. Création Site Complet avec Pages

```bash
# 1. Créer le site
POST /websites/
{
    "name": "Site E-commerce Mode",
    "url": "https://boutique-mode.com",
    "brand": 5,
    "domain_authority": 35,
    "page_type": "vitrine"
}

# 2. Créer page d'accueil
POST /websites/pages/
{
    "title": "Boutique Mode Tendance 2024",
    "url_path": "/",
    "website": 15,
    "page_type": "vitrine", 
    "search_intent": "TOFU"
}

# 3. Créer pages produits
POST /websites/pages/
{
    "title": "Robes de Soirée Élégantes",
    "url_path": "/collections/robes-soiree",
    "website": 15,
    "page_type": "produit",
    "search_intent": "BOFU"
}
```

### 3. Monitoring Performance Continue

```bash
# 1. Dashboard sites nécessitant attention
GET /websites/?performance_vs_category=below&needs_openai_sync=true&include_stats=true

# 2. Pages à optimiser par site
GET /websites/pages/?has_keywords=false&workflow_status=published&has_meta_description=false

# 3. Suivi progression SEO
GET /websites/?keywords_coverage_min=0.8&publication_ratio_min=0.9&da_above_category=true
```

---

## 💡 Bonnes Pratiques

### Filtrage Efficace
1. **Combiner les filtres** pour réduire les résultats
2. **Utiliser include_stats=true** pour analyses
3. **Filtrer par catégorie** pour benchmarking
4. **Monitoring via needs_openai_sync** pour IA

### Performance
1. **Pagination recommandée** : page_size=25-50
2. **Filtres indexés prioritaires** : website, page_type, workflow_status
3. **Stats conditionnelles** : Activées automatiquement selon filtres
4. **Cache stratégique** : Réponses cachées 5min côté client

### Sécurité
1. **Brand scoping automatique** : Filtrage transparent par brand accessible
2. **Validation stricte** : Tous champs validés avant sauvegarde
3. **Permissions granulaires** : Company admin vs brand member
4. **Audit trail** : Tous changements tracés avec user_id

---

## 📚 Ressources Complémentaires

### Apps Associées (Contexte)
- **Keywords** : `/websites/keywords/` - Gestion mots-clés
- **Builder** : `/websites/builder/` - Page builder CSS Grid  
- **Structure** : `/websites/structure/` - Hiérarchie pages
- **Workflow** : `/websites/workflow/` - États publication
- **SEO** : `/websites/seo/` - Configuration SEO
- **Categorization** : `/websites/categorization/` - Catégories sites

### Documentation Technique
- **Filtres Complets** : `/docs/api/websites/reference/` 
- **Modèles Détaillés** : `/docs/api/websites/models/`
- **Exemples Avancés** : `/docs/api/websites/examples/`

### Support
- **GitHub Issues** : Bugs et feature requests
- **Documentation Live** : Tests interactifs Swagger
- **Monitoring** : Dashboard performance temps réel

---

**Documentation v2.0** - Architecture websites modulaire MEGAHUB  
**Dernière mise à jour** : 2024-12-20  
**Contact** : équipe technique MEGAHUB