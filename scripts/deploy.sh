#!/bin/bash
set -euo pipefail

PROJECT_DIR="/var/www/megahub"
FRONTEND_DIR="$PROJECT_DIR/frontend/react-app"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p "$BACKUP_DIR"

log() { echo "[$(date +'%H:%M:%S')] $1"; }
success() { echo "✅ $1"; }
error() { echo "❌ $1"; exit 1; }
react19_log() { echo "🚀 [React 19] $1"; }

log "🚀 Déploiement MegaHub Frontend React 19 v3.0.0"

# Backup
log "📦 Backup de l'ancien build"
if [ -d "$FRONTEND_DIR/dist" ]; then
    tar -czf "$BACKUP_DIR/frontend_backup_$TIMESTAMP.tar.gz" -C "$FRONTEND_DIR" dist
    success "Backup créé: frontend_backup_$TIMESTAMP.tar.gz"
fi

# Pull latest
log "📥 Récupération du code"
cd "$FRONTEND_DIR"
git fetch origin main
git reset --hard origin/main
react19_log "Code React 19 mis à jour"

# Install dependencies avec nouvelle syntaxe npm
log "📦 Installation des dépendances React 19"
npm ci

# Audit security fix
log "🔒 Correction vulnérabilités sécurité"
npm audit fix --force || echo "⚠️ Certaines vulnérabilités nécessitent attention manuelle"

# Type check strict selon standards
log "📝 Vérification TypeScript 5.8.3 strict"
npm run type-check:strict

# Lint (placeholder pour l'instant)
log "🔍 Linting du code"
npm run lint:ci

# Génération routes TanStack
log "🛤️ Génération routes TanStack Router"
npm run routes:generate

# Build production React 19
log "🏗️ Build production React 19 + Lightning CSS"
react19_log "Démarrage build avec React Compiler..."
npm run build

# Vérifier build selon standards
[ ! -d "dist" ] && error "Build échoué - dist manquant"
[ ! -f "dist/index.html" ] && error "Build échoué - index.html manquant"

# Vérifier assets JS générés
JS_FILES=$(find dist/assets -name "*.js" | wc -l)
[ "$JS_FILES" -lt 3 ] && error "Build incomplet - JS files manquants ($JS_FILES trouvés)"

react19_log "Build React 19 réussi - $JS_FILES fichiers JS générés"
log "Taille build: $(du -sh dist | cut -f1)"

# Deploy Docker avec build optimisé
log "🐳 Déploiement Docker React 19"
cd "$PROJECT_DIR"

# Arrêter l'ancien conteneur proprement
docker-compose -f docker-compose.yml stop frontend 2>/dev/null || true
# Build + deploy nouveau conteneur
docker-compose -f docker-compose.yml up -d --build frontend

# ==========================================
# HEALTH CHECK ROBUSTE - STANDARDS LEADERS
# ==========================================

log "🏥 Vérification déploiement production - Approche progressive"

# 1. Attendre démarrage conteneur (initial)
log "⏳ Attente démarrage conteneur initial (15s)..."
sleep 15

# 2. Vérifier que le conteneur est en cours d'exécution
log "🔍 Vérification statut conteneur..."
if ! docker-compose -f docker-compose.yml ps frontend | grep -q "Up\|healthy"; then
    error "Conteneur frontend ne démarre pas correctement"
fi
success "Conteneur frontend démarré"

# 3. Health check INTERNE du conteneur (priorité)
log "🩺 Test health check interne conteneur..."
INTERNAL_HEALTH=""
for i in {1..6}; do
    if INTERNAL_HEALTH=$(docker exec megahub-frontend curl -f http://localhost/health 2>/dev/null); then
        success "Health check interne réussi: $INTERNAL_HEALTH"
        break
    else
        log "⏳ Tentative $i/6 - Health check interne en cours..."
        sleep 10
    fi
done

if [ -z "$INTERNAL_HEALTH" ]; then
    error "Health check interne échoué après 60s - Problème conteneur"
fi

# 4. Attendre nginx-proxy + Let's Encrypt (nécessaire pour SSL)
log "🔐 Attente configuration nginx-proxy + SSL (30s)..."
sleep 30

# 5. Test EXTERNE progressif (HTTP puis HTTPS)
log "🌐 Test health check externe progressif..."

# Test HTTP d'abord (pour diagnostiquer nginx-proxy)
log "📡 Test HTTP externe (diagnostic nginx-proxy)..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://megahub.humari.fr/health 2>/dev/null || echo "000")
log "Status HTTP: $HTTP_STATUS (attendu: 301 redirection vers HTTPS)"

# Test HTTPS principal avec retry robuste
log "🔒 Test HTTPS externe avec retry..."
HTTPS_HEALTH=""
for i in {1..10}; do
    if HTTPS_HEALTH=$(curl -f -s --max-time 10 https://megahub.humari.fr/health 2>/dev/null); then
        success "Health check HTTPS externe réussi: $HTTPS_HEALTH"
        break
    else
        log "⏳ Tentative $i/10 - HTTPS health check en cours..."
        sleep 15
    fi
done

if [ -z "$HTTPS_HEALTH" ]; then
    # Diagnostic approfondi en cas d'échec
    log "🔍 Diagnostic approfondi SSL/HTTPS..."
    
    # Vérifier certificat SSL
    SSL_STATUS=$(echo | timeout 10 openssl s_client -connect megahub.humari.fr:443 -servername megahub.humari.fr 2>/dev/null | grep "Verification:" || echo "SSL_ERROR")
    log "SSL Status: $SSL_STATUS"
    
    # Vérifier nginx-proxy logs
    log "📋 Derniers logs nginx-proxy:"
    docker logs nginx-proxy --tail 5 2>/dev/null || echo "nginx-proxy logs non disponibles"
    
    # Logs du conteneur frontend
    log "📋 Logs conteneur frontend:"
    docker-compose -f docker-compose.yml logs frontend --tail 10
    
    error "Health check HTTPS externe échoué après 150s - Vérifier SSL/nginx-proxy"
fi

# ==========================================
# TESTS PERFORMANCE & VALIDATIONS FINALES
# ==========================================

# Test performance production
log "📊 Test performance production"
RESPONSE_TIME=$(curl -w "%{time_total}" -o /dev/null -s --max-time 15 https://megahub.humari.fr/ 2>/dev/null || echo "ERROR")

if [ "$RESPONSE_TIME" != "ERROR" ]; then
    react19_log "Temps de réponse: ${RESPONSE_TIME}s"
    
    # Validation performance selon standards
    if (( $(echo "$RESPONSE_TIME < 1.0" | bc -l) )); then
        success "Performance excellente (< 1s) ✅"
    elif (( $(echo "$RESPONSE_TIME < 2.0" | bc -l) )); then
        log "⚠️ Performance acceptable (< 2s) - Optimisation possible"
    else
        log "⚠️ Performance lente (> 2s) - Investigation requise"
    fi
else
    log "⚠️ Test performance échoué - Application accessible mais lente"
fi

# Test build info endpoint
log "ℹ️ Vérification build info..."
BUILD_INFO=$(curl -s --max-time 5 https://megahub.humari.fr/build-info 2>/dev/null || echo "N/A")
log "Build Info: $BUILD_INFO"

# Cleanup images
log "🧹 Nettoyage Docker"
docker image prune -f >/dev/null 2>&1

# Status final avec métriques
log "📊 Status final déploiement:"
docker-compose -f docker-compose.yml ps frontend
success "🎉 Déploiement React 19 réussi!"
react19_log "Application disponible: https://megahub.humari.fr"
log "📈 Monitoring continu: docker-compose -f docker-compose.yml logs frontend"
log "🔍 Debugging: docker exec megahub-frontend curl http://localhost/health"
log "⚡ Performance: curl -w '%{time_total}' https://megahub.humari.fr/"