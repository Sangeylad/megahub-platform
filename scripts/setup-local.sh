#!/bin/bash
# Script à exécuter sur ton poste local

PROJECT_NAME="megahub-frontend"
GITHUB_REPO="https://github.com/Sangeylad/megahub.git"

echo "🛠️ Setup développement local MegaHub"

# Créer dossier projets
mkdir -p ~/Projects
cd ~/Projects

# Clone repository
git clone $GITHUB_REPO
cd $PROJECT_NAME

# Install dependencies
npm install

# Setup environnement local
cp .env.local.example .env.local 2>/dev/null || echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local

# Premier démarrage
echo "✅ Setup terminé!"
echo "📝 Commandes disponibles:"
echo "  npm run dev     # Développement (port 3000)"
echo "  npm run build   # Build production"
echo "  npm run lint    # Linting"
echo "  npm run test    # Tests"
echo ""
echo "🚀 Démarrer: npm run dev"
