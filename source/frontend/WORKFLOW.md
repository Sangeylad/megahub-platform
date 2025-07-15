# 🚀 MEGAHUB - Workflow Quotidien Final 2025 (Architecture Leaders)

## 🌍 **ENVIRONNEMENTS & URLs**

```bash
🏠 DEV LOCAL      : localhost:3000              # Hot reload instantané ⚡
🔧 DEV CONTAINER  : localhost:3000              # Test intégration Docker
🧪 STAGING        : staging.megahub.humari.fr  # Preview associé
🚀 PRODUCTION     : megahub.humari.fr          # Public live
📡 API BACKEND    : backoffice.humari.fr       # Django API
```

---

## ⚡ **COMMANDES QUOTIDIENNES**

### **🌅 1. DÉMARRER LA SESSION DEV (5 min)**

```bash

# Aller dans le projet (NOUVEAU CHEMIN)
cd /var/www/megahub

# Démarrer infrastructure backend (1x par session)
docker-compose -p megahub-dev -f docker-compose.yml up -d backend postgres redis

# Démarrer frontend en local (HOT RELOAD)
cd source/frontend
git pull origin main                           # Sync dernière version
npm run dev                                    # 🚀 localhost:3000 ⚡
```

### **🎨 2. DÉVELOPPEMENT (Hot Reload Magic)**

```bash
# VSCode : Éditer code dans source/frontend/src/
# Browser : localhost:3000 → changements instantanés < 30ms ✅
# Terminal : Voir logs en temps réel

# Pas besoin de rebuild/restart ! HMR automatique 🔥
```

### **✅ 3. VALIDATION AVANT COMMIT**

```bash
# Dans source/frontend/
npm run lint:fix                              # Auto-correction style
npm run type-check:strict                     # TypeScript ultra-strict
npm run test                                  # Tests complets  
npm run build                                 # Test build production
# Si tout ✅ → OK pour commit
```

### **📝 4. COMMIT (Convention Leaders)**

```bash
git add .
git commit -m "feat(page-builder): add drag & drop components

- Implement react-beautiful-dnd with React 19
- Add visual feedback for drop zones with Lightning CSS
- Update TypeScript 5.8+ strict types
- Test coverage: 95% → 97%
- Bundle optimization: -15kb gzipped

Closes #MB-245"

git push origin main                          # Push vers GitHub
```

### **🧪 5. DEPLOY STAGING (Preview Associé)**

```bash
# Merge vers develop pour staging
git checkout develop && git merge main && git push origin develop

# Deploy staging avec nouveau script ⚡
./scripts/deploy-env.sh staging

# ✅ Résultat automatique :
# - Git pull develop
# - Build React 19 + Lightning CSS  
# - Docker build + deploy
# - Collectstatic (168 fichiers)
# - Health checks complets
# - URL: staging.megahub.humari.fr
```

### **🚀 6. DEPLOY PRODUCTION**

```bash
# Retour sur main et deploy
git checkout main && git push origin main

# Deploy production sécurisé
./scripts/deploy-env.sh production
# ↑ Demande confirmation "PRODUCTION" pour sécurité

# ✅ Résultat : megahub.humari.fr live !
```

---

## 🎯 **NOUVEAUX SCRIPTS MULTI-ENVIRONNEMENTS**

### **⚡ Scripts de Déploiement**

```bash
# Deploy un environnement
./scripts/deploy-env.sh {development|staging|production}

# Deploy plusieurs environnements
./scripts/deploy-all.sh sequential           # Dev → Staging → Prod
./scripts/deploy-all.sh parallel            # Tous en parallèle
./scripts/deploy-all.sh staging-prod        # Staging + Prod seulement
./scripts/deploy-all.sh interactive         # Menu interactif

# Utilitaires multi-env
./scripts/utils-multi-env.sh status         # Status tous environnements
./scripts/utils-multi-env.sh health         # Health check complet
./scripts/utils-multi-env.sh logs staging   # Logs d'un environnement
./scripts/utils-multi-env.sh shell staging backend  # Shell dans container
```

### **📊 Commandes de Monitoring**

```bash
# Status complet multi-environnements
./scripts/utils-multi-env.sh status

# Health check tous environnements
./scripts/utils-multi-env.sh health

# Voir logs en temps réel
./scripts/utils-multi-env.sh logs staging
./scripts/utils-multi-env.sh logs production
```

---

## 📋 **CONVENTIONS DE COMMIT (Standards Leaders)**

### **🎯 Types de Commit**

```bash
feat(scope): description courte               # Nouvelle fonctionnalité
fix(scope): description courte                # Correction de bug  
perf(scope): description courte               # Performance (+React 19)
docs(scope): description courte               # Documentation
test(scope): description courte               # Tests + coverage
refactor(scope): description courte           # Refactorisation
build(scope): description courte              # Build/Lightning CSS
ci(scope): description courte                 # CI/CD scripts
```

### **🎯 Scopes MegaHub 2025**

```bash
(auth)          # Authentification JWT
(ui)            # Interface utilisateur React 19
(api)           # Intégration API Django
(page-builder)  # Page builder TanStack
(seo)           # SEO + React 19 Server Components
(perf)          # Performance + Lightning CSS
(mobile)        # Responsive + React 19 optimizations
(a11y)          # Accessibilité WCAG 2.1
(deploy)        # Scripts déploiement
(docker)        # Configuration Docker
```

---

## 🛠️ **WORKFLOWS PAR TYPE DE FEATURE**

### **🏃 FEATURE QUOTIDIENNE (Standard)**

```bash
# 1. Dev local avec hot reload
cd /var/www/megahub/source/frontend
npm run dev                                   # localhost:3000 ⚡

# 2. Développement + validation
# ... coding ...
npm run lint:fix && npm run test && npm run build

# 3. Commit + deploy direct production
git add . && git commit -m "feat(ui): improve button styles"
git push origin main
./scripts/deploy-env.sh production           # megahub.humari.fr
```

### **👥 FEATURE COLLABORATIVE (Avec Preview)**

```bash
# 1. Développement local
cd /var/www/megahub/source/frontend && npm run dev

# 2. Staging pour review associé
git checkout develop && git merge main && git push origin develop
./scripts/deploy-env.sh staging             # staging.megahub.humari.fr
# 📱 Message : "Feature prête ! Test ici : staging.megahub.humari.fr"

# 3. Validation associé → Production
git checkout main && git push origin main
./scripts/deploy-env.sh production          # megahub.humari.fr
```

### **🧪 FEATURE EXPÉRIMENTALE (Branch)**

```bash
# 1. Branche feature
git checkout -b feature/ai-chat-v2
# ... développement sur localhost:3000 ...

# 2. Test staging branche
git push -u origin feature/ai-chat-v2
git checkout develop && git merge feature/ai-chat-v2
./scripts/deploy-env.sh staging

# 3. Si validé → merge main
git checkout main && git merge feature/ai-chat-v2
./scripts/deploy-env.sh production
```

---

## 🚨 **RECOVERY & MAINTENANCE**

### **🔄 Infrastructure nginx-proxy**

```bash
# Démarrer nginx-proxy (reverse proxy + SSL)
cd /var/www/megahub/infrastructure
docker-compose up -d

# Vérifier SSL + redirections
curl -I https://staging.megahub.humari.fr/health
curl -I https://megahub.humari.fr/health
```

### **🔥 Rollback Urgence**

```bash
# Voir backups disponibles
ls -la /var/www/megahub/backups/ | grep frontend

# Rollback Git rapide
cd /var/www/megahub/source
git log --oneline -5                         # Voir derniers commits
git reset --hard HEAD~1                     # Revenir 1 commit en arrière
./scripts/deploy-env.sh production          # Redeploy
```

### **⚡ Fix Performance**

```bash
# Redémarrer tous les environnements
./scripts/utils-multi-env.sh restart all

# Nettoyer Docker (libérer espace)
docker system prune -af && docker volume prune -f

# Rebuild complet si problème
./scripts/deploy-all.sh sequential
```

---

## 📊 **MÉTRIQUES & STANDARDS 2025**

### **✅ Standards à Respecter**

```bash
✅ TypeScript strict     : 0% any autorisé (5.8.3)
✅ Test coverage         : > 95% (Vitest)
✅ Bundle size           : < 280kb gzipped (React 19 + Lightning CSS)
✅ Build time            : < 1.2s (Lightning CSS optimized)
✅ HMR                   : < 30ms (React 19 Fast Refresh)
✅ First load            : < 650ms (nginx + cache + React Compiler)
✅ Lighthouse score      : > 98 (React 19 Server Components ready)
✅ Collectstatic         : 168 fichiers automatique
✅ Security vulns        : 0 high/critical (npm audit)
```

### **📈 Commandes de Validation**

```bash
# Performance & Qualité
npm run build:analyze                        # Bundle analyzer
npm run test:coverage                        # Coverage tests 95%+
npm audit --audit-level moderate             # Sécurité packages
npm run type-check:strict                    # TypeScript ultra-strict

# Production testing
curl -w "%{time_total}" https://megahub.humari.fr/  # < 650ms target
curl -f https://megahub.humari.fr/health     # Health check production
```

---

## 🔗 **ARCHITECTURE TECHNIQUE 2025**

### **📦 Stack Frontend (React 19 + Leaders)**

```bash
⚡ React 19.1.0          # Server Components + Actions + Compiler
⚡ TypeScript 5.8.3      # Strict mode + nouvelles inférences  
⚡ TanStack Router v1.127 # File-based routing + preloading
⚡ TanStack Query v5.82  # Suspense native + 20% bundle reduction
⚡ Vite 6.3.5            # Lightning CSS + build ultra-rapide
⚡ Tailwind CSS v4       # CSS-first + moteur Oxide
⚡ Biome 2.1.1           # Linter/formatter Rust ultra-performant
```

### **🐳 Stack Infrastructure**

```bash
🐳 Docker Compose       # Multi-environnements avec project names
🔒 nginx-proxy          # Reverse proxy + SSL Let's Encrypt auto
🐍 Django 4.2           # Backend API + collectstatic automatique
🗄️ PostgreSQL 15        # Database principal + staging séparé
⚡ Redis 7               # Cache + sessions
🚀 Debian 12            # OS serveur optimisé
```

---

## 🎯 **COMMANDES EXPRESS (Copy/Paste)**

### **⚡ Dev Session Complète**

```bash
# Setup complet session dev (copy/paste)
ssh debian@vps-64d4da2a.osc-fr1.scaleway.com
cd /var/www/megahub
docker-compose -p megahub-dev -f docker-compose.yml up -d backend postgres redis
cd source/frontend && git pull origin main && npm run dev
# ↑ localhost:3000 prêt avec hot reload ⚡
```

### **🚀 Deploy Production Express**

```bash
# Deploy production complet (copy/paste)
cd /var/www/megahub
git add . && git commit -m "feat: update" && git push origin main
./scripts/deploy-env.sh production
# ↑ megahub.humari.fr mis à jour automatiquement
```

### **🧪 Test Staging Rapide**

```bash
# Deploy staging pour test (copy/paste)
cd /var/www/megahub && git checkout develop && git merge main && git push origin develop
./scripts/deploy-env.sh staging
echo "Test ici : https://staging.megahub.humari.fr"
```

---

## 💡 **ALIASES PRODUCTIVITÉ**

### **Ajouter dans ~/.bashrc**

```bash
# Navigation MegaHub
alias mh='cd /var/www/megahub'
alias mhf='cd /var/www/megahub/source/frontend'
alias mhb='cd /var/www/megahub/source/backend'

# Développement
alias dev='npm run dev'
alias build='npm run build'
alias test='npm run test'
alias lint='npm run lint:fix'

# Déploiements
alias deploy-dev='cd /var/www/megahub && ./scripts/deploy-env.sh development'
alias deploy-staging='cd /var/www/megahub && ./scripts/deploy-env.sh staging'
alias deploy-prod='cd /var/www/megahub && ./scripts/deploy-env.sh production'
alias deploy-all='cd /var/www/megahub && ./scripts/deploy-all.sh'

# Monitoring
alias mh-status='cd /var/www/megahub && ./scripts/utils-multi-env.sh status'
alias mh-health='cd /var/www/megahub && ./scripts/utils-multi-env.sh health'
alias mh-logs='cd /var/www/megahub && ./scripts/utils-multi-env.sh logs'

# Usage après aliases :
# mhf && dev              # → Dev session localhost:3000
# deploy-prod             # → Deploy production  
# mh-status               # → Status multi-env
```

---

## 📱 **MESSAGES TYPES ASSOCIÉ**

```bash
"✨ Nouvelle feature prête ! Preview : staging.megahub.humari.fr"
"🚀 Version live mise à jour : megahub.humari.fr"  
"🔧 Bug fix urgent déployé : megahub.humari.fr"
"📊 Dashboard mis à jour avec métriques temps réel"
"⚡ Performance améliorée : -150ms de chargement"
"🎉 Release v3.1.0 déployée avec [liste features]"
```

---

## 🔍 **DEBUG RAPIDE**

### **Health Checks Instantanés**

```bash
# Status infrastructure complet
./scripts/utils-multi-env.sh health

# URLs individuelles
curl -f https://megahub.humari.fr/health && echo " ✅ Production OK"
curl -f https://staging.megahub.humari.fr/health && echo " ✅ Staging OK"  
curl -f http://localhost:3000 && echo " ✅ Dev local OK"
```

### **Performance Quick Check**

```bash
# Temps de réponse production
curl -w "Temps: %{time_total}s\n" -o /dev/null -s https://megahub.humari.fr/

# Taille bundle (doit être < 280kb)
cd /var/www/megahub/source/frontend && npm run build:analyze

# Logs erreurs récentes
docker logs megahub-backend-prod --tail 20 | grep ERROR
```

---

## 🎉 **RÉCAPITULATIF : TON WORKFLOW OPTIMAL**

### **📅 Quotidien (90% du temps)**
```bash
1. ssh + cd /var/www/megahub/source/frontend
2. npm run dev                    # localhost:3000 ⚡
3. Code + save → voir changements instantanés
4. git commit + push + deploy-prod quand prêt
```

### **🔄 Hebdomadaire (testing associé)**
```bash
1. Deploy staging pour preview
2. Validation associé
3. Deploy production final
```

### **🚀 Monthly (maintenance)**
```bash
1. npm audit + update packages
2. Health checks complets  
3. Performance optimization
4. Backup verification
```

---

**🎯 Ce workflow = architecture leaders 2025 avec React 19 + Lightning CSS + multi-environnements + scripts automatisés !**

*Sauvegarde dans `/var/www/megahub/WORKFLOW-2025.md`*


🔄 WORKFLOW A : Développement sur Develop (Sans Toucher Main)
Si tu veux tester en staging SANS toucher main :
bash# 1. Développer directement sur develop
git checkout develop
# ... développement en local ...
git add . && git commit -m "feat: nouvelle feature"
git push origin develop              # ← Push DEVELOP (pas main !)

# 2. Deploy staging direct
./scripts/deploy-env.sh staging      # staging.megahub.humari.fr

# 3. Main reste intact pour prod
# megahub.humari.fr = version actuelle inchangée

# 4. Si feature validée, merger vers main
git checkout main
git merge develop                    # main récupère develop
git push origin main
./scripts/deploy-env.sh production   # megahub.humari.fr
🔄 WORKFLOW B : Développement sur Main (Simple)
Si tu développes sur main (workflow simple) :
bash# 1. Développer sur main
git checkout main
# ... développement ...
git add . && git commit -m "feat: nouvelle feature"  
git push origin main                 # ← Push MAIN

# 2. Pour tester en staging, synchroniser develop
git checkout develop
git merge main                       # develop récupère main
git push origin develop
./scripts/deploy-env.sh staging

# 3. Prod depuis main (déjà à jour)
./scripts/deploy-env.sh production