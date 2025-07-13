# Humari Tools WordPress Plugin

Plugin WordPress pour intégrer les outils publics MegaHub et le glossaire business dans WordPress.

## 🎯 **Vue d'ensemble**

Ce plugin offre une intégration complète entre WordPress et les services MegaHub :
- **Outils publics** : Convertisseur, raccourcisseur d'URL, optimiseur de fichiers, calculateur ROAS
- **Glossaire business** : 60+ termes avec pages dédiées et système de rappel intelligent
- **Architecture sécurisée** : API Django invisible côté client

## 📦 **Installation**

1. **Copier le plugin**
   ```bash
   # Copier le dossier dans /wp-content/plugins/
   cp -r humari-tools /wp-content/plugins/
   ```

2. **Activer le plugin**
   - Aller dans WordPress Admin → Extensions
   - Activer "Humari Tools"

3. **Configurer les permaliens**
   - Aller dans Réglages → Permaliens
   - Cliquer sur "Enregistrer" (pour activer les rewrite rules du glossaire)

## 🛠️ **Outils Publics**

### **Convertisseur de Documents**
```php
[humari_tool tool="converter" category="document"]
```
- Conversion PDF, DOCX, TXT, etc.
- Support multi-fichiers
- Téléchargement asynchrone

### **Raccourcisseur d'URL**
```php
[humari_tool tool="shortener" category="web"]
```
- URLs courtes personnalisées
- Statistiques de clics
- QR codes automatiques

### **Optimiseur de Fichiers**
```php
[humari_tool tool="optimizer" category="file"]
```
- Compression images (JPEG, PNG, WebP)
- Optimisation PDF
- Redimensionnement intelligent

### **Calculateur ROAS**
```php
[humari_tool tool="roas-calculator" category="ecommerce"]
```
- Calcul retour sur investissement publicitaire
- Scénarios multiples
- Export des résultats

### **Simulateur Immobilier** *(À venir)*
```php
[humari_tool tool="simulator" category="real-estate"]
```

## 📚 **Glossaire Business**

### **Pages Dédiées (SEO-Friendly)**

Le plugin crée automatiquement des pages avec URLs propres :

```
https://monsite.com/glossaire/                           # Hub principal
https://monsite.com/glossaire/marketing-digital/        # Page catégorie  
https://monsite.com/glossaire/marketing-digital/beroas/ # Page terme
https://monsite.com/glossaire/recherche/                # Page recherche
```

**Fonctionnalités SEO :**
- ✅ Meta titles/descriptions dynamiques
- ✅ Structured data (JSON-LD)
- ✅ Breadcrumb automatique
- ✅ Sitemap intégré
- ✅ Cache optimisé (1-2h)

### **Shortcodes d'Intégration**

#### **Hub Glossaire**
```php
[humari_glossary_hub show_categories="true" show_popular="true" popular_limit="10"]
```

#### **Page Catégorie**
```php
[humari_glossary_category slug="marketing-digital" terms_per_page="20"]
```

#### **Terme Individuel**
```php
[humari_glossary_term slug="beroas" show_related="true" show_examples="true"]
```

#### **Recherche**
```php
[humari_glossary_search placeholder="Rechercher un terme..." auto_search="true"]
```

#### **Termes Populaires**
```php
[humari_glossary_popular limit="5" layout="inline" title="🔥 Termes populaires"]
```

#### **Termes Essentiels**
```php
[humari_glossary_essential category="seo" layout="cards" title="📚 Essentiels SEO"]
```

## 💡 **Système de Rappel Intelligent**

### **Shortcode de Rappel**
```php
[humari_glossary_recall term="beroas" style="block" link="dofollow"]
```

### **Paramètres Disponibles**

| Paramètre | Valeurs | Défaut | Description |
|-----------|---------|---------|-------------|
| `term` | `string` | - | **Obligatoire** - Slug du terme |
| `style` | `block`, `inline`, `tooltip`, `card` | `block` | Style d'affichage |
| `link` | `dofollow`, `nofollow`, `none` | `dofollow` | Contrôle SEO du lien |
| `definition_length` | `number` | `100` | Caractères de définition |
| `show_category` | `true`, `false` | `true` | Afficher la catégorie |
| `custom_text` | `string` | - | Texte personnalisé du lien |
| `css_class` | `string` | - | Classes CSS additionnelles |

### **Styles Visuels**

#### **Style Block** (Défaut)
```php
[humari_glossary_recall term="roi" style="block" link="dofollow"]
```
→ Bloc de rappel avec icône, définition et lien

#### **Style Inline**
```php
Le [humari_glossary_recall term="cpc" style="inline" link="dofollow"] est un indicateur clé.
```
→ Terme surligné dans le texte

#### **Style Tooltip**
```php
Calculez votre [humari_glossary_recall term="ltv" style="tooltip" link="dofollow"] avant d'investir.
```
→ Infobulle au survol

#### **Style Card**
```php
[humari_glossary_recall term="beroas" style="card" link="dofollow" show_category="true"]
```
→ Carte visuelle avec header coloré

## 🎯 **Stratégie SEO Avancée**

### **Maillage Interne Intelligent**

```php
<!-- Articles de blog → Glossaire (dofollow) -->
[humari_glossary_recall term="seo" link="dofollow"]

<!-- Pages service → Définitions (nofollow pour éviter dilution) -->
[humari_glossary_recall term="leads" link="nofollow"]

<!-- Définition sans lien (éviter sur-optimisation) -->
[humari_glossary_recall term="kpi" link="none"]
```

### **Variation des Ancres**

```php
<!-- Éviter la sur-optimisation avec des ancres variées -->
[humari_glossary_recall term="roas" custom_text="retour sur investissement publicitaire"]
[humari_glossary_recall term="roas" custom_text="ROAS"]
[humari_glossary_recall term="roas" custom_text="rentabilité publicitaire"]
```

## 📊 **Données Disponibles**

### **16 Catégories Hiérarchiques**
- **Marketing Digital** (SEO, Publicité, Automation, Analytics)
- **Sales** (Prospection, Négociation, CRM)
- **Business & Strategy** (Analyse, Stratégie, Management)
- **Tech & Data** (Développement, Data Science)

### **60+ Termes Essentiels**
- **SEO** : BEROAS, SERP, Backlink, Maillage interne
- **Marketing** : Inbound, Buyer Persona, Lead Magnet, ROAS
- **Sales** : Pipeline, Qualification BANT, Closing
- **Business** : LTV, CAC, MRR, Churn Rate
- **Analytics** : KPI, Dashboard, Conversion Rate

## ⚙️ **Configuration**

### **Variables d'Environnement**

```php
// humari-tools.php
define('HUMARI_TOOLS_API_BASE', 'https://backoffice.humari.fr/public-tools/');
```

### **Cache WordPress**

```php
// Cache adaptatif par type de contenu :
// - Catégories : 2h (changent peu)
// - Termes : 1h (plus dynamiques)
// - Recherches : 30min (très dynamiques)
// - Stats : 30min (calculs coûteux)
```

### **Rate Limiting**

```php
// Respect du rate limiting Django :
// - Lecture générale : 1000/heure
// - Recherches : 300/heure  
// - Statistiques : 100/heure
```

## 🔧 **Personnalisation CSS**

### **Classes CSS Disponibles**

```css
/* Outils publics */
.humari-tool-container { }
.conversion-results { }
.shortener-results { }
.optimizer-results { }

/* Glossaire */
.humari-glossary-hub { }
.humari-glossary-category { }
.humari-glossary-term { }
.categories-grid { }
.category-card { }
.term-header { }
.search-results-list { }

/* Rappels */
.humari-glossary-recall.style-block { }
.humari-glossary-recall.style-inline { }
.humari-glossary-recall.style-tooltip { }
.humari-glossary-recall.style-card { }
```

### **Personnalisation Avancée**

```php
// Ajouter des classes personnalisées
[humari_glossary_recall term="roi" css_class="highlight-important"]

// Modifier la longueur des définitions
[humari_glossary_recall term="cpc" definition_length="150"]

// Désactiver la catégorie
[humari_glossary_recall term="seo" show_category="false"]
```

## 🚀 **Exemples d'Usage**

### **Article de Blog Marketing**

```php
Dans cet article, nous allons explorer le [humari_glossary_recall term="inbound-marketing" style="inline" link="dofollow"] et son impact sur la génération de leads.

[humari_glossary_recall term="buyer-persona" style="block" link="dofollow"]

Pour mesurer l'efficacité de vos campagnes, calculez votre [humari_glossary_recall term="roas" style="tooltip" link="dofollow"] régulièrement.

[humari_tool tool="roas-calculator" category="ecommerce"]
```

### **Page Service SEO**

```php
Nos services SEO vous aident à améliorer votre [humari_glossary_recall term="serp" style="inline" link="nofollow"] et votre visibilité organique.

[humari_glossary_essential category="seo" layout="cards" title="Concepts SEO fondamentaux"]

Utilisez notre convertisseur pour optimiser vos documents :
[humari_tool tool="converter" category="document"]
```

### **Landing Page Glossaire**

```php
[humari_glossary_hub show_categories="true" show_popular="true" popular_limit="8"]

[humari_glossary_search placeholder="Que recherchez-vous ?" auto_search="true"]
```

## 🐛 **Dépannage**

### **URLs du Glossaire ne Fonctionnent Pas**
```bash
# Solution : Réinitialiser les permaliens
WordPress Admin → Réglages → Permaliens → Enregistrer
```

### **Erreur "Terme non trouvé"**
```bash
# Vérifier que l'API Django est accessible
curl https://backoffice.humari.fr/public-tools/glossaire/terms/by-slug/beroas/
```

### **Cache Problématique**
```php
// Forcer le rafraîchissement du cache
delete_transient('humari_glossary_term_beroas_fr_');
```

### **Logs des Erreurs**
```php
// Activer les logs dans wp-config.php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);

// Vérifier : /wp-content/debug.log
```

## 📈 **Roadmap**

### **Version 1.1** *(Prochaine)*
- [ ] Simulateur immobilier fonctionnel
- [ ] Export PDF des termes glossaire
- [ ] Intégration Google Analytics pour tracking
- [ ] Mode hors ligne avec cache étendu

### **Version 1.2** *(Future)*
- [ ] Glossaire multilingue (EN, ES)
- [ ] Système de favoris utilisateur
- [ ] API REST WordPress pour le glossaire
- [ ] Intégration Elementor widgets

### **Version 2.0** *(Long terme)*
- [ ] IA pour suggestions de termes contextuels
- [ ] Système de commentaires sur les définitions
- [ ] Glossaire collaboratif
- [ ] Analytics avancées d'utilisation

## 🔗 **Liens Utiles**

- **API Documentation** : https://backoffice.humari.fr/api/docs/
- **Support** : contact@humari.fr
- **Changelog** : /CHANGELOG.md
- **Repository** : Interne MegaHub

## 📄 **Licence**

Propriétaire - Humari © 2025

---

**Plugin Version :** 1.0.0  
**Testé jusqu'à :** WordPress 6.4  
**Requires PHP :** 7.4+  
**Auteur :** Équipe Humari