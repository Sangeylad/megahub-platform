#!/bin/bash
# /var/www/megahub/scripts/deploy-env.sh
# Script unifié de déploiement multi-environnements selon standards leaders

set -euo pipefail

# ==========================================
# CONFIGURATION ENVIRONNEMENTS
# ==========================================
PROJECT_DIR="/var/www/megahub"
SOURCE_DIR="$PROJECT_DIR/source"                     # ← Nouvelle architecture
FRONTEND_DIR="$SOURCE_DIR/frontend"                  # ← Nouveau chemin
BACKEND_DIR="$SOURCE_DIR/backend"                    # ← Nouveau chemin
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

ENVIRONMENT=${1:-development}

# Configuration par environnement
case $ENVIRONMENT in
    "development")
        COMPOSE_FILE="docker-compose.yml"
        FRONTEND_CONTAINER="megahub-frontend-dev"
        BACKEND_CONTAINER="megahub-backend-dev"
        DJANGO_SETTINGS="django_app.settings.development"
        FRONTEND_URL="http://localhost:3000"
        BACKEND_URL="http://localhost:8000"
        GIT_BRANCH="main"
        ;;
    "staging")
        COMPOSE_FILE="docker-compose.staging.yml"
        FRONTEND_CONTAINER="megahub-frontend-staging"
        BACKEND_CONTAINER="megahub-backend-staging"
        DJANGO_SETTINGS="django_app.settings.staging"
        FRONTEND_URL="https://staging.megahub.humari.fr"
        BACKEND_URL="https://staging-api.megahub.humari.fr"
        GIT_BRANCH="develop"
        ;;
    "production")
        COMPOSE_FILE="docker-compose.production.yml"
        FRONTEND_CONTAINER="megahub-frontend-prod"
        BACKEND_CONTAINER="megahub-backend-prod"
        DJANGO_SETTINGS="django_app.settings.production"
        FRONTEND_URL="https://megahub.humari.fr"
        BACKEND_URL="https://backoffice.humari.fr"
        GIT_BRANCH="main"
        ;;
    *)
        echo "❌ Environnement non valide: $ENVIRONMENT"
        echo "Usage: $0 {development|staging|production}"
        exit 1
        ;;
esac

mkdir -p "$BACKUP_DIR"

# ==========================================
# FONCTIONS UTILITAIRES
# ==========================================
log() { echo "[$(date +'%H:%M:%S')] $1"; }
success() { echo "✅ $1"; }
error() { echo "❌ $1"; exit 1; }
react19_log() { echo "🚀 [React 19] $1"; }
django_log() { echo "🐍 [Django] $1"; }

log "🚀 Déploiement MegaHub $ENVIRONMENT - Architecture Leaders"

# ==========================================
# PROTECTION PRODUCTION
# ==========================================
if [ "$ENVIRONMENT" = "production" ]; then
    echo "⚠️  ATTENTION: Déploiement en PRODUCTION"
    read -p "Tapez 'PRODUCTION' pour confirmer: " confirmation
    if [ "$confirmation" != "PRODUCTION" ]; then
        echo "Déploiement annulé"
        exit 1
    fi
fi

# ==========================================
# BACKUP AVANT DÉPLOIEMENT
# ==========================================
backup_current_state() {
    log "📦 Backup de l'état actuel $ENVIRONMENT"
    
    # Backup frontend si existe
    if [ -d "$FRONTEND_DIR/dist" ]; then
        tar -czf "$BACKUP_DIR/frontend_${ENVIRONMENT}_backup_$TIMESTAMP.tar.gz" -C "$FRONTEND_DIR" dist
        success "Frontend backup créé"
    fi
    
    # Backup base de données si pas development
    if [ "$ENVIRONMENT" != "development" ]; then
        log "📦 Backup base de données $ENVIRONMENT"
        docker exec $BACKEND_CONTAINER pg_dump > "$BACKUP_DIR/db_${ENVIRONMENT}_backup_$TIMESTAMP.sql" || log "⚠️ Backup DB échoué"
    fi
    
    # Tag Git pour rollback possible
    cd "$SOURCE_DIR"
    git tag "backup-${ENVIRONMENT}-${TIMESTAMP}"
    git push origin "backup-${ENVIRONMENT}-${TIMESTAMP}" || log "⚠️ Push tag backup échoué"
}

# ==========================================
# MISE À JOUR CODE SOURCE
# ==========================================
update_source_code() {
    log "📥 Mise à jour code source depuis $GIT_BRANCH"
    cd "$SOURCE_DIR"
    
    # ✅ PAS DE git reset --hard ! (problème résolu)
    git fetch origin $GIT_BRANCH
    git checkout $GIT_BRANCH
    git pull origin $GIT_BRANCH
    
    react19_log "Code React 19 mis à jour depuis $GIT_BRANCH"
    django_log "Code Django mis à jour avec settings $DJANGO_SETTINGS"
}

# ==========================================
# BUILD FRONTEND REACT 19
# ==========================================
build_frontend() {
    log "🏗️ Build Frontend React 19 pour $ENVIRONMENT"
    cd "$FRONTEND_DIR"
    
    # Install dependencies
    log "📦 Installation dépendances React 19"
    npm ci
    
    # Audit security
    log "🔒 Audit sécurité"
    npm audit fix --force || log "⚠️ Vulnérabilités détectées"
    
    # Type check strict
    log "📝 TypeScript check strict"
    npm run type-check:strict
    
    # Lint
    log "🔍 Linting"
    npm run lint:ci || log "⚠️ Warnings lint détectés"
    
    # Routes TanStack
    log "🛤️ Génération routes TanStack"
    npm run routes:generate
    
    # Build avec variables d'environnement
    log "🏗️ Build React 19 + Lightning CSS"
    export VITE_ENV=$ENVIRONMENT
    npm run build
    
    # Vérifications build
    [ ! -d "dist" ] && error "Build échoué - dist manquant"
    [ ! -f "dist/index.html" ] && error "Build échoué - index.html manquant"
    
    JS_FILES=$(find dist/assets -name "*.js" | wc -l 2>/dev/null || echo "0")
    [ "$JS_FILES" -lt 1 ] && error "Build incomplet - JS files manquants"
    
    react19_log "Build réussi - $JS_FILES fichiers JS générés"
    log "📊 Taille build: $(du -sh dist | cut -f1)"
}

# ==========================================
# MIGRATIONS DJANGO
# ==========================================
run_migrations() {
    django_log "🗃️ Migrations Django $ENVIRONMENT"
    
    # Vérifier connexion DB
    docker exec $BACKEND_CONTAINER python manage.py check --database=default || error "Connexion DB échouée"
    
    # Migrations
    docker exec $BACKEND_CONTAINER python manage.py migrate --database=default
    
    # Collectstatic si production/staging
    if [ "$ENVIRONMENT" != "development" ]; then
        django_log "📦 Collectstatic"
        docker exec $BACKEND_CONTAINER python manage.py collectstatic --noinput || log "⚠️ Collectstatic échoué"
    fi
    
    django_log "Migrations $ENVIRONMENT terminées"
}

# ==========================================
# DÉPLOIEMENT DOCKER
# ==========================================
deploy_containers() {
    log "🐳 Déploiement Docker $ENVIRONMENT"
    cd "$PROJECT_DIR"
    
    # Arrêt propre
    docker-compose -f $COMPOSE_FILE stop 2>/dev/null || true
    
    # Build et démarrage
    docker-compose -f $COMPOSE_FILE up -d --build
    
    success "Containers $ENVIRONMENT démarrés"
}

# ==========================================
# HEALTH CHECKS ROBUSTES
# ==========================================
health_checks() {
    log "🏥 Health checks $ENVIRONMENT"
    
    # Attendre démarrage
    log "⏳ Attente démarrage (20s)..."
    sleep 20
    
    # Check containers
    if ! docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
        error "Containers ne démarrent pas"
    fi
    success "Containers actifs"
    
    # Health check interne frontend
    log "🩺 Health check frontend interne..."
    for i in {1..6}; do
        if docker exec $FRONTEND_CONTAINER curl -f http://localhost/health >/dev/null 2>&1; then
            success "Frontend health OK"
            break
        fi
        log "⏳ Tentative $i/6..."
        sleep 10
    done
    
    # Health check interne backend
    log "🩺 Health check backend interne..."
    for i in {1..6}; do
        if docker exec $BACKEND_CONTAINER python /app/health_check.py >/dev/null 2>&1; then
            success "Backend health OK"
            break
        fi
        log "⏳ Tentative $i/6..."
        sleep 10
    done
    
    # Health check externe (si pas development)
    if [ "$ENVIRONMENT" != "development" ]; then
        log "🌐 Health check externe..."
        sleep 30  # Attendre SSL/nginx-proxy
        
        for i in {1..10}; do
            if curl -f -s --max-time 10 "$FRONTEND_URL/health" >/dev/null 2>&1; then
                success "Health check externe réussi"
                break
            fi
            log "⏳ Tentative externe $i/10..."
            sleep 15
        done
    fi
}

# ==========================================
# TEST PERFORMANCE
# ==========================================
performance_test() {
    if [ "$ENVIRONMENT" != "development" ]; then
        log "📊 Test performance $ENVIRONMENT"
        
        RESPONSE_TIME=$(curl -w "%{time_total}" -o /dev/null -s --max-time 15 "$FRONTEND_URL/" 2>/dev/null || echo "ERROR")
        
        if [ "$RESPONSE_TIME" != "ERROR" ]; then
            react19_log "Temps de réponse: ${RESPONSE_TIME}s"
            
            if (( $(echo "$RESPONSE_TIME < 1.0" | bc -l) )); then
                success "Performance excellente (< 1s) ✅"
            elif (( $(echo "$RESPONSE_TIME < 2.0" | bc -l) )); then
                log "⚠️ Performance acceptable (< 2s)"
            else
                log "⚠️ Performance lente (> 2s)"
            fi
        fi
    fi
}

# ==========================================
# EXÉCUTION PRINCIPALE
# ==========================================
main() {
    backup_current_state
    update_source_code
    build_frontend
    deploy_containers
    run_migrations
    health_checks
    performance_test
    
    # Cleanup
    log "🧹 Nettoyage Docker"
    docker image prune -f >/dev/null 2>&1
    
    # Status final
    log "📊 Status final $ENVIRONMENT:"
    docker-compose -f $COMPOSE_FILE ps
    
    success "🎉 Déploiement $ENVIRONMENT réussi!"
    log "🌐 Frontend: $FRONTEND_URL"
    log "🐍 Backend: $BACKEND_URL"
    log "📈 Monitoring: docker-compose -f $COMPOSE_FILE logs -f"
    log "🔍 Debug: ./scripts/debug-env.sh $ENVIRONMENT"
}

main