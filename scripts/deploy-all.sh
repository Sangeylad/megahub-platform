#!/bin/bash
# /var/www/megahub/scripts/deploy-all.sh
# Déploiement simultané des 3 environnements MegaHub

set -euo pipefail

PROJECT_DIR="/var/www/megahub"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# ==========================================
# CONFIGURATION
# ==========================================
DEPLOY_MODE=${1:-sequential}  # sequential | parallel | staging-prod

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log() { echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }

# ==========================================
# FONCTIONS UTILITAIRES
# ==========================================
deploy_single_env() {
    local env=$1
    local log_file="/tmp/deploy_${env}_$TIMESTAMP.log"
    
    log "🚀 Déploiement $env démarré..."
    
    if ./scripts/deploy-env.sh $env > "$log_file" 2>&1; then
        success "Déploiement $env réussi"
        return 0
    else
        error "Déploiement $env échoué - Voir $log_file"
        return 1
    fi
}

show_final_status() {
    log "📊 Status final multi-environnements:"
    echo ""
    
    echo -e "${CYAN}🔧 DEVELOPMENT:${NC}"
    docker-compose -p megahub-dev -f docker-compose.yml ps 2>/dev/null || echo "  Non démarré"
    
    echo -e "${YELLOW}🧪 STAGING:${NC}"
    docker-compose -p megahub-staging -f docker-compose.staging.yml ps 2>/dev/null || echo "  Non démarré"
    
    echo -e "${GREEN}🚀 PRODUCTION:${NC}"
    docker-compose -p megahub-production -f docker-compose.production.yml ps 2>/dev/null || echo "  Non démarré"
    
    echo ""
    log "🌐 URLs accessibles:"
    echo "  Development:  http://localhost:3000"
    echo "  Staging:      https://staging.megahub.humari.fr"
    echo "  Production:   https://megahub.humari.fr"
}

health_check_all_envs() {
    log "🏥 Health check complet multi-environnements..."
    
    echo -e "${CYAN}🔧 Development:${NC}"
    if docker exec megahub-backend-dev python /app/health_check.py >/dev/null 2>&1; then
        success "Backend Dev OK"
    else
        warning "Backend Dev KO ou non démarré"
    fi
    
    echo -e "${YELLOW}🧪 Staging:${NC}"
    if docker exec megahub-backend-staging python /app/health_check.py >/dev/null 2>&1; then
        success "Backend Staging OK"
    else
        warning "Backend Staging KO"
    fi
    
    echo -e "${GREEN}🚀 Production:${NC}"
    if docker exec megahub-backend-prod python /app/health_check.py >/dev/null 2>&1; then
        success "Backend Production OK"
    else
        warning "Backend Production KO"
    fi
}

# ==========================================
# MODES DE DÉPLOIEMENT
# ==========================================
deploy_sequential() {
    log "🔄 Déploiement séquentiel - Development → Staging → Production"
    
    local success_count=0
    local total_count=3
    
    # Development
    if deploy_single_env "development"; then
        ((success_count++))
    fi
    
    # Staging  
    if deploy_single_env "staging"; then
        ((success_count++))
    fi
    
    # Production (avec confirmation)
    echo ""
    warning "⚠️ ATTENTION: Déploiement PRODUCTION"
    read -p "Continuer avec production ? (y/N): " confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
        if deploy_single_env "production"; then
            ((success_count++))
        fi
    else
        warning "Production ignorée"
        ((total_count--))
    fi
    
    echo ""
    success "$success_count/$total_count environnements déployés avec succès"
}

deploy_parallel() {
    log "⚡ Déploiement parallèle - Tous environnements simultanément"
    
    # Démarrer les 3 en parallèle (background)
    deploy_single_env "development" &
    local dev_pid=$!
    
    deploy_single_env "staging" &
    local staging_pid=$!
    
    # Production avec confirmation
    echo ""
    warning "⚠️ Déploiement PRODUCTION en parallèle"
    read -p "Confirmer production ? (y/N): " confirm
    local prod_pid=""
    if [[ $confirm =~ ^[Yy]$ ]]; then
        deploy_single_env "production" &
        prod_pid=$!
    fi
    
    # Attendre completion
    log "⏳ Attente completion déploiements parallèles..."
    
    local success_count=0
    
    if wait $dev_pid; then
        success "Development terminé"
        ((success_count++))
    else
        error "Development échoué"
    fi
    
    if wait $staging_pid; then
        success "Staging terminé"
        ((success_count++))
    else
        error "Staging échoué"
    fi
    
    if [[ -n "$prod_pid" ]]; then
        if wait $prod_pid; then
            success "Production terminé"
            ((success_count++))
        else
            error "Production échoué"
        fi
    fi
    
    echo ""
    success "$success_count environnements déployés en parallèle"
}

deploy_staging_prod() {
    log "🎯 Déploiement Staging + Production uniquement"
    
    local success_count=0
    
    # Staging
    if deploy_single_env "staging"; then
        ((success_count++))
    fi
    
    # Production avec confirmation
    echo ""
    warning "⚠️ ATTENTION: Déploiement PRODUCTION"
    read -p "Continuer avec production ? (y/N): " confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
        if deploy_single_env "production"; then
            ((success_count++))
        fi
    else
        warning "Production ignorée"
    fi
    
    echo ""
    success "$success_count/2 environnements déployés"
}

# ==========================================
# MENU INTERACTIF
# ==========================================
interactive_menu() {
    echo -e "${CYAN}"
    echo "🎯 MegaHub - Déploiement Multi-Environnements"
    echo "============================================="
    echo -e "${NC}"
    echo "1) 🔄 Séquentiel (Dev → Staging → Prod)"
    echo "2) ⚡ Parallèle (Tous simultanément)"  
    echo "3) 🎯 Staging + Production uniquement"
    echo "4) 📊 Status actuel"
    echo "5) 🏥 Health check complet"
    echo "6) 🛑 Sortir"
    echo ""
    read -p "Choix (1-6): " choice
    
    case $choice in
        1) deploy_sequential ;;
        2) deploy_parallel ;;
        3) deploy_staging_prod ;;
        4) show_final_status ;;
        5) health_check_all_envs ;;
        6) exit 0 ;;
        *) error "Choix invalide" && interactive_menu ;;
    esac
}

# ==========================================
# EXÉCUTION PRINCIPALE
# ==========================================
main() {
    cd "$PROJECT_DIR"
    
    log "🚀 MegaHub Multi-Deploy - Mode: $DEPLOY_MODE"
    
    case $DEPLOY_MODE in
        "sequential"|"seq")
            deploy_sequential
            ;;
        "parallel"|"para")
            deploy_parallel
            ;;
        "staging-prod"|"sp")
            deploy_staging_prod
            ;;
        "interactive"|"menu"|"i")
            interactive_menu
            ;;
        "help"|"--help"|"-h")
            echo "Usage: $0 [MODE]"
            echo ""
            echo "Modes disponibles:"
            echo "  sequential     - Déploiement séquentiel (défaut)"
            echo "  parallel       - Déploiement parallèle"
            echo "  staging-prod   - Staging + Production uniquement"
            echo "  interactive    - Menu interactif"
            echo ""
            echo "Exemples:"
            echo "  $0                    # Séquentiel"
            echo "  $0 parallel           # Parallèle"
            echo "  $0 staging-prod       # Staging + Prod"
            echo "  $0 interactive        # Menu"
            exit 0
            ;;
        *)
            error "Mode '$DEPLOY_MODE' inconnu"
            echo "Usage: $0 {sequential|parallel|staging-prod|interactive|help}"
            exit 1
            ;;
    esac
    
    # Status final
    echo ""
    show_final_status
    health_check_all_envs
    
    success "🎉 Déploiement multi-environnements terminé!"
}

main