# 📚 MEGAHUB API Documentation

## Vue d'Ensemble
Documentation complète de l'API RESTful MEGAHUB suivant les standards des leaders du secteur.

## 🎯 Architecture API
- **RESTful Pure** : 100% CRUD + actions spécifiques via @action
- **JWT Authentication** : Tokens avec refresh automatique  
- **Multi-tenant** : Scope automatique par brand via middleware
- **Permissions Granulaires** : IsBrandMember, IsBrandAdmin, IsCompanyAdmin

## 📋 Modules Documentés

### Core Business
- [Business API](../business/api.md) - Authentification, companies, brands, users

### Website Management  
- [Website Core](../websites/core.md) - Sites web et métriques SEO
- [Pages Content](../websites/pages.md) - Contenu et structure des pages
- [Page Builder](../websites/builder.md) - Builder avec CSS Grid
- [SEO Pages](../websites/seo.md) - Optimisation et métriques

### Blog System
- [Blog Content](../blog/content.md) - Articles, auteurs, tags
- [Blog Editor](../blog/editor.md) - Éditeur TipTap avancé  
- [Blog Publishing](../blog/publishing.md) - Workflow de publication
- [Blog Collections](../blog/collections.md) - Dossiers et séries

### SEO Research
- [Keywords Base](../seo/keywords.md) - Base de données mots-clés
- [Semantic Cocoons](../seo/cocoons.md) - Cocons sémantiques

### Task Infrastructure 🔥
- [**Tasks Complete Reference**](./tasks/complete-reference.md) - **VUE D'ENSEMBLE COMPLÈTE**
- [Task Core](./tasks/core.md) - Hub central des tâches
- [Task Monitoring](./tasks/monitoring.md) - Métriques et alertes
- [Task Persistence](./tasks/persistence.md) - Jobs résumables  
- [Task Scheduling](./tasks/scheduling.md) - Planification et cron

### Integrations
- [OpenAI Sync](../integrations/openai.md) - Synchronisation vector stores

### Tools & Utilities
- [File Converter](../tools/converter.md) - Conversion de fichiers
- [URL Shortener](../tools/shortener.md) - Raccourcisseur d'URLs

## 🔑 Standards d'Usage

### Authentication
```http
Authorization: Bearer {jwt_token}





echo "📦 Création ai_core..."
python manage.py startapp ai_core

# Structure obligatoire ai_core
mkdir -p ai_core/{admin,models,serializers,services,views,filters,tests/factories,utils,migrations}
rm ai_core/{admin.py,models.py,views.py,tests.py}

# ===========================================
# 📦 2. CRÉER APP AI_OPENAI  
# ===========================================

echo "📦 Création ai_openai..."
python manage.py startapp ai_openai

# Structure obligatoire ai_openai
mkdir -p ai_openai/{admin,models,serializers,services,views,filters,tests/factories,utils,migrations}
rm ai_openai/{admin.py,models.py,views.py,tests.py}

# ===========================================
# 🏗️ 3. AI_CORE - MODÈLES
# ===========================================

cat > ai_core/models/__init__.py << 'EOF'
# /var/www/megahub/backend/ai_core/models/__init__.py

from .core_models import AIJob, AIJobType, AIJobStatus
from .config_models import AISystemConfig

__all__ = ['AIJob', 'AIJobType', 'AIJobStatus', 'AISystemConfig']
