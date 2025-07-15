
# === NAVIGATION RAPIDE ===
alias cdm='cd /var/www/megahub'                           # Racine projet
alias mh='cd /var/www/megahub/frontend/react-app'         # Frontend React 19
alias mhb='cd /var/www/megahub/backend'                   # Backend Django

# === DÉVELOPPEMENT FRONTEND REACT 19 ===
alias dev='cd /var/www/megahub/frontend/react-app && npm run dev'
alias build='cd /var/www/megahub/frontend/react-app && npm run build'
alias preview='cd /var/www/megahub/frontend/react-app && npm run preview'
alias validate='cd /var/www/megahub/frontend/react-app && npm run lint:fix && npm run type-check:strict && npm run test && npm run build'

# === DÉPLOIEMENT ===a# MegaHub - Référence Complète des Aliases & Commandes

> **📍 Fichier de référence** pour tous les raccourcis bash configurés dans le projet MegaHub selon l'architecture des leaders technologiques.

---

## 🧭 Navigation Rapide

| Alias | Commande | Description |
|-------|----------|-------------|
| `cdm` | `cd /var/www/megahub` | Racine du projet |
| `mh` | `cd /var/www/megahub/source/frontend` | Frontend React 19 |
| `mhb` | `cd /var/www/megahub/source/backend` | Backend Django |
| `mhs` | `cd /var/www/megahub/source` | Dossier source complet |

---

## ⚛️ Développement Frontend (React 19)

| Alias | Commande | Description |
|-------|----------|-------------|
| `dev` | `cd .../frontend && npm run dev` | Démarrer serveur de développement |
| `build` | `cd .../frontend && npm run build` | Build production |
| `preview` | `cd .../frontend && npm run preview` | Preview du build |
| `validate` | `lint + typecheck + test + build` | Validation complète avant commit |

---

## 🚀 Déploiement & Environments

| Alias | Commande | Description |
|-------|----------|-------------|
| `deploy` | `./scripts/deploy.sh` | Déploiement production |
| `staging` | `./scripts/deploy-staging.sh` | Déploiement staging |
| `staging-status` | `./scripts/staging-utils.sh status` | Status environnement staging |
| `staging-logs` | `./scripts/staging-utils.sh logs` | Logs staging en temps réel |
| `staging-restart` | `./scripts/staging-utils.sh restart` | Redémarrer staging |

---

## 📁 Gestion des Paths

| Alias | Commande | Description |
|-------|----------|-------------|
| `paths` | `./infrastructure/scripts/update-file-paths.sh` | Met à jour tous les commentaires de paths |

---

## 🌿 Git Workflow

### Aliases Simples
| Alias | Commande | Description |
|-------|----------|-------------|
| `gs` | `git status` | État du repository |
| `ga` | `git add .` | Ajouter tous les fichiers |
| `gp` | `git push origin` | Push vers origin |
| `gpm` | `git push origin main` | Push vers main |
| `gpd` | `git push origin develop` | Push vers develop |
| `gco` | `git checkout` | Changer de branche |
| `gcom` | `git checkout main` | Aller sur main |
| `gcod` | `git checkout develop` | Aller sur develop |
| `gpull` | `git pull origin` | Pull depuis origin |
| `gpm-pull` | `git checkout main && git pull origin main` | Pull main proprement |

### Fonctions Intelligentes
| Fonction | Usage | Description |
|----------|-------|-------------|
| `gc` | `gc message de commit` | Commit avec/sans guillemets |
| `deploy-quick` | `deploy-quick [message]` | Validate + commit + push + deploy |
| `feature` | `feature nom-de-la-feature` | Créer branche feature/ |
| `hotfix` | `hotfix nom-du-hotfix` | Créer branche hotfix/ |

**Exemples d'usage :**
```bash
gc feat: add new page builder              # Sans guillemets
gc "fix: resolve issue with spaces"        # Avec guillemets  
feature drag and drop                       # → feature/drag-and-drop
hotfix critical security patch             # → hotfix/critical-security-patch
deploy-quick hotfix urgent auth bug        # Déploiement rapide personnalisé
```

---

## 🧪 Tests & Validation

| Alias | Commande | Description |
|-------|----------|-------------|
| `test` | `cd .../frontend && npm run test` | Lancer tests |
| `test-watch` | `cd .../frontend && npm run test:watch` | Tests en mode watch |
| `test-coverage` | `cd .../frontend && npm run test:coverage` | Coverage des tests |
| `lint` | `cd .../frontend && npm run lint:fix` | Correction automatique du code |
| `typecheck` | `cd .../frontend && npm run type-check:strict` | Vérification TypeScript stricte |

---

## 📊 Monitoring & Debug

| Alias | Commande | Description |
|-------|----------|-------------|
| `logs-prod` | `docker-compose logs frontend --tail 50 -f` | Logs production |
| `logs-staging` | `docker-compose -f docker-compose.staging.yml logs frontend -f` | Logs staging |
| `health-prod` | `curl -f https://megahub.humari.fr/health` | Health check production |
| `health-staging` | `curl -f https://staging.megahub.humari.fr/health` | Health check staging |
| `perf-prod` | `curl -w "%{time_total}" ...megahub.humari.fr/` | Performance production |
| `perf-staging` | `curl -w "%{time_total}" ...staging.megahub.humari.fr/` | Performance staging |

---

## 🐳 Docker Management

| Alias | Commande | Description |
|-------|----------|-------------|
| `dps` | `docker-compose ps` | Status containers production |
| `dps-staging` | `docker-compose -f docker-compose.staging.yml ps` | Status containers staging |
| `drestart` | `docker-compose restart frontend` | Redémarrer frontend prod |
| `drestart-staging` | `docker-compose -f docker-compose.staging.yml restart frontend` | Redémarrer frontend staging |
| `dclean` | `docker system prune -f && docker image prune -f` | Nettoyer Docker |

---

## 🐍 Backend Django

| Alias | Commande | Description |
|-------|----------|-------------|
| `dbe` | `docker exec -it megahub-backend bash` | Shell backend |
| `dfe` | `docker exec -it megahub-frontend bash` | Shell frontend |
| `dfe-staging` | `docker exec -it megahub-frontend-staging bash` | Shell frontend staging |
| `dmm` | `docker exec -it megahub-backend python manage.py makemigrations` | Créer migrations |
| `dmi` | `docker exec -it megahub-backend python manage.py migrate` | Appliquer migrations |
| `drs` | `docker exec -it megahub-backend python manage.py runserver` | Serveur Django |
| `dct` | `docker exec -it megahub-backend python manage.py test` | Tests Django |
| `dcol` | `docker exec -it megahub-backend python manage.py collectstatic` | Collecter fichiers statiques |
| `dsh` | `docker exec -it megahub-backend python manage.py shell` | Shell Django |
| `dlg` | `docker logs megahub-backend -f` | Logs backend |
| `dre` | `docker-compose restart` | Redémarrer tous les services |

---

## ⚡ Workflow Shortcuts

| Alias | Commande | Description |
|-------|----------|-------------|
| `morning` | `gpm-pull && paths && mh && dev` | Routine matinale complète |

---

## 🔧 Fonctions Utilitaires

| Fonction | Usage | Description |
|----------|-------|-------------|
| `search` | `search terme-à-chercher` | Recherche dans tout le code |
| `status` | `status` | État complet Git + Docker |
| `clean-all` | `clean-all` | Nettoyage complet projet |

**Exemples d'usage :**
```bash
search useAuth                          # Chercher useAuth dans le code
status                                  # Voir état complet du projet
clean-all                               # Nettoyer node_modules + Docker
```

---

## 🎯 Workflows Types

### Développement Quotidien
```bash
morning                                 # Setup matinal
feature new awesome feature             # Nouvelle feature
# ... développement ...
validate                               # Validation complète
gc feat: implement awesome feature      # Commit
gpm                                    # Push
```

### Déploiement Standard
```bash
validate                               # Tests + build
ga                                     # Add changes
gc feat: ready for deployment          # Commit
gpm                                    # Push main
staging                                # Deploy staging first
# ... validation staging ...
deploy                                 # Deploy production
```

### Hotfix Urgent
```bash
hotfix critical security issue         # Branche hotfix
# ... fix urgent ...
deploy-quick hotfix critical security  # Deploy direct
```

### Debug & Monitoring
```bash
health-prod                            # Check production
logs-prod                              # Voir logs
perf-prod                              # Check performance
dps                                    # Status containers
```

---

## 📝 Notes Importantes

- **Tous les alias fonctionnent depuis n'importe quel répertoire**
- **Les fonctions `gc`, `feature`, `hotfix` acceptent les espaces**
- **Architecture conforme aux standards Netflix/Stripe/Airbnb**
- **Paths automatiquement mis à jour avec `paths`**
- **Séparation complète dev/staging/production**

---

*Dernière mise à jour : Architecture Leaders - Janvier 2025*
alias deploy='cd /var/www/megahub && ./scripts/deploy.sh'               # Production
alias staging='cd /var/www/megahub && ./scripts/deploy-staging.sh'      # Staging
alias deploy-quick='validate && git add . && git commit -m "fix: quick update" && git push origin main && deploy'

# === STAGING UTILITIES ===
alias staging-status='cd /var/www/megahub && ./scripts/staging-utils.sh status'
alias staging-logs='cd /var/www/megahub && ./scripts/staging-utils.sh logs'
alias staging-restart='cd /var/www/megahub && ./scripts/staging-utils.sh restart'

# === GIT WORKFLOW ===
alias gs='git status'
alias ga='git add .'
alias gc='git commit -m'
alias gp='git push origin'
alias gpm='git push origin main'
alias gpd='git push origin develop'
alias gco='git checkout'
alias gcom='git checkout main'
alias gcod='git checkout develop'
alias gpull='git pull origin'
alias gpm-pull='git checkout main && git pull origin main'

# === TESTS & VALIDATION ===
alias test='cd /var/www/megahub/frontend/react-app && npm run test'
alias test-watch='cd /var/www/megahub/frontend/react-app && npm run test:watch'
alias test-coverage='cd /var/www/megahub/frontend/react-app && npm run test:coverage'
alias lint='cd /var/www/megahub/frontend/react-app && npm run lint:fix'
alias typecheck='cd /var/www/megahub/frontend/react-app && npm run type-check:strict'

# === MONITORING & DEBUG ===
alias logs-prod='docker-compose logs frontend --tail 50 -f'
alias logs-staging='docker-compose -f docker-compose.staging.yml logs frontend --tail 50 -f'
alias health-prod='curl -f https://megahub.humari.fr/health'
alias health-staging='curl -f https://staging.megahub.humari.fr/health'
alias perf-prod='curl -w "%{time_total}" -o /dev/null https://megahub.humari.fr/'
alias perf-staging='curl -w "%{time_total}" -o /dev/null https://staging.megahub.humari.fr/'

# === DOCKER MANAGEMENT ===
alias dps='docker-compose ps'                             # Status containers
alias dps-staging='docker-compose -f docker-compose.staging.yml ps'
alias drestart='docker-compose restart frontend'          # Restart prod
alias drestart-staging='docker-compose -f docker-compose.staging.yml restart frontend'
alias dclean='docker system prune -f && docker image prune -f'

# === BACKEND DJANGO ===
alias dbe='docker exec -it megahub-backend bash'
alias dfe='docker exec -it megahub-frontend bash'
alias dfe-staging='docker exec -it megahub-frontend-staging bash'
alias dmm='docker exec -it megahub-backend python manage.py makemigrations'
alias dmi='docker exec -it megahub-backend python manage.py migrate'
alias drs='docker exec -it megahub-backend python manage.py runserver'
alias dct='docker exec -it megahub-backend python manage.py test'
alias dcol='docker exec -it megahub-backend python manage.py collectstatic'
alias dsh='docker exec -it megahub-backend python manage.py shell'
alias dlg='docker logs megahub-backend -f'
alias dre='docker-compose restart'

# === WORKFLOW SHORTCUTS ===
alias morning='gpm-pull && mh && dev'                     # Routine matinale
alias feature='function _feature() { gcom && gpull main && gco -b feature/$1; }; _feature'
alias hotfix='function _hotfix() { gcom && gpull main && gco -b hotfix/$1; }; _hotfix'


alias paths='cd /var/www/megahub && ./infrastructure/scripts/update-file-paths.sh'


🎯 Nouveaux Alias Déploiement Créés
🔥 PRODUCTION (4 variants pour familiarisation)
bashdeploy              # Principal (plus court)
deploy-prod         # Explicite
deploy-production   # Complet
deploy-p           # Ultra-court
🧪 STAGING (2 variants)
bashdeploy-staging     # Standard
deploy-s          # Court
🛠️ DEVELOPMENT (3 variants)
bashdeploy-dev         # Standard
deploy-development # Complet
deploy-d          # Court