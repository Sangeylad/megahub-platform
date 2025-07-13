#!/bin/bash

#########################################
# Script de déploiement Humari Tools Plugin
#
# COMMANDES POUR EXECUTER :
# cd /var/www/megahub/humari_tools_wp/
# chmod +x deploy.sh
# ./deploy.sh
#
# OU en une ligne depuis n'importe où :
# /var/www/megahub/humari_tools_wp/deploy.sh
#
# PRÉREQUIS :
# - Avoir les droits d'écriture sur le dossier WordPress
# - Plugin peut rester activé (drag & drop logic)
#########################################

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Chemins
SOURCE_DIR="/var/www/megahub/humari_tools_wp"
DEST_DIR="/var/www/frenchease/sites/prod/Humari/wp-content/plugins/humari-tools"

echo -e "${BLUE}🚀 Déploiement du plugin Humari Tools${NC}"
echo "=================================="

# Vérification du dossier source
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}❌ Erreur: Dossier source introuvable: $SOURCE_DIR${NC}"
    exit 1
fi

# Vérification du dossier WordPress de destination
WORDPRESS_PLUGINS_DIR="/var/www/frenchease/sites/prod/Humari/wp-content/plugins"
if [ ! -d "$WORDPRESS_PLUGINS_DIR" ]; then
    echo -e "${RED}❌ Erreur: Dossier WordPress plugins introuvable: $WORDPRESS_PLUGINS_DIR${NC}"
    exit 1
fi

# Affichage des chemins
echo -e "${YELLOW}📂 Source:${NC} $SOURCE_DIR"
echo -e "${YELLOW}📂 Destination:${NC} $DEST_DIR"
echo ""

# Demander confirmation
read -p "Continuer le déploiement ? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⏹️  Déploiement annulé${NC}"
    exit 0
fi

# Backup du plugin existant (si il existe)
if [ -d "$DEST_DIR" ]; then
    BACKUP_DIR="${DEST_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}📦 Backup du plugin existant vers: $BACKUP_DIR${NC}"
    cp -r "$DEST_DIR" "$BACKUP_DIR"
    
    # Suppression complète de l'ancien (logique drag & drop)
    echo -e "${YELLOW}🗑️  Suppression de l'ancien plugin...${NC}"
    rm -rf "$DEST_DIR"
fi

# Création du nouveau dossier
echo -e "${BLUE}📁 Création du nouveau dossier plugin...${NC}"
mkdir -p "$DEST_DIR"

# Copie sélective des fichiers (EXCLUSION du deploy.sh)
echo -e "${BLUE}📋 Copie des fichiers...${NC}"

# Liste des fichiers/dossiers à exclure
EXCLUDE_FILES=("deploy.sh" ".git" ".gitignore" "node_modules")

# Function pour vérifier si un fichier doit être exclu
should_exclude() {
    local file="$1"
    for exclude in "${EXCLUDE_FILES[@]}"; do
        if [[ "$file" == "$exclude" ]]; then
            return 0  # True - à exclure
        fi
    done
    return 1  # False - à inclure
}

# Parcourir et copier tous les fichiers/dossiers sauf ceux exclus
for item in "$SOURCE_DIR"/*; do
    if [ -e "$item" ]; then
        basename_item=$(basename "$item")
        
        if should_exclude "$basename_item"; then
            echo -e "${YELLOW}⏭️  Exclusion: $basename_item${NC}"
            continue
        fi
        
        if [ -d "$item" ]; then
            cp -r "$item" "$DEST_DIR/" && echo -e "${GREEN}✅ Dossier $basename_item copié${NC}"
        else
            cp "$item" "$DEST_DIR/" && echo -e "${GREEN}✅ Fichier $basename_item copié${NC}"
        fi
    fi
done

# Ajustement des permissions (comme WordPress)
echo -e "${BLUE}🔐 Ajustement des permissions...${NC}"
chown -R www-data:www-data "$DEST_DIR"
chmod -R 755 "$DEST_DIR"
find "$DEST_DIR" -type f -exec chmod 644 {} \;

# Vérification finale
echo ""
echo -e "${BLUE}🔍 Vérification du déploiement:${NC}"

# Vérification des fichiers essentiels
if [ -f "$DEST_DIR/humari-tools.php" ]; then
    echo -e "${GREEN}✅ Plugin principal trouvé${NC}"
else
    echo -e "${RED}❌ Plugin principal manquant${NC}"
    exit 1
fi

if [ -d "$DEST_DIR/includes" ]; then
    echo -e "${GREEN}✅ Dossier includes/ trouvé${NC}"
    echo "   $(ls -1 "$DEST_DIR/includes" | wc -l) fichier(s) dans includes/"
else
    echo -e "${RED}❌ Dossier includes/ manquant${NC}"
fi

if [ -d "$DEST_DIR/assets" ]; then
    echo -e "${GREEN}✅ Dossier assets/ trouvé${NC}"
else
    echo -e "${YELLOW}⚠️  Dossier assets/ manquant (optionnel)${NC}"
fi

# Vérification que deploy.sh n'a PAS été copié
if [ -f "$DEST_DIR/deploy.sh" ]; then
    echo -e "${RED}❌ ERREUR: deploy.sh a été copié par erreur${NC}"
    rm -f "$DEST_DIR/deploy.sh"
    echo -e "${GREEN}✅ deploy.sh supprimé${NC}"
else
    echo -e "${GREEN}✅ deploy.sh correctement exclu${NC}"
fi

# Affichage de la taille et du contenu
PLUGIN_SIZE=$(du -sh "$DEST_DIR" | cut -f1)
FILE_COUNT=$(find "$DEST_DIR" -type f | wc -l)
echo -e "${BLUE}📊 Taille du plugin:${NC} $PLUGIN_SIZE ($FILE_COUNT fichiers)"

# Liste des fichiers copiés
echo -e "${BLUE}📄 Contenu final:${NC}"
ls -la "$DEST_DIR"

echo ""
echo -e "${GREEN}🎉 Déploiement terminé avec succès !${NC}"
echo -e "${GREEN}🔄 Logique drag & drop appliquée (suppression/recréation)${NC}"
echo ""
echo -e "${YELLOW}📝 Prochaines étapes:${NC}"
echo "1. Le plugin reste activé s'il l'était"
echo "2. Tester avec un shortcode: [humari_tool tool=\"converter\" category=\"document\"]"
echo "3. Vérifier dans l'admin WordPress si besoin"
echo ""
echo -e "${BLUE}🔗 Chemin du plugin:${NC} $DEST_DIR"