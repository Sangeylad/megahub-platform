# 📚 Blog System API Documentation

**Version:** 1.0  
**Base URL:** `/blogs/`  
**Authentication:** Bearer Token (JWT)

## 🎯 Vue d'ensemble

Le système de blog MegaHub est une solution complète et modulaire pour la gestion de contenu éditorial. Il s'articule autour de **5 modules principaux** :

### 🏗️ Architecture Modulaire

```
blog_config/       # Configuration globale par website
blog_content/      # Contenu pur (articles, auteurs, tags)
blog_editor/       # Édition TipTap & conversions HTML
blog_publishing/   # Workflow de publication
blog_collections/  # Collections d'articles (séries, formations)
```

### 🔗 Relations Clés

> **⚠️ Important :** Chaque `BlogArticle` **EST** une extension du modèle `Page` du système SEO via une relation `OneToOneField`. Cela signifie que chaque article hérite automatiquement des fonctionnalités SEO (URL, méta-données, hiérarchie, etc.).

```python
Website (SEO) → Page (SEO) → BlogArticle → BlogContent
                                 ↓
                         BlogPublishingStatus
                                 ↓
                         BlogCollection
```

---

## 🚀 Guide de Démarrage Rapide

### 1. Configuration du Blog

```bash
# Créer la configuration blog pour un website
POST /blogs/config/
{
  "website": 1,
  "blog_name": "Blog Marketing",
  "blog_slug": "marketing", 
  "blog_description": "Actualités marketing digital"
}
```

### 2. Créer un Article

```bash
# Créer un article (crée automatiquement une Page SEO)
POST /blogs/articles/
{
  "title": "Guide SEO 2024",
  "website_id": 1,
  "primary_author": 1,
  "excerpt": "Guide complet pour optimiser votre SEO",
  "tags": [1, 2, 3]
}
```

### 3. Ajouter le Contenu

```bash
# Ajouter contenu TipTap
POST /blogs/editor/content/
{
  "article": 1,
  "content_tiptap": {
    "type": "doc",
    "content": [...]
  }
}
```

### 4. Publier l'Article

```bash
# Publier immédiatement
POST /blogs/publishing/status/1/publish_now/
```

---

## 📖 Référence API Complète

## 🔧 Blog Config

### Configuration globale du blog par website

**Base URL:** `/blogs/config/`

#### 📊 Modèle BlogConfig

```python
{
  "id": 1,
  "website": 1,
  "blog_name": "Blog Marketing",
  "blog_slug": "marketing",
  "blog_description": "Actualités marketing digital",
  "posts_per_page": 12,
  "posts_per_rss": 20,
  "excerpt_length": 160,
  "enable_comments": false,
  "enable_newsletter": true,
  "enable_related_posts": true,
  "enable_auto_publish": false,
  "default_meta_title_pattern": "{{article.title}} | {{blog.name}}",
  "default_meta_description_pattern": "{{article.excerpt|truncate:150}}",
  "google_analytics_id": "GA-123456789",
  "default_featured_image": "https://example.com/default.jpg",
  "auto_generate_excerpts": true,
  "template_article_page": 1,
  "template_category_page": 2,
  "template_archive_page": 3,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 🔗 Endpoints

#### `GET /blogs/config/`
Liste des configurations blog

**Paramètres de requête:**
- `website_id` (integer) - Filtrer par website

**Réponse:**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "website_name": "Mon Site",
      "blog_name": "Blog Marketing",
      "blog_slug": "marketing",
      "posts_per_page": 12,
      "enable_comments": false,
      "enable_newsletter": true,
      "total_articles": 25,
      "published_articles": 18,
      "enable_auto_publish": false
    }
  ]
}
```

#### `POST /blogs/config/`
Créer une configuration blog

**Payload:**
```json
{
  "website": 1,
  "blog_name": "Blog Marketing",
  "blog_slug": "marketing",
  "blog_description": "Actualités marketing digital",
  "posts_per_page": 12,
  "posts_per_rss": 20,
  "excerpt_length": 160,
  "enable_comments": false,
  "enable_newsletter": true,
  "enable_related_posts": true,
  "enable_auto_publish": false,
  "default_meta_title_pattern": "{{article.title}} | {{blog.name}}"
}
```

**Réponse:** Configuration créée avec stats calculées

#### `GET /blogs/config/{id}/`
Détail d'une configuration

#### `PUT /blogs/config/{id}/`
Mettre à jour une configuration

#### `DELETE /blogs/config/{id}/`
Supprimer une configuration

#### `GET /blogs/config/templates/`
Pages templates disponibles

**Paramètres de requête:**
- `website_id` (integer, requis) - ID du website

**Réponse:**
```json
{
  "available_templates": [
    {
      "id": 1,
      "title": "Template Article Standard",
      "page_type": "blog",
      "url_path": "/templates/article"
    },
    {
      "id": 2,
      "title": "Template Catégorie",
      "page_type": "blog_category",
      "url_path": "/templates/category"
    }
  ]
}
```

---

## 📝 Blog Content

### Gestion du contenu (articles, auteurs, tags)

**Base URL:** `/blogs/`

#### 📊 Modèle BlogArticle

```python
{
  "id": 1,
  "page": 1,
  "page_title": "Guide SEO 2024",
  "page_url_path": "/blog/guide-seo-2024",
  "page_status": "published",
  "website_name": "Mon Site",
  "website_id": 1,
  "primary_author": 1,
  "author_name": "John Doe",
  "author_avatar": "https://example.com/avatar.jpg",
  "co_authors": [2, 3],
  "excerpt": "Guide complet pour optimiser votre SEO",
  "auto_excerpt": "Guide complet pour optimiser votre SEO",
  "featured_image_url": "https://example.com/image.jpg",
  "featured_image_alt": "Guide SEO",
  "featured_image_caption": "Optimisation SEO",
  "tags": [1, 2, 3],
  "focus_keyword": "SEO 2024",
  "word_count": 1500,
  "reading_time_minutes": 6,
  "category_name": "Marketing",
  "publishing_status": "published",
  "publishing_status_display": "Publié",
  "published_date": "2024-01-15T10:30:00Z",
  "scheduled_date": null,
  "is_featured": true,
  "is_published": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### 📊 Modèle BlogAuthor

```python
{
  "id": 1,
  "user": 1,
  "username": "john.doe",
  "email": "john@example.com",
  "display_name": "John Doe",
  "full_name": "John Doe",
  "bio": "Expert en marketing digital",
  "avatar_url": "https://example.com/avatar.jpg",
  "website_url": "https://johndoe.com",
  "twitter_handle": "johndoe",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "expertise_topics": ["SEO", "Content Marketing", "Analytics"],
  "articles_count": 12,
  "published_articles_count": 10,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### 📊 Modèle BlogTag

```python
{
  "id": 1,
  "name": "SEO",
  "slug": "seo",
  "description": "Optimisation pour les moteurs de recherche",
  "color": "#3b82f6",
  "meta_title": "Articles SEO",
  "meta_description": "Tous nos articles sur le SEO",
  "usage_count": 25,
  "articles_count": 20,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 🔗 Endpoints Articles

#### `GET /blogs/articles/`
Liste des articles

**Paramètres de requête:**
- `search` (string) - Recherche textuelle
- `author` (integer) - Filtrer par auteur
- `tag` (integer) - Filtrer par tag
- `has_featured_image` (boolean) - A une image featured
- `word_count_min` (integer) - Nombre de mots minimum
- `word_count_max` (integer) - Nombre de mots maximum
- `reading_time_min` (integer) - Temps de lecture minimum
- `reading_time_max` (integer) - Temps de lecture maximum
- `page_type` (string) - Type de page (`blog`, `blog_category`)
- `page_status` (string) - Statut page (`draft`, `published`, `archived`)
- `website` (integer) - Site web
- `created_after` (date) - Créé après
- `created_before` (date) - Créé avant
- `ordering` (string) - Tri (`created_at`, `-created_at`, `page__title`, `word_count`, `publishing_status__published_date`)

**Réponse:**
```json
{
  "count": 50,
  "next": "http://localhost:8000/blogs/articles/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "page_title": "Guide SEO 2024",
      "page_url_path": "/blog/guide-seo-2024",
      "page_status": "published",
      "website_name": "Mon Site",
      "website_id": 1,
      "author_name": "John Doe",
      "author_avatar": "https://example.com/avatar.jpg",
      "category_name": "Marketing",
      "excerpt": "Guide complet pour optimiser votre SEO",
      "auto_excerpt": "Guide complet pour optimiser votre SEO",
      "featured_image_url": "https://example.com/image.jpg",
      "reading_time_minutes": 6,
      "word_count": 1500,
      "created_at": "2024-01-15T10:30:00Z",
      "publishing_status": "published",
      "publishing_status_display": "Publié",
      "published_date": "2024-01-15T10:30:00Z",
      "is_featured": true,
      "is_published": true
    }
  ]
}
```

#### `POST /blogs/articles/`
Créer un article (crée automatiquement une Page SEO)

**Payload:**
```json
{
  "title": "Guide SEO 2024",
  "url_path": "/blog/guide-seo-2024",
  "meta_description": "Guide complet pour optimiser votre SEO en 2024",
  "website_id": 1,
  "primary_author": 1,
  "co_authors": [2, 3],
  "excerpt": "Guide complet pour optimiser votre SEO",
  "featured_image_url": "https://example.com/image.jpg",
  "featured_image_alt": "Guide SEO",
  "featured_image_caption": "Optimisation SEO",
  "tags": [1, 2, 3],
  "focus_keyword": "SEO 2024"
}
```

**Réponse:** Article créé avec Page SEO et BlogPublishingStatus automatiques

#### `GET /blogs/articles/{id}/`
Détail d'un article

#### `PUT /blogs/articles/{id}/`
Mettre à jour un article

#### `DELETE /blogs/articles/{id}/`
Supprimer un article

#### `GET /blogs/articles/by_website/`
Articles par website

**Paramètres de requête:**
- `website_id` (integer, requis) - ID du website

#### `GET /blogs/articles/by_author/`
Articles par auteur

**Paramètres de requête:**
- `author_id` (integer, requis) - ID de l'auteur

#### `GET /blogs/articles/status_stats/`
Statistiques par statut de publication

**Réponse:**
```json
{
  "draft": 10,
  "pending_review": 3,
  "approved": 2,
  "scheduled": 1,
  "published": 25,
  "unpublished": 1,
  "archived": 5,
  "total": 47
}
```

### 🔗 Endpoints Auteurs

#### `GET /blogs/authors/`
Liste des auteurs

**Paramètres de requête:**
- `search` (string) - Recherche textuelle
- `has_articles` (boolean) - A des articles
- `expertise_topic` (string) - Filtre par expertise
- `ordering` (string) - Tri (`display_name`, `articles_count`, `created_at`)

#### `POST /blogs/authors/`
Créer un auteur (automatique via signal)

#### `GET /blogs/authors/{id}/`
Détail d'un auteur

#### `PUT /blogs/authors/{id}/`
Mettre à jour un auteur

#### `DELETE /blogs/authors/{id}/`
Supprimer un auteur

#### `GET /blogs/authors/available_users/`
Users de la company avec leur statut auteur

**Réponse:**
```json
{
  "users": [
    {
      "id": 1,
      "username": "john.doe",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "full_name": "John Doe",
      "has_author_profile": true,
      "author_id": 1
    }
  ],
  "count": 1,
  "company": "MegaHub Inc"
}
```

### 🔗 Endpoints Tags

#### `GET /blogs/tags/`
Liste des tags

**Paramètres de requête:**
- `search` (string) - Recherche textuelle
- `is_used` (boolean) - Tag utilisé
- `color` (string) - Couleur exacte
- `ordering` (string) - Tri (`name`, `usage_count`, `created_at`)

#### `POST /blogs/tags/`
Créer un tag

**Payload:**
```json
{
  "name": "SEO",
  "description": "Optimisation pour les moteurs de recherche",
  "color": "#3b82f6",
  "meta_title": "Articles SEO",
  "meta_description": "Tous nos articles sur le SEO"
}
```

#### `GET /blogs/tags/{id}/`
Détail d'un tag

#### `PUT /blogs/tags/{id}/`
Mettre à jour un tag

#### `DELETE /blogs/tags/{id}/`
Supprimer un tag

#### `GET /blogs/tags/popular/`
Tags les plus utilisés

**Réponse:** Top 20 des tags par usage_count

---

## ✏️ Blog Editor

### Édition TipTap et gestion du contenu

**Base URL:** `/blogs/editor/`

#### 📊 Modèle BlogContent

```python
{
  "id": 1,
  "article": 1,
  "article_title": "Guide SEO 2024",
  "article_author": "John Doe",
  "content_tiptap": {
    "type": "doc",
    "content": [
      {
        "type": "heading",
        "attrs": {"level": 1},
        "content": [{"type": "text", "text": "Guide SEO 2024"}]
      },
      {
        "type": "paragraph",
        "content": [{"type": "text", "text": "Contenu de l'article..."}]
      }
    ]
  },
  "content_html": "<h1>Guide SEO 2024</h1><p>Contenu de l'article...</p>",
  "content_text": "Guide SEO 2024\n\nContenu de l'article...",
  "version": 3,
  "last_edited_by": 1,
  "last_editor_name": "John Doe",
  "word_count_calculated": 1500,
  "reading_time_calculated": 6,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:45:00Z"
}
```

### 🔗 Endpoints

#### `GET /blogs/editor/content/`
Liste du contenu

**Paramètres de requête:**
- `article_id` (integer) - Filtrer par article

#### `POST /blogs/editor/content/`
Créer du contenu

**Payload:**
```json
{
  "article": 1,
  "content_tiptap": {
    "type": "doc",
    "content": [...]
  }
}
```

#### `GET /blogs/editor/content/{id}/`
Détail du contenu

#### `PUT /blogs/editor/content/{id}/`
Mettre à jour le contenu (incrémente version)

#### `DELETE /blogs/editor/content/{id}/`
Supprimer le contenu

#### `POST /blogs/editor/content/{id}/autosave/`
Sauvegarde automatique (sans incrémenter version)

**Payload:**
```json
{
  "content_tiptap": {...},
  "content_html": "<p>...</p>",
  "content_text": "..."
}
```

**Réponse:**
```json
{
  "message": "Autosave réussie",
  "last_autosave": "2024-01-15T11:45:00Z",
  "version": 3
}
```

#### `POST /blogs/editor/content/{id}/publish_content/`
Finaliser le contenu et calculer les métriques

**Réponse:**
```json
{
  "message": "Contenu finalisé",
  "version": 4,
  "word_count": 1500,
  "reading_time": 6
}
```

#### `GET /blogs/editor/content/by_article/`
Contenu par article

**Paramètres de requête:**
- `article_id` (integer, requis) - ID de l'article

#### `GET /blogs/editor/content/templates/`
Templates de contenu prédéfinis

**Réponse:**
```json
{
  "templates": [
    {
      "name": "Article Standard",
      "description": "Structure article classique",
      "content_tiptap": {
        "type": "doc",
        "content": [...]
      }
    },
    {
      "name": "Article Guide",
      "description": "Structure guide étape par étape",
      "content_tiptap": {
        "type": "doc",
        "content": [...]
      }
    }
  ]
}
```

---

## 📤 Blog Publishing

### Workflow de publication

**Base URL:** `/blogs/publishing/`

#### 📊 Modèle BlogPublishingStatus

```python
{
  "id": 1,
  "article": 1,
  "article_title": "Guide SEO 2024",
  "article_author": "John Doe",
  "status": "published",
  "published_date": "2024-01-15T10:30:00Z",
  "scheduled_date": null,
  "last_published_date": "2024-01-15T10:30:00Z",
  "submitted_for_review_at": "2024-01-15T09:00:00Z",
  "approved_at": "2024-01-15T10:00:00Z",
  "approved_by": 2,
  "approved_by_name": "Admin User",
  "is_featured": true,
  "is_premium": false,
  "is_evergreen": true,
  "notify_on_publish": true,
  "is_published_now": true,
  "can_publish": true,
  "is_scheduled_future": false,
  "created_at": "2024-01-15T08:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Statuts de publication:**
- `draft` - Brouillon
- `pending_review` - En attente de relecture
- `approved` - Approuvé
- `scheduled` - Programmé
- `published` - Publié
- `unpublished` - Dépublié
- `archived` - Archivé

#### 📊 Modèle BlogScheduledPublication

```python
{
  "id": 1,
  "article": 1,
  "article_title": "Guide SEO 2024",
  "scheduled_for": "2024-01-20T09:00:00Z",
  "execution_status": "pending",
  "executed_at": null,
  "error_message": "",
  "retry_count": 0,
  "max_retries": 3,
  "notify_author": true,
  "update_social_media": false,
  "send_newsletter": false,
  "scheduled_by": 1,
  "scheduled_by_name": "John Doe",
  "is_ready": false,
  "can_retry_now": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Statuts d'exécution:**
- `pending` - En attente
- `processing` - En cours
- `completed` - Terminée
- `failed` - Échec
- `cancelled` - Annulée

### 🔗 Endpoints Status

#### `GET /blogs/publishing/status/`
Liste des statuts de publication

**Paramètres de requête:**
- `status` (string) - Filtrer par statut
- `is_featured` (boolean) - Articles featured
- `is_premium` (boolean) - Contenu premium
- `is_evergreen` (boolean) - Contenu intemporel
- `ordering` (string) - Tri (`created_at`, `published_date`, `scheduled_date`)

#### `POST /blogs/publishing/status/`
Créer un statut de publication

**Payload:**
```json
{
  "article": 1,
  "status": "draft",
  "scheduled_date": "2024-01-20T09:00:00Z"
}
```

#### `GET /blogs/publishing/status/{id}/`
Détail d'un statut

#### `PUT /blogs/publishing/status/{id}/`
Mettre à jour un statut

**Payload:**
```json
{
  "status": "published",
  "is_featured": true,
  "is_premium": false,
  "is_evergreen": true,
  "notify_on_publish": true
}
```

#### `DELETE /blogs/publishing/status/{id}/`
Supprimer un statut

#### `GET /blogs/publishing/status/dashboard/`
Dashboard éditorial complet

**Réponse:**
```json
{
  "stats": {
    "draft": 10,
    "pending_review": 3,
    "approved": 2,
    "scheduled": 1,
    "published": 25,
    "total": 41
  },
  "pending_review": [
    {
      "id": 1,
      "article_title": "Guide SEO 2024",
      "article_author": "John Doe",
      "status": "pending_review",
      "submitted_for_review_at": "2024-01-15T09:00:00Z"
    }
  ],
  "upcoming_scheduled": [
    {
      "id": 2,
      "article_title": "Marketing Digital 2024",
      "scheduled_date": "2024-01-20T09:00:00Z"
    }
  ],
  "recent_published": [
    {
      "id": 3,
      "article_title": "Analytics Web",
      "published_date": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### `POST /blogs/publishing/status/{id}/approve/`
Approuver un article (admin seulement)

**Réponse:**
```json
{
  "message": "Article approuvé",
  "approved_at": "2024-01-15T10:30:00Z",
  "approved_by": "Admin User"
}
```

#### `POST /blogs/publishing/status/{id}/publish_now/`
Publication immédiate

**Réponse:**
```json
{
  "message": "Article publié immédiatement",
  "published_date": "2024-01-15T10:30:00Z"
}
```

#### `POST /blogs/publishing/status/bulk_approve/`
Approbation en masse (admin seulement)

**Payload:**
```json
{
  "article_ids": [1, 2, 3]
}
```

**Réponse:**
```json
{
  "message": "3 articles approuvés",
  "approved_count": 3
}
```

### 🔗 Endpoints Scheduled

#### `GET /blogs/publishing/scheduled/`
Liste des publications programmées

**Paramètres de requête:**
- `execution_status` (string) - Filtrer par statut d'exécution
- `ordering` (string) - Tri (`scheduled_for`, `created_at`)

#### `POST /blogs/publishing/scheduled/`
Créer une publication programmée

**Payload:**
```json
{
  "article": 1,
  "scheduled_for": "2024-01-20T09:00:00Z",
  "notify_author": true,
  "update_social_media": false,
  "send_newsletter": false
}
```

#### `GET /blogs/publishing/scheduled/{id}/`
Détail d'une publication programmée

#### `PUT /blogs/publishing/scheduled/{id}/`
Mettre à jour une publication programmée

#### `DELETE /blogs/publishing/scheduled/{id}/`
Supprimer une publication programmée

#### `GET /blogs/publishing/scheduled/ready_for_execution/`
Publications prêtes à exécuter

**Réponse:**
```json
{
  "ready_publications": [
    {
      "id": 1,
      "article_title": "Guide SEO 2024",
      "scheduled_for": "2024-01-15T10:30:00Z",
      "execution_status": "pending",
      "is_ready": true
    }
  ],
  "count": 1
}
```

#### `POST /blogs/publishing/scheduled/{id}/execute_now/`
Exécuter publication immédiatement

**Réponse:**
```json
{
  "message": "Publication exécutée avec succès",
  "executed_at": "2024-01-15T10:30:00Z"
}
```

#### `POST /blogs/publishing/scheduled/{id}/cancel/`
Annuler publication programmée

**Réponse:**
```json
{
  "message": "Publication annulée"
}
```

---

## 📚 Blog Collections

### Collections d'articles (séries, formations, dossiers)

**Base URL:** `/blogs/collections/`

#### 📊 Modèle BlogCollection

```python
{
  "id": 1,
  "name": "Formation SEO Complète",
  "slug": "formation-seo-complete",
  "description": "Formation complète en 10 articles",
  "collection_type": "formation",
  "template_page": 1,
  "template_page_title": "Template Formation",
  "cover_image_url": "https://example.com/cover.jpg",
  "is_active": true,
  "is_featured": true,
  "is_sequential": true,
  "meta_title": "Formation SEO Complète",
  "meta_description": "Apprenez le SEO en 10 étapes",
  "created_by": 1,
  "created_by_name": "John Doe",
  "articles_count": 10,
  "published_articles_count": 8,
  "reading_time_total": 60,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Types de collections:**
- `dossier` - Dossier Thématique
- `serie` - Série d'Articles
- `formation` - Formation
- `guide` - Guide Complet
- `newsletter` - Série Newsletter

#### 📊 Modèle BlogCollectionItem

```python
{
  "id": 1,
  "collection": 1,
  "article": 1,
  "article_title": "Guide SEO 2024",
  "article_url": "/blog/guide-seo-2024",
  "article_author": "John Doe",
  "article_reading_time": 6,
  "article_published_date": "2024-01-15T10:30:00Z",
  "order": 1,
  "custom_title": "Chapitre 1 : Introduction au SEO",
  "custom_description": "Découvrez les bases du SEO",
  "is_optional": false,
  "is_bonus": false,
  "added_by": 1,
  "display_title": "Chapitre 1 : Introduction au SEO",
  "display_description": "Découvrez les bases du SEO",
  "has_next": true,
  "has_previous": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 🔗 Endpoints Collections

#### `GET /blogs/collections/`
Liste des collections

**Paramètres de requête:**
- `collection_type` (string) - Filtrer par type
- `is_active` (boolean) - Collections actives
- `is_featured` (boolean) - Collections featured
- `is_sequential` (boolean) - Collections séquentielles
- `search` (string) - Recherche textuelle
- `ordering` (string) - Tri (`name`, `created_at`, `articles_count`)

#### `POST /blogs/collections/`
Créer une collection

**Payload:**
```json
{
  "name": "Formation SEO Complète",
  "description": "Formation complète en 10 articles",
  "collection_type": "formation",
  "template_page": 1,
  "cover_image_url": "https://example.com/cover.jpg",
  "is_active": true,
  "is_featured": true,
  "is_sequential": true,
  "meta_title": "Formation SEO Complète",
  "meta_description": "Apprenez le SEO en 10 étapes"
}
```

#### `GET /blogs/collections/{id}/`
Détail d'une collection

#### `PUT /blogs/collections/{id}/`
Mettre à jour une collection

#### `DELETE /blogs/collections/{id}/`
Supprimer une collection

#### `GET /blogs/collections/by_type/`
Collections par type

**Paramètres de requête:**
- `type` (string, requis) - Type de collection

#### `GET /blogs/collections/{id}/articles/`
Articles de la collection dans l'ordre

**Réponse:**
```json
[
  {
    "id": 1,
    "page_title": "Guide SEO 2024",
    "page_url_path": "/blog/guide-seo-2024",
    "author_name": "John Doe",
    "reading_time_minutes": 6,
    "published_date": "2024-01-15T10:30:00Z"
  }
]
```

#### `POST /blogs/collections/{id}/manage_articles/`
Gestion articles collection

**Payload:**
```json
{
  "action": "add",
  "article_ids": [1, 2, 3]
}
```

**Actions possibles:**
- `add` - Ajouter articles
- `remove` - Retirer articles
- `reorder` - Réorganiser ordre

**Réponse:**
```json
{
  "message": "Gestion articles réussie",
  "result": {
    "action": "add",
    "added_count": 3
  }
}
```

#### `GET /blogs/collections/{id}/navigation/`
Structure navigation complète

**Réponse:**
```json
{
  "collection": {
    "id": 1,
    "name": "Formation SEO Complète",
    "is_sequential": true
  },
  "navigation": [
    {
      "item_id": 1,
      "article_id": 1,
      "title": "Chapitre 1 : Introduction au SEO",
      "url_path": "/blog/guide-seo-2024",
      "order": 1,
      "is_optional": false,
      "is_bonus": false,
      "has_next": true,
      "has_previous": false
    }
  ],
  "total_items": 10
}
```

### 🔗 Endpoints Items

#### `GET /blogs/collections/items/`
Liste des items de collection

**Paramètres de requête:**
- `collection` (integer) - Filtrer par collection
- `collection_id` (integer) - Filtrer par collection (alternative)
- `is_optional` (boolean) - Items optionnels
- `is_bonus` (boolean) - Items bonus
- `ordering` (string) - Tri (`order`, `created_at`)

#### `POST /blogs/collections/items/`
Créer un item de collection

**Payload:**
```json
{
  "collection": 1,
  "article": 1,
  "order": 1,
  "custom_title": "Chapitre 1 : Introduction au SEO",
  "custom_description": "Découvrez les bases du SEO",
  "is_optional": false,
  "is_bonus": false
}
```

#### `GET /blogs/collections/items/{id}/`
Détail d'un item

#### `PUT /blogs/collections/items/{id}/`
Mettre à jour un item

#### `DELETE /blogs/collections/items/{id}/`
Supprimer un item

#### `GET /blogs/collections/items/{id}/next/`
Article suivant dans la collection

**Réponse:** Item suivant ou 404

#### `GET /blogs/collections/items/{id}/previous/`
Article précédent dans la collection

**Réponse:** Item précédent ou 404

#### `POST /blogs/collections/items/reorder/`
Réorganiser ordre des items

**Payload:**
```json
{
  "collection_id": 1,
  "items_order": [
    {"id": 1, "order": 0},
    {"id": 2, "order": 1},
    {"id": 3, "order": 2}
  ]
}
```

**Réponse:**
```json
{
  "message": "3 items réorganisés",
  "updated_count": 3
}
```

---

## 🔒 Permissions et Sécurité

### Système de permissions

- **IsAuthenticated** : Utilisateur connecté requis
- **IsBrandMember** : Membre de la brand requis
- **IsBrandAdmin** : Admin de la brand requis (pour approbation)
- **BrandScopedViewSetMixin** : Filtrage automatique par brand

### Middleware de Brand

Le système utilise un middleware qui injecte automatiquement la brand courante dans `request.current_brand` basé sur l'utilisateur connecté.

---

## 🛡️ Gestion des Erreurs

### Codes d'erreur standard

```json
{
  "error": "Message d'erreur descriptif",
  "details": {
    "field": ["Message d'erreur spécifique"]
  }
}
```

### Codes de statut HTTP

- `200` - OK
- `201` - Created
- `400` - Bad Request (validation)
- `401` - Unauthorized (non connecté)
- `403` - Forbidden (pas les permissions)
- `404` - Not Found
- `500` - Internal Server Error

---

## 📊 Pagination

### Format de réponse paginée

```json
{
  "count": 100,
  "next": "http://localhost:8000/blogs/articles/?page=2",
  "previous": null,
  "results": [...]
}
```

### Paramètres de pagination

- `page` (integer) - Numéro de page
- `page_size` (integer) - Taille de page (max 100)

---

## 🔍 Filtres et Recherche

### Filtres disponibles

Chaque endpoint supporte différents filtres selon le contexte :

- **Filtres textuels** : `search`, `name`, `title`
- **Filtres booléens** : `is_active`, `is_featured`, `has_content`
- **Filtres numériques** : `word_count_min`, `word_count_max`
- **Filtres de dates** : `created_after`, `created_before`
- **Filtres de relations** : `author`, `tag`, `collection`

### Tri (ordering)

Paramètre `ordering` avec préfixe `-` pour décroissant :
- `created_at` (croissant)
- `-created_at` (décroissant)
- `name`, `title`, `word_count`, etc.

---

## 🚀 Exemples d'usage

### Workflow complet de création d'article

```bash
# 1. Créer l'article
curl -X POST /blogs/articles/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Guide SEO 2024",
    "website_id": 1,
    "primary_author": 1,
    "excerpt": "Guide complet pour optimiser votre SEO",
    "tags": [1, 2, 3]
  }'

# 2. Ajouter le contenu
curl -X POST /blogs/editor/content/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "article": 1,
    "content_tiptap": {
      "type": "doc",
      "content": [...]
    }
  }'

# 3. Publier l'article
curl -X POST /blogs/publishing/status/1/publish_now/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Création d'une collection

```bash
# 1. Créer la collection
curl -X POST /blogs/collections/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Formation SEO Complète",
    "collection_type": "formation",
    "description": "Formation complète en 10 articles",
    "is_sequential": true
  }'

# 2. Ajouter des articles
curl -X POST /blogs/collections/1/manage_articles/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "add",
    "article_ids": [1, 2, 3]
  }'
```

---

## 📋 Checklist de mise en production

### Configuration requise

- [ ] Variables d'environnement configurées
- [ ] Base de données migrée
- [ ] Permissions configurées
- [ ] Middleware de brand activé
- [ ] Système d'authentification JWT configuré

### Tests recommandés

- [ ] Création/modification d'articles
- [ ] Workflow de publication
- [ ] Gestion des collections
- [ ] Permissions par brand
- [ ] Filtres et recherche
- [ ] Pagination sur grandes listes

---

## 🔄 Changelog

### Version 1.0 (2024-01-15)
- Système de blog modulaire complet
- Intégration avec système de pages SEO
- Workflow de publication avancé
- Gestion des collections d'articles
- Éditeur TipTap intégré
- Système de permissions par brand

---

Pour plus d'informations techniques, consultez le code source ou contactez l'équipe de développement.