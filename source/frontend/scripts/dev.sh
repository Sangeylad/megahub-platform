#!/bin/bash
# 🎯 Script développement MegaHub Frontend

set -e

echo "🚀 Démarrage MegaHub Frontend en mode développement"
echo "⚛️ React 19 + TanStack v5 + Lightning CSS"

# Vérifier Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2)
MIN_VERSION="20.12.0"

if ! printf '%s\n%s\n' "$MIN_VERSION" "$NODE_VERSION" | sort -V -C; then
    echo "❌ Node.js version $MIN_VERSION ou supérieure requise (actuelle: $NODE_VERSION)"
    exit 1
fi

# Installer dépendances si nécessaire
if [ ! -d "node_modules" ]; then
    echo "📦 Installation des dépendances..."
    npm install
fi

# Générer routes TanStack Router
echo "🛣️ Génération des routes TanStack Router..."
npm run routes:generate

# Vérification Biome
echo "🔍 Vérification code avec Biome..."
npm run lint

# Démarrer serveur développement
echo "🌐 Serveur disponible sur http://localhost:3000"
npm run dev
