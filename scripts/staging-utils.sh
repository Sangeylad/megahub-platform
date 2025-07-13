#!/bin/bash
# MegaHub Staging Utilities

case "$1" in
  "deploy")
    echo "🚀 Déploiement staging..."
    ./scripts/deploy-staging.sh
    ;;
  "logs")
    echo "📋 Logs staging..."
    docker-compose -f docker-compose.staging.yml logs frontend --tail 50 -f
    ;;
  "status")
    echo "📊 Status staging..."
    docker-compose -f docker-compose.staging.yml ps frontend
    curl -I https://staging.megahub.humari.fr/health
    ;;
  "stop")
    echo "🛑 Arrêt staging..."
    docker-compose -f docker-compose.staging.yml stop frontend
    ;;
  "restart")
    echo "🔄 Redémarrage staging..."
    docker-compose -f docker-compose.staging.yml restart frontend
    ;;
  *)
    echo "Usage: $0 {deploy|logs|status|stop|restart}"
    exit 1
    ;;
esac
