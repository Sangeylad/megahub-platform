# 📚 GUIDE COMPLET - API Websites vs Pages MEGAHUB

## 🎯 Vue d'Ensemble : 2 Endpoints, 2 Responsabilités

MEGAHUB propose **2 endpoints complémentaires** pour gérer sites web et pages avec des responsabilités distinctes :

- **`/websites/`** : Vision **macro** - Dashboard, sélection, analytics sites
- **`/websites/pages/`** : Vision **micro** - CRUD pages, workflow, optimisation SEO

## 🚦 RÈGLES D'USAGE - À RESPECTER IMPÉRATIVEMENT

### ✅ UTILISER `/websites/` QUAND :

#### 1. **Dashboard Principal / Vue d'Ensemble**
```javascript
// KPIs globaux, métriques agrégées par site
GET /websites/?include_stats=true
// → Retourne : pages_count, publication_ratio, keywords_coverage par site
```

#### 2. **Sélection de Site (Navigation)**
```javascript
// Dropdown/sidebar pour choisir un site à travailler
GET /websites/?has_pages=true&brand=9
// → Sites avec contenu pour la brand courante
```

#### 3. **Analytics Cross-Sites**
```javascript
// Benchmark performance entre sites
GET /websites/?performance_vs_category=below&needs_attention=true
// → Sites sous-performants nécessitant action
```

#### 4. **Gestion Sites (Admin)**
```javascript
// CRUD sites uniquement
POST /websites/ → Créer nouveau site
PUT /websites/5/ → Modifier config site
```

#### 5. **Audit Portfolio**
```javascript
// Vue stratégique du portefeuille de sites
GET /websites/?categorization_source=manual&da_above_category=true
// → Sites bien catégorisés avec bon DA
```

---

### ✅ UTILISER `/websites/pages/` QUAND :

#### 1. **Gestion Contenu Pages**
```javascript
// CRUD pages, workflow publication
GET /websites/pages/?website=5&workflow_status=draft
POST /websites/pages/ → Créer nouvelle page
PUT /websites/pages/123/ → Modifier page
```

#### 2. **Optimisation SEO Page par Page**
```javascript
// Pages à optimiser, missing keywords, etc.
GET /websites/pages/?has_meta_description=false&sitemap_priority_max=0.5
// → Pages nécessitant optimisation SEO
```

#### 3. **Workflow Publication**
```javascript
// Gestion éditoriale, validation, planning
GET /websites/pages/?workflow_status=pending_review
PATCH /websites/pages/123/ → {"workflow_status": "published"}
```

#### 4. **Page Builder / Layout**
```javascript
// Interface page builder, sections, design
GET /websites/pages/?has_layout=false&page_type=vitrine
// → Pages à moderniser avec page builder
```

#### 5. **Recherche/Filtrage Avancé**
```javascript
// Tous les 40+ filtres cross-app disponibles
GET /websites/pages/?page_type=blog&has_primary_keyword=false&hierarchy_level=2
```

---

## ❌ ANTI-PATTERNS À ÉVITER

### ❌ NE JAMAIS :

1. **Mélanger les 2 dans un même composant React**
```javascript
// ❌ INTERDIT
const MyComponent = () => {
  const sites = useFetch('/websites/')
  const pages = useFetch('/websites/pages/') // Confusion !
}

// ✅ CORRECT - Composants séparés
const SiteSelector = () => useFetch('/websites/')
const PageManager = () => useFetch('/websites/pages/')
```

2. **Utiliser `/websites/` pour gérer les pages**
```javascript
// ❌ INTERDIT
POST /websites/5/create-page/ // N'existe pas !

// ✅ CORRECT
POST /websites/pages/ {"website": 5}
```

3. **Dupliquer la logique de filtrage**
```javascript
// ❌ INTERDIT - Même filtre sur les 2 endpoints
const filterBothApis = () => {
  fetch('/websites/?has_keywords=true')
  fetch('/websites/pages/?has_keywords=true') // Redondant !
}
```

---

## 🔄 PATTERNS DE NAVIGATION RECOMMANDÉS

### 1. **Workflow Hiérarchique Naturel**
```javascript
// Navigation logique utilisateur
const NavigationFlow = () => {
  // 1. Dashboard → Choisir site à travailler
  const sites = await fetch('/websites/?has_pages=true')
  
  // 2. Site sélectionné → Voir ses pages
  const pages = await fetch(`/websites/pages/?website=${selectedSite.id}`)
  
  // 3. Page sélectionnée → Éditer
  const pageDetail = await fetch(`/websites/pages/${selectedPage.id}/`)
}
```

### 2. **State Management Coordonné**
```javascript
// Zustand stores liés mais séparés
const useSitesStore = create((set, get) => ({
  sites: [],
  currentSite: null,
  setCurrentSite: (site) => {
    set({ currentSite: site })
    // Sync avec pages store
    usePagesStore.getState().loadPagesForSite(site.id)
  }
}))

const usePagesStore = create((set) => ({
  pages: [],
  website: null,
  loadPagesForSite: (websiteId) => {
    set({ website: websiteId, pages: [] })
    // Charger pages du site
  }
}))
```

### 3. **Router Setup Logique**
```javascript
// Routes React Router v5 cohérentes
const AppRoutes = () => (
  <Switch>
    {/* Dashboard sites */}
    <Route path="/dashboard" component={SitesDashboard} />
    
    {/* Détail site */}
    <Route path="/sites/:siteId" component={SiteDetail} />
    
    {/* Pages du site */}
    <Route path="/sites/:siteId/pages" component={PagesList} />
    
    {/* Édition page */}
    <Route path="/pages/:pageId/edit" component={PageEditor} />
  </Switch>
)
```

---

## 🎯 EXEMPLES CONCRETS D'USAGE

### **Cas 1 : Dashboard Principal**
```javascript
// Composant: DashboardSites.jsx
const DashboardSites = () => {
  // ✅ CORRECT - Vue macro avec métriques agrégées
  const { data: sites } = useQuery({
    queryKey: ['sites', 'dashboard'],
    queryFn: () => fetch('/websites/?include_stats=true&brand=9')
  })
  
  return (
    <div className="dashboard-grid">
      {sites.map(site => (
        <SiteCard 
          key={site.id}
          site={site}
          stats={{
            pages_count: site.pages_count,
            publication_ratio: site.publication_ratio,
            performance_score: site.performance_score
          }}
          onSelect={() => navigate(`/sites/${site.id}`)}
        />
      ))}
    </div>
  )
}
```

### **Cas 2 : Gestion Pages d'un Site**
```javascript
// Composant: SitePageManager.jsx
const SitePageManager = ({ siteId }) => {
  // ✅ CORRECT - Vue micro avec filtres détaillés
  const [filters, setFilters] = useState({
    workflow_status: 'draft',
    has_meta_description: false
  })
  
  const { data: pages } = useQuery({
    queryKey: ['pages', siteId, filters],
    queryFn: () => fetch(`/websites/pages/?website=${siteId}&${buildQuery(filters)}`)
  })
  
  return (
    <div>
      <PageFilters filters={filters} onChange={setFilters} />
      <PagesList 
        pages={pages}
        onEdit={(page) => navigate(`/pages/${page.id}/edit`)}
        onPublish={(page) => updatePageStatus(page.id, 'published')}
      />
    </div>
  )
}
```

### **Cas 3 : Audit SEO Cross-Sites**
```javascript
// Composant: SEOAudit.jsx
const SEOAudit = () => {
  // ✅ CORRECT - Analyse cross-sites via /websites/
  const { data: underperformingSites } = useQuery({
    queryKey: ['audit', 'sites'],
    queryFn: () => fetch('/websites/?meta_description_coverage_max=0.5&keywords_coverage_max=0.3')
  })
  
  // ✅ CORRECT - Détail pages problématiques via /websites/pages/
  const { data: problematicPages } = useQuery({
    queryKey: ['audit', 'pages'],
    queryFn: () => fetch('/websites/pages/?has_meta_description=false&workflow_status=published')
  })
  
  return (
    <div className="audit-dashboard">
      <AuditSitesList sites={underperformingSites} />
      <AuditPagesList pages={problematicPages} />
    </div>
  )
}
```

### **Cas 4 : Création de Contenu**
```javascript
// Composant: ContentCreator.jsx
const ContentCreator = () => {
  const [selectedSite, setSelectedSite] = useState(null)
  
  // ✅ CORRECT - Sélection site via /websites/
  const { data: sites } = useQuery({
    queryKey: ['sites', 'creation'],
    queryFn: () => fetch('/websites/?has_page_builder=true')
  })
  
  // ✅ CORRECT - Création page via /websites/pages/
  const createPage = useMutation({
    mutationFn: (pageData) => fetch('/websites/pages/', {
      method: 'POST',
      body: JSON.stringify({
        ...pageData,
        website: selectedSite.id
      })
    })
  })
  
  return (
    <form onSubmit={(data) => createPage.mutate(data)}>
      <SiteSelector 
        sites={sites}
        value={selectedSite}
        onChange={setSelectedSite}
      />
      <PageForm />
    </form>
  )
}
```

---

## 🔍 GUIDE FILTRES PAR ENDPOINT

### **Filtres `/websites/` (54 disponibles)**

#### **Recommandés pour Dashboard/Analytics :**
```bash
# Performance & benchmark
?performance_vs_category=below
?da_above_category=true
?publication_ratio_min=0.8

# Catégorisation & organisation
?primary_category=5
?categorization_source=manual
?has_primary_category=true

# Métriques agrégées
?keywords_coverage_min=0.7
?meta_description_coverage_min=0.8
?has_page_builder=true

# Brand & sync
?needs_openai_sync=true
?has_chatgpt_key=true
```

### **Filtres `/websites/pages/` (40+ disponibles)**

#### **Recommandés pour Gestion Contenu :**
```bash
# Workflow éditorial
?workflow_status=draft
?is_published=false
?status_changed_after=2024-12-01T00:00:00Z

# SEO & optimisation
?has_meta_description=false
?has_primary_keyword=false
?sitemap_priority_max=0.5

# Structure & hiérarchie
?hierarchy_level=2
?has_parent=true
?is_root_page=true

# Page builder & layout
?has_layout=false
?render_strategy=sections
?sections_count_min=3

# Keywords & content
?has_keywords=false
?keyword_type=primary
?is_ai_selected=true
```

---

## 🚀 OPTIMISATIONS PERFORMANCE

### **1. Pagination Intelligente**
```javascript
// Adapter page_size selon l'usage
const PAGE_SIZES = {
  siteSelection: 50,    // Peu nombreux, vue d'ensemble
  pagesList: 25,        // Plus nombreuses, détail
  searchResults: 100,   // Recherche, scan rapide
  mobileView: 10        // Mobile, UX optimisée
}
```

### **2. Cache Stratégique**
```javascript
// Cache différencié par endpoint
const CACHE_DURATIONS = {
  '/websites/': 10 * 60 * 1000,        // 10min - Données sites stable
  '/websites/pages/': 5 * 60 * 1000,   // 5min - Contenu plus dynamique
  '/websites/stats/': 30 * 60 * 1000   // 30min - Métriques lourdes
}
```

### **3. Préchargement Intelligent**
```javascript
// Précharger selon navigation
const useSmartPrefetch = () => {
  const prefetchSitePages = (siteId) => {
    // Précharger pages du site quand site sélectionné
    queryClient.prefetchQuery({
      queryKey: ['pages', siteId],
      queryFn: () => fetch(`/websites/pages/?website=${siteId}`)
    })
  }
}
```

---

## 📋 CHECKLIST DÉVELOPPEMENT

### **Avant Chaque Nouveau Composant :**

- [ ] **Définir le scope** : Site-level ou Page-level ?
- [ ] **Choisir l'endpoint** selon les règles ci-dessus
- [ ] **Vérifier les filtres** disponibles pour l'use case
- [ ] **Planifier la navigation** (hiérarchique ou directe ?)
- [ ] **Configurer le cache** selon la fréquence de changement

### **Structure de Fichiers Recommandée :**
```
src/features/
├── sites-management/          # /websites/ logic
│   ├── components/SiteSelector.jsx
│   ├── components/SitesDashboard.jsx
│   ├── hooks/useSites.js
│   └── services/sitesService.js
├── pages-management/          # /websites/pages/ logic
│   ├── components/PagesList.jsx
│   ├── components/PageEditor.jsx
│   ├── hooks/usePages.js
│   └── services/pagesService.js
└── seo-audit/                 # Cross-endpoint logic
    ├── components/AuditDashboard.jsx
    └── hooks/useAuditData.js
```

---

## 🎯 MÉTRIQUES DE SUCCÈS

### **Indicateurs d'une Bonne Architecture :**
- ✅ **0 duplication** de logique entre composants
- ✅ **Navigation intuitive** : Dashboard → Site → Pages → Page
- ✅ **Performance** : < 200ms pour listes, < 500ms pour dashboards
- ✅ **Réutilisabilité** : Composants utilisables dans différents contextes
- ✅ **Maintenance** : Modifications isolées par responsabilité

---

**🔥 Cette architecture duale optimise les performances tout en gardant une séparation claire des responsabilités. Chaque endpoint excelle dans son domaine sans redondance !**

**Version 1.0 - Architecture Websites/Pages MEGAHUB**  
**Dernière mise à jour : 08/07/2025**