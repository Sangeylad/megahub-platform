#!/bin/bash
# /var/www/megahub/scripts/utils-env.sh
# Utilitaires MegaHub par environnement

ENVIRONMENT=${1:-development}
ACTION=${2:-status}

case $ENVIRONMENT in
    "development") COMPOSE_FILE="docker-compose.yml" ;;
    "staging") COMPOSE_FILE="docker-compose.staging.yml" ;;
    "production") COMPOSE_FILE="docker-compose.production.yml" ;;
    *) echo "Usage: $0 {development|staging|production} {deploy|logs|status|stop|restart|shell}"; exit 1 ;;
esac

case "$ACTION" in
    "deploy")
        echo "🚀 Déploiement $ENVIRONMENT..."
        ./scripts/deploy-env.sh $ENVIRONMENT
        ;;
    "logs")
        echo "📋 Logs $ENVIRONMENT..."
        docker-compose -f $COMPOSE_FILE logs --tail 50 -f
        ;;
    "status")
        echo "📊 Status $ENVIRONMENT..."
        docker-compose -f $COMPOSE_FILE ps
        if [ "$ENVIRONMENT" != "development" ]; then
            case $ENVIRONMENT in
                "staging") curl -I https://staging.megahub.humari.fr/health ;;
                "production") curl -I https://megahub.humari.fr/health ;;
            esac
        fi
        ;;
    "stop")
        echo "🛑 Arrêt $ENVIRONMENT..."
        docker-compose -f $COMPOSE_FILE stop
        ;;
    "restart")
        echo "🔄 Redémarrage $ENVIRONMENT..."
        docker-compose -f $COMPOSE_FILE restart
        ;;
    "shell")
        echo "🐚 Shell backend $ENVIRONMENT..."
        docker-compose -f $COMPOSE_FILE exec backend bash
        ;;
    *)
        echo "Usage: $0 $ENVIRONMENT {deploy|logs|status|stop|restart|shell}"
        exit 1
        ;;
esac