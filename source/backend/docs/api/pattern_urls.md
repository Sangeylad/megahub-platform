# 📡 MEGAHUB URL PATTERNS GUIDE - Architecture RESTful

## 🎯 Philosophie des URLs MEGAHUB

MEGAHUB utilise une **architecture d'URLs hiérarchique et modulaire** qui reflète l'organisation métier de la plateforme. Chaque système est organisé avec ses sous-modules spécialisés, et l'app **core** agit comme **catch-all** pour les logiques transversales.

---

## 🏗️ Pattern Principal : Système → Spécialisations → Core

### **Structure Type**
```python
path('domain/', include([
    # 🎯 Apps spécialisées AVANT (ordre important !)
    path('specialized-module/', include(('app_specialized.urls', 'app_specialized'), namespace='specialized')),
    path('another-module/', include(('app_another.urls', 'app_another'), namespace='another')),
    
    # 🔧 App CORE en DERNIER (catch-all)
    path('', include(('domain_core.urls', 'domain_core'), namespace='domain')),
])),
```

### **Pourquoi cette structure ?**

1. **Apps spécialisées capturent en premier** : URLs spécifiques traitées par des apps dédiées
2. **Core comme fallback intelligent** : Gère les cas génériques + logiques cross-app
3. **Évolutivité maximale** : Ajouter des spécialisations sans casser l'existant
4. **Cohérence RESTful** : Chaque niveau a sa responsabilité claire

---

## 📋 Patterns par Type de Système

### **🤖 AI Infrastructure - Hub Central**
```python
path('ai/', include([
    # Providers et credentials
    path('', include(('ai_providers.urls', 'ai_providers'), namespace='ai_providers')),
    
    # OpenAI spécifique
    path('openai/', include(('ai_openai.urls', 'ai_openai'), namespace='ai_openai')),
    
    # Usage et métriques
    path('', include(('ai_usage.urls', 'ai_usage'), namespace='ai_usage')),
    
    # 🔧 AI Core en DERNIER (jobs, orchestration)
    path('', include(('ai_core.urls', 'ai_core'), namespace='ai_core')),
])),
```

**Endpoints résultants :**
- `GET /ai/providers/` → Providers disponibles
- `POST /ai/openai/chat/` → Chat OpenAI spécialisé  
- `GET /ai/usage/dashboard/` → Dashboard usage
- `GET /ai/jobs/` → **Core : Tous les jobs IA**
- `GET /ai/dashboard/` → **Core : Dashboard global IA**

### **🌐 Website Management - Structure Complexe**
```python
path('websites/', include([
    # 🔧 FIX: Pages AVANT websites (ordre critique !)
    path('pages/', include(('seo_pages_content.urls', 'seo_pages_content'), namespace='pages')),
    path('builder/', include(('seo_pages_layout.urls', 'seo_pages_layout'), namespace='builder')),
    path('structure/', include(('seo_pages_hierarchy.urls', 'seo_pages_hierarchy'), namespace='structure')),
    path('workflow/', include(('seo_pages_workflow.urls', 'seo_pages_workflow'), namespace='workflow')),
    path('seo/', include(('seo_pages_seo.urls', 'seo_pages_seo'), namespace='seo')),
    path('keywords/', include(('seo_pages_keywords.urls', 'seo_pages_keywords'), namespace='keywords')),
    path('categorization/', include(('seo_websites_categorization.urls', 'seo_websites_categorization'), namespace='categorization')),

    # 🔧 Sites web en DERNIER (catch-all)
    path('', include(('seo_websites_core.urls', 'seo_websites_core'), namespace='sites')),
])),
```

**Endpoints résultants :**
- `GET /websites/pages/` → Pages spécialisées (contenu)
- `GET /websites/builder/` → Layout builder spécialisé
- `GET /websites/seo/` → SEO spécialisé
- `GET /websites/` → **Core : Gestion websites globale**
- `GET /websites/sync-all/` → **Core : Actions cross-pages**

### **🎨 Design System - Modulaire**
```python
path('design/', include([
    # Gestion des couleurs
    path('colors/', include(('brands_design_colors.urls', 'brands_design_colors'), namespace='design_colors')),
    
    # Système typographique  
    path('typography/', include(('brands_design_typography.urls', 'brands_design_typography'), namespace='design_typography')),
    
    # Espacement et layout
    path('spacing/', include(('brands_design_spacing.urls', 'brands_design_spacing'), namespace='design_spacing')),
    
    # Configuration Tailwind
    path('tailwind/', include(('brands_design_tailwind.urls', 'brands_design_tailwind'), namespace='design_tailwind')),
])),
```

**Endpoints résultants :**
- `GET /design/colors/brand-palettes/` → Couleurs spécialisées
- `GET /design/typography/website-configs/` → Typography spécialisée
- `GET /design/tailwind/export-config/` → Export Tailwind spécialisé

### **🏢 Business Extended - Apps Satellites**
```python
path('companies/', include([
    # Gestion des slots et features
    path('slots/', include(('company_slots.urls', 'company_slots'), namespace='company_slots')),
    path('features/', include(('company_features.urls', 'company_features'), namespace='company_features')),
    
    # 🔧 Companies core en DERNIER (catch-all)
    path('', include(('company_core.urls', 'company_core'), namespace='companies')),
])),
```

**Endpoints résultants :**
- `GET /companies/slots/` → Slots spécialisés
- `GET /companies/features/` → Features spécialisées  
- `GET /companies/` → **Core : CRUD companies + logiques cross-apps**
- `GET /companies/{id}/billing-summary/` → **Core : Résumé multi-apps**

---

## 🔧 Importance du Pattern Catch-All

### **❌ Sans Core (Problématique)**
```python
# Chaque app isolée - PAS DE LOGIQUES TRANSVERSALES
path('websites/pages/', include('seo_pages_content.urls')),
path('websites/seo/', include('seo_pages_seo.urls')),  
path('websites/builder/', include('seo_pages_layout.urls')),
# ❌ Aucune vue globale, pas de coordination
```

### **✅ Avec Core (Architecture MEGAHUB)**
```python
path('websites/', include([
    # Apps spécialisées
    path('pages/', include(('seo_pages_content.urls', 'seo_pages_content'), namespace='pages')),
    path('seo/', include(('seo_pages_seo.urls', 'seo_pages_seo'), namespace='seo')),
    
    # 🎯 CORE = Logiques transversales
    path('', include(('seo_websites_core.urls', 'seo_websites_core'), namespace='sites')),
])),
```

**Le Core gère :**
- **Vues globales** : Dashboard consolidé, stats cross-apps
- **Actions transversales** : Sync, import/export multi-apps
- **Filtrage intelligent** : Recherche cross-pages/SEO/builder
- **Orchestration** : Workflows impliquant plusieurs apps

---

## 📝 Template pour Nouveau Système

### **1. Créer la Structure**
```python
# django_app/urls.py

# ========== NOUVEAU SYSTEM ==========
# 📊 Description du système
path('nouveau-system/', include([
    # Module spécialisé 1
    # GET/POST /nouveau-system/module1/ → Fonctionnalités spécifiques
    path('module1/', include(('nouveau_system_module1.urls', 'nouveau_system_module1'), namespace='nouveau_module1')),
    
    # Module spécialisé 2  
    # GET/POST /nouveau-system/module2/ → Autres fonctionnalités
    path('module2/', include(('nouveau_system_module2.urls', 'nouveau_system_module2'), namespace='nouveau_module2')),
    
    # Analytics/métriques (pattern récurrent)
    # GET /nouveau-system/analytics/ → Métriques spécialisées
    path('analytics/', include(('nouveau_system_analytics.urls', 'nouveau_system_analytics'), namespace='nouveau_analytics')),
    
    # 🔧 Core en DERNIER (catch-all pour logiques globales)
    # GET/POST /nouveau-system/ → CRUD principal + vues globales
    # GET /nouveau-system/dashboard/ → Dashboard consolidé
    path('', include(('nouveau_system_core.urls', 'nouveau_system_core'), namespace='nouveau_system')),
])),
```

### **2. URLs Core (Exemple)**
```python
# nouveau_system_core/urls.py

from rest_framework import routers
from .views import NouveauSystemViewSet

router = routers.DefaultRouter()
router.register(r'items', NouveauSystemViewSet, basename='items')

urlpatterns = [
    # Actions spéciales AVANT le router
    path('dashboard/', NouveauSystemViewSet.as_view({'get': 'dashboard'}), name='dashboard'),
    path('cross-modules-sync/', NouveauSystemViewSet.as_view({'post': 'cross_sync'}), name='cross_sync'),
    
    # 🔧 Router en DERNIER (catch-all)
    path('', include(router.urls)),
]
```

---

## 🎯 Bonnes Pratiques

### **1. Nommage des Namespaces**
```python
# ✅ BON - Cohérent et prévisible
('ai_core.urls', 'ai_core'), namespace='ai_core'
('ai_openai.urls', 'ai_openai'), namespace='ai_openai'

# ❌ ÉVITER - Incohérent
('ai_core.urls', 'ai_core'), namespace='ai'
('ai_openai.urls', 'ai_openai'), namespace='openai_stuff'
```

### **2. Organisation des Commentaires**
```python
# ========== SECTION MAJEURE ==========
# 🎯 Description du domaine métier
path('domain/', include([
    # Sous-module avec endpoints principaux
    # GET/POST /domain/sub/ → Description des actions
    # GET /domain/sub/special-action/ → Action spéciale
    path('sub/', include(('domain_sub.urls', 'domain_sub'), namespace='sub')),
    
    # 🔧 Core description
    path('', include(('domain_core.urls', 'domain_core'), namespace='domain')),
])),
```

### **3. Ordre des Paths (CRITIQUE)**
```python
# ✅ CORRECT - Spécifique vers générique
path('websites/', include([
    path('pages/seo/', ...),          # Plus spécifique
    path('pages/', ...),              # Moins spécifique  
    path('', ...),                    # Catch-all (le plus générique)
])),

# ❌ INCORRECT - Catch-all en premier
path('websites/', include([
    path('', ...),                    # ❌ Capture tout !
    path('pages/', ...),              # ❌ Jamais atteint
])),
```

### **4. Apps Core - Responsabilités**
```python
# Dans votre_system_core/views.py

class SystemCoreViewSet(BrandScopedViewSetMixin, ModelViewSet):
    """
    ViewSet Core = Hub du système
    
    Responsabilités :
    - CRUD principal du système
    - Vues globales et dashboards
    - Actions transversales (sync, import/export)
    - Filtrage cross-apps
    - Orchestration workflows complexes
    """
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Dashboard consolidé de TOUT le système"""
        # Agrège données de toutes les apps du système
        
    @action(detail=False, methods=['post'])
    def cross_sync(self, request):
        """Synchronisation entre apps du système"""
        # Orchestre plusieurs apps spécialisées
```

---

## 🚀 Exemples Concrets MEGAHUB

### **Blog System - Multi-Apps**
```python
path('blogs/', include([
    # Configuration blog par website
    path('config/', include(('blog_config.urls', 'blog_config'), namespace='blog_config')),
    
    # Workflow de publication
    path('publishing/', include(('blog_publishing.urls', 'blog_publishing'), namespace='blog_publishing')),
    
    # Collections et organisation
    path('collections/', include(('blog_collections.urls', 'blog_collections'), namespace='blog_collections')),
    
    # Éditeur avancé
    path('editor/', include(('blog_editor.urls', 'blog_editor'), namespace='blog_editor')),
    
    # 🔧 Contenu de base en dernier (catch-all)
    path('', include(('blog_content.urls', 'blog_content'), namespace='blog_content')),
])),
```

**Résultat :**
- `POST /blogs/config/` → Configuration spécialisée
- `GET /blogs/publishing/dashboard/` → Workflow spécialisé
- `GET /blogs/collections/` → Collections spécialisées
- `GET /blogs/` → **Core : Tous les articles, vues globales**
- `GET /blogs/cross-website-stats/` → **Core : Stats cross-websites**

### **Templates IA - Structure Avancée**
```python
path('templates/', include([
    # Templates spécialisés SEO
    path('seo/', include(('seo_websites_ai_templates_content.urls', 'seo_websites_ai_templates_content'), namespace='template_seo')),
    
    # Workflow et validation
    path('workflow/', include(('ai_templates_workflow.urls', 'ai_templates_workflow'), namespace='template_workflow')),
    
    # Analytics et métriques
    path('analytics/', include(('ai_templates_analytics.urls', 'ai_templates_analytics'), namespace='template_analytics')),
    
    # Variables et versioning
    path('storage/', include(('ai_templates_storage.urls', 'ai_templates_storage'), namespace='template_storage')),
    
    # Organisation et catégories
    path('categories/', include(('ai_templates_categories.urls', 'ai_templates_categories'), namespace='template_categories')),
    
    # 🔧 Core templates en DERNIER (catch-all)
    path('', include(('ai_templates_core.urls', 'ai_templates_core'), namespace='templates')),
])),
```

**Résultat :**
- `GET /templates/seo/` → Templates SEO spécialisés
- `GET /templates/workflow/approvals/` → Workflow spécialisé
- `GET /templates/analytics/usage-metrics/` → Analytics spécialisées
- `GET /templates/` → **Core : Tous les templates, CRUD principal**
- `POST /templates/{id}/duplicate/` → **Core : Actions génériques**

---

## 🔍 Debugging des URLs

### **Commande de Test**
```bash
# Voir toutes les URLs
python manage.py show_urls

# Tester un pattern spécifique
python manage.py show_urls | grep "websites"

# Debug ordre des paths
python manage.py show_urls --format table
```

### **Test Manuel**
```python
# Dans le shell Django
from django.urls import reverse, resolve

# Tester la résolution
resolve('/websites/pages/')          # → seo_pages_content
resolve('/websites/seo/')            # → seo_pages_seo  
resolve('/websites/')                # → seo_websites_core (catch-all)
resolve('/websites/dashboard/')      # → seo_websites_core (action du core)

# Tester la génération
reverse('pages:page-list')           # → /websites/pages/
reverse('sites:website-dashboard')   # → /websites/dashboard/
```

---

## 📊 Métriques de Qualité

### **Checklist Nouveau Système**

- [ ] **Structure hiérarchique** : Domain → Spécialisations → Core
- [ ] **Apps spécialisées AVANT core** dans les paths
- [ ] **Namespaces cohérents** : nom_app = namespace
- [ ] **Commentaires explicatifs** avec endpoints principaux
- [ ] **Core en catch-all** pour logiques transversales
- [ ] **Ordre des paths testé** (spécifique → générique)
- [ ] **Responsabilités claires** entre apps spécialisées et core

### **Signaux d'Alerte**

🚨 **À éviter :**
- Core en premier dans les paths
- Namespaces incohérents ou absents
- Apps spécialisées sans responsabilité claire
- Logiques transversales dans les apps spécialisées
- URLs plates sans hiérarchie logique

---

## 🏁 Conclusion

L'architecture d'URLs MEGAHUB permet :

1. **Évolutivité maximale** : Ajouter des spécialisations sans impact
2. **Cohérence métier** : URLs qui reflètent l'organisation business  
3. **Logiques transversales** : Core apps pour orchestration
4. **Maintenabilité** : Structure prévisible et documentée
5. **Performance** : Routage efficace vers les bonnes apps

**Cette architecture n'est pas une suggestion, c'est le standard MEGAHUB.** 🚀

---

**📌 À consulter avant chaque ajout de système, pendant le développement, après chaque refactoring d'URLs.**