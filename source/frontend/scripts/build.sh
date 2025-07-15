#!/bin/bash
# 🎯 Script build production MegaHub Frontend

set -e

echo "🏗️ Build MegaHub Frontend pour production"
echo "⚛️ React 19 + Lightning CSS + TanStack v5"

# Nettoyage
echo "🧹 Nettoyage des anciens builds..."
rm -rf dist

# Variables d'environnement production
export NODE_ENV=production
export VITE_ENABLE_REACT_COMPILER=true
export VITE_ENABLE_LIGHTNING_CSS=true
export GENERATE_SOURCEMAP=false

# Type checking strict
echo "📝 Vérification TypeScript 5.8.3..."
npm run type-check:strict

# Linting avec Biome
echo "🔍 Linting avec Biome..."
npm run lint:ci

# Tests (si activés)
if [ "$SKIP_TESTS" != "true" ]; then
    echo "🧪 Exécution des tests..."
    npm run test:ci
fi

# Génération routes
echo "🛣️ Génération routes TanStack Router..."
npm run routes:generate

# Build optimisé
echo "⚡ Build avec Vite 6 + Lightning CSS..."
npm run build

# Vérifications post-build
if [ ! -d "dist" ]; then
    echo "❌ Erreur: Répertoire dist non trouvé"
    exit 1
fi

if [ ! -f "dist/index.html" ]; then
    echo "❌ Erreur: index.html non trouvé"
    exit 1
fi

# Stats build
BUILD_SIZE=$(du -sh dist | cut -f1)
JS_FILES=$(find dist -name "*.js" | wc -l)
CSS_FILES=$(find dist -name "*.css" | wc -l)

echo "✅ Build réussi!"
echo "📊 Taille: $BUILD_SIZE"
echo "📊 Fichiers JS: $JS_FILES"
echo "📊 Fichiers CSS: $CSS_FILES"
