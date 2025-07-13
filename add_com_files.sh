#!/bin/bash

# Script pour ajouter les chemins de fichiers - VERSION CORRIGÉE
set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Script d'ajout des chemins de fichiers (VERSION SÉCURISÉE)${NC}"

# Variables CORRIGÉES pour Docker
CONTAINER_NAME="megahub-backend"
BACKEND_DIR="/app"  # Chemin DANS le container
FRONTEND_DIR="/var/www/megahub/frontend/react-app"  # Chemin hôte
BACKUP_DIR="/tmp/megahub_backup_$(date +%Y%m%d_%H%M%S)"

# 1. BACKUP sur l'hôte
echo -e "${YELLOW}📦 Création du backup...${NC}"
mkdir -p "$BACKUP_DIR"

# Backup backend depuis le container
docker exec "$CONTAINER_NAME" tar czf /tmp/backend_backup.tar.gz -C /app .
docker cp "${CONTAINER_NAME}:/tmp/backend_backup.tar.gz" "${BACKUP_DIR}/"

# Backup frontend (si accessible depuis l'hôte)
if [[ -d "$FRONTEND_DIR" ]]; then
    tar czf "${BACKUP_DIR}/frontend_backup.tar.gz" -C "$FRONTEND_DIR" .
    echo -e "${GREEN}✅ Backup frontend créé${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend non trouvé sur l'hôte, backup ignoré${NC}"
fi

echo -e "${GREEN}✅ Backup créé dans: $BACKUP_DIR${NC}"

# Fonction pour les commentaires
get_comment_style() {
    local file="$1"
    local ext="${file##*.}"
    
    case "$ext" in
        py)              echo "# " ;;
        js|jsx|ts|tsx)   echo "// " ;;
        css|scss|sass)   echo "/* " ;;
        html|htm)        echo "<!-- " ;;
        md)              echo "<!-- " ;;
        json|yaml|yml)   echo "" ;;  # Pas de commentaires
        *)               echo "# " ;;
    esac
}

get_comment_end() {
    local file="$1"
    local ext="${file##*.}"
    
    case "$ext" in
        css|scss|sass) echo " */" ;;
        html|htm)      echo " -->" ;;
        md)            echo " -->" ;;
        *)             echo "" ;;
    esac
}

# Fonction pour traiter les fichiers BACKEND (dans container)
process_backend_files() {
    echo -e "${BLUE}📁 Traitement Backend (dans container)...${NC}"
    
    # Script à exécuter DANS le container
    local script='
#!/bin/bash
set -e

# Fonction helper dans le container
add_path_comment() {
    local file="$1"
    local relative_path="${file#/app/}"
    
    # Vérifier si déjà traité
    if head -n 1 "$file" 2>/dev/null | grep -q "$relative_path"; then
        echo "Déjà traité: $relative_path"
        return 0
    fi
    
    # Déterminer le type de commentaire
    local ext="${file##*.}"
    local comment_start=""
    local comment_end=""
    
    case "$ext" in
        py)              comment_start="# " ;;
        js|jsx|ts|tsx)   comment_start="// " ;;
        css|scss|sass)   comment_start="/* "; comment_end=" */" ;;
        html|htm)        comment_start="<!-- "; comment_end=" -->" ;;
        md)              comment_start="<!-- "; comment_end=" -->" ;;
        json|yaml|yml)   return 0 ;;  # Ignore
        *)               comment_start="# " ;;
    esac
    
    if [[ -z "$comment_start" ]]; then
        return 0
    fi
    
    # Créer temp file DANS le container
    local temp_file="/tmp/temp_$(basename "$file")"
    echo "${comment_start}${relative_path}${comment_end}" > "$temp_file"
    cat "$file" >> "$temp_file"
    
    # Remplacer
    mv "$temp_file" "$file"
    echo "✅ Traité: $relative_path"
}

# Traiter tous les fichiers Python
find /app -name "*.py" -type f | while read -r file; do
    if [[ "$file" != *"__pycache__"* ]] && [[ "$file" != *"/migrations/"* ]]; then
        add_path_comment "$file"
    fi
done

echo "Backend terminé!"
'

    # Exécuter le script dans le container
    echo "$script" | docker exec -i "$CONTAINER_NAME" bash
}

# Fonction pour traiter les fichiers FRONTEND (sur hôte)
process_frontend_files() {
    if [[ ! -d "$FRONTEND_DIR" ]]; then
        echo -e "${YELLOW}⚠️  Frontend non accessible, ignoré${NC}"
        return 0
    fi
    
    echo -e "${BLUE}📁 Traitement Frontend (sur hôte)...${NC}"
    
    # Extensions frontend
    local extensions=("js" "jsx" "ts" "tsx" "css" "scss" "sass")
    
    for ext in "${extensions[@]}"; do
        find "$FRONTEND_DIR" -name "*.$ext" -type f | while read -r file; do
            # Ignorer node_modules, build, etc.
            if [[ "$file" == *"node_modules"* ]] || [[ "$file" == *"build"* ]] || [[ "$file" == *".next"* ]]; then
                continue
            fi
            
            local relative_path="${file#$FRONTEND_DIR/}"
            
            # Vérifier si déjà traité
            if head -n 1 "$file" 2>/dev/null | grep -q "$relative_path"; then
                echo -e "${YELLOW}⏭️  Déjà traité: $relative_path${NC}"
                continue
            fi
            
            # Déterminer le commentaire
            local comment_start=""
            local comment_end=""
            
            case "$ext" in
                js|jsx|ts|tsx)   comment_start="// " ;;
                css|scss|sass)   comment_start="/* "; comment_end=" */" ;;
            esac
            
            # Créer temp file sur l'hôte
            local temp_file=$(mktemp)
            echo "${comment_start}${relative_path}${comment_end}" > "$temp_file"
            cat "$file" >> "$temp_file"
            
            # Remplacer
            mv "$temp_file" "$file"
            echo -e "${GREEN}✅ Traité: $relative_path${NC}"
        done
    done
}

# Fonction de restauration en cas d'erreur
restore_backup() {
    echo -e "${RED}🚨 Erreur détectée, restauration du backup...${NC}"
    
    # Restaurer backend
    if [[ -f "${BACKUP_DIR}/backend_backup.tar.gz" ]]; then
        docker exec "$CONTAINER_NAME" rm -rf /app/*
        docker cp "${BACKUP_DIR}/backend_backup.tar.gz" "${CONTAINER_NAME}:/tmp/"
        docker exec "$CONTAINER_NAME" tar xzf /tmp/backend_backup.tar.gz -C /app
        echo -e "${GREEN}✅ Backend restauré${NC}"
    fi
    
    # Restaurer frontend
    if [[ -f "${BACKUP_DIR}/frontend_backup.tar.gz" ]] && [[ -d "$FRONTEND_DIR" ]]; then
        rm -rf "${FRONTEND_DIR:?}"/*
        tar xzf "${BACKUP_DIR}/frontend_backup.tar.gz" -C "$FRONTEND_DIR"
        echo -e "${GREEN}✅ Frontend restauré${NC}"
    fi
}

# Trap pour restaurer en cas d'erreur
trap restore_backup ERR

# Fonction principale
main() {
    echo -e "${BLUE}🎯 Début du traitement sécurisé...${NC}"
    
    # Vérifier que le container existe
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        echo -e "${RED}❌ Container $CONTAINER_NAME non trouvé${NC}"
        exit 1
    fi
    
    # Traiter backend
    process_backend_files
    
    # Traiter frontend
    process_frontend_files
    
    echo -e "\n${GREEN}🎉 Traitement terminé avec succès !${NC}"
    echo -e "${BLUE}📦 Backup disponible dans: $BACKUP_DIR${NC}"
}

# Demander confirmation
echo -e "${YELLOW}⚠️  Ce script va modifier tous les fichiers Python/JS/CSS${NC}"
echo -e "${YELLOW}📦 Backup automatique + restauration en cas d'erreur${NC}"
echo -e "${BLUE}Continuer ? (y/N)${NC}"
read -r response
if [[ "$response" != "y" && "$response" != "Y" ]]; then
    echo -e "${RED}❌ Annulé${NC}"
    exit 0
fi

# Lancer
main