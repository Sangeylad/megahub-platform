#!/bin/bash
# /var/www/megahub/scripts/utils-multi-env.sh
# Utilitaires pour gérer staging ET production simultanément

PROJECT_DIR="/var/www/megahub"

# ==========================================
# FONCTIONS MULTI-ENVIRONNEMENTS
# ==========================================

status_all() {
    echo "📊 Status TOUS les environnements:"
    echo ""
    echo "🧪 STAGING:"
    docker-compose -p megahub-staging -f docker-compose.staging.yml ps
    echo ""
    echo "🚀 PRODUCTION:"
    docker-compose -p megahub-production -f docker-compose.production.yml ps
}

logs_env() {
    ENV=${1:-staging}
    case $ENV in
        "staging")
            echo "📋 Logs STAGING..."
            docker-compose -p megahub-staging -f docker-compose.staging.yml logs --tail 50 -f
            ;;
        "production"|"prod")
            echo "📋 Logs PRODUCTION..."
            docker-compose -p megahub-production -f docker-compose.production.yml logs --tail 50 -f
            ;;
        *)
            echo "Usage: logs {staging|production}"
            ;;
    esac
}

stop_env() {
    ENV=${1:-staging}
    case $ENV in
        "staging")
            echo "🛑 Arrêt STAGING..."
            docker-compose -p megahub-staging -f docker-compose.staging.yml stop
            ;;
        "production"|"prod")
            echo "🛑 Arrêt PRODUCTION..."
            docker-compose -p megahub-production -f docker-compose.production.yml stop
            ;;
        "all")
            echo "🛑 Arrêt TOUS les environnements..."
            docker-compose -p megahub-staging -f docker-compose.staging.yml stop
            docker-compose -p megahub-production -f docker-compose.production.yml stop
            ;;
        *)
            echo "Usage: stop {staging|production|all}"
            ;;
    esac
}

start_env() {
    ENV=${1:-staging}
    case $ENV in
        "staging")
            echo "🚀 Démarrage STAGING..."
            docker-compose -p megahub-staging -f docker-compose.staging.yml up -d
            ;;
        "production"|"prod")
            echo "🚀 Démarrage PRODUCTION..."
            docker-compose -p megahub-production -f docker-compose.production.yml up -d
            ;;
        "all")
            echo "🚀 Démarrage TOUS les environnements..."
            docker-compose -p megahub-staging -f docker-compose.staging.yml up -d
            docker-compose -p megahub-production -f docker-compose.production.yml up -d
            ;;
        *)
            echo "Usage: start {staging|production|all}"
            ;;
    esac
}

restart_env() {
    ENV=${1:-staging}
    case $ENV in
        "staging")
            echo "🔄 Redémarrage STAGING..."
            docker-compose -p megahub-staging -f docker-compose.staging.yml restart
            ;;
        "production"|"prod")
            echo "🔄 Redémarrage PRODUCTION..."
            docker-compose -p megahub-production -f docker-compose.production.yml restart
            ;;
        "all")
            echo "🔄 Redémarrage TOUS les environnements..."
            docker-compose -p megahub-staging -f docker-compose.staging.yml restart
            docker-compose -p megahub-production -f docker-compose.production.yml restart
            ;;
        *)
            echo "Usage: restart {staging|production|all}"
            ;;
    esac
}

shell_env() {
    ENV=${1:-staging}
    SERVICE=${2:-backend}
    case $ENV in
        "staging")
            echo "🐚 Shell STAGING $SERVICE..."
            docker exec -it megahub-${SERVICE}-staging bash
            ;;
        "production"|"prod")
            echo "🐚 Shell PRODUCTION $SERVICE..."
            docker exec -it megahub-${SERVICE}-prod bash
            ;;
        *)
            echo "Usage: shell {staging|production} [backend|frontend]"
            ;;
    esac
}

health_check_all() {
    echo "🏥 Health check TOUS les environnements:"
    echo ""
    echo "🧪 STAGING Backend:"
    docker exec megahub-backend-staging python /app/health_check.py 2>/dev/null && echo "✅ OK" || echo "❌ KO"
    echo "🧪 STAGING Frontend:"
    docker exec megahub-frontend-staging curl -f http://localhost/health >/dev/null 2>&1 && echo "✅ OK" || echo "❌ KO"
    echo ""
    echo "🚀 PRODUCTION Backend:"
    docker exec megahub-backend-prod python /app/health_check.py 2>/dev/null && echo "✅ OK" || echo "❌ KO"
    echo "🚀 PRODUCTION Frontend:"
    docker exec megahub-frontend-prod curl -f http://localhost/health >/dev/null 2>&1 && echo "✅ OK" || echo "❌ KO"
}

# ==========================================
# RACCOURCIS PRATIQUES
# ==========================================
alias mh-status='status_all'
alias mh-health='health_check_all'
alias mh-staging='start_env staging'
alias mh-prod='start_env production'
alias mh-stop-all='stop_env all'
alias mh-restart-all='restart_env all'

# ==========================================
# GESTION ARGUMENTS
# ==========================================
case "${1:-help}" in
    "status")
        status_all
        ;;
    "logs")
        logs_env $2
        ;;
    "stop")
        stop_env $2
        ;;
    "start")
        start_env $2
        ;;
    "restart")
        restart_env $2
        ;;
    "shell")
        shell_env $2 $3
        ;;
    "health")
        health_check_all
        ;;
    "help"|*)
        echo "🎯 MegaHub Multi-Environnements"
        echo "Usage: $0 {status|logs|stop|start|restart|shell|health}"
        echo ""
        echo "Commandes:"
        echo "  status                    - Status tous environnements"
        echo "  logs {staging|production} - Logs environnement"
        echo "  stop {staging|production|all} - Arrêt environnement"
        echo "  start {staging|production|all} - Démarrage environnement"
        echo "  restart {staging|production|all} - Redémarrage environnement"
        echo "  shell {staging|production} [service] - Shell dans container"
        echo "  health                    - Health check tous environnements"
        echo ""
        echo "Raccourcis disponibles:"
        echo "  mh-status, mh-health, mh-staging, mh-prod, mh-stop-all, mh-restart-all"
        ;;
esac