#!/bin/bash
# /var/www/megahub/infrastructure/scripts/simple-fix-paths.sh
# Script ultra simple qui marche

BASE_DIR="/var/www/megahub/source"
COUNT=0

echo "🔄 Correction simple des paths dans $BASE_DIR"

# Fonction simple pour mettre à jour un fichier
fix_file() {
    local file="$1"
    local relative_path="${file#$BASE_DIR/}"
    local extension="${file##*.}"
    
    # Générer le bon commentaire
    local new_comment
    case "$extension" in
        "py")
            new_comment="# $relative_path"
            ;;
        "ts"|"tsx"|"js"|"jsx")
            new_comment="// $relative_path"
            ;;
        "css"|"scss")
            new_comment="/* $relative_path */"
            ;;
        "sh")
            new_comment="# $relative_path"
            ;;
        *)
            return  # Skip autres extensions
            ;;
    esac
    
    # Lire première ligne
    local first_line=$(head -n 1 "$file" 2>/dev/null)
    
    # Si déjà bon, skip
    if [[ "$first_line" == "$new_comment" ]]; then
        return
    fi
    
    # Si c'est un commentaire, remplacer
    if [[ "$first_line" =~ ^[[:space:]]*# ]] || \
       [[ "$first_line" =~ ^[[:space:]]*// ]] || \
       [[ "$first_line" =~ ^[[:space:]]*\/\* ]]; then
        sed -i "1s|.*|$new_comment|" "$file"
        echo "✅ $relative_path"
        ((COUNT++))
    else
        # Ajouter au début
        {
            echo "$new_comment"
            cat "$file"
        } > "$file.tmp" && mv "$file.tmp" "$file"
        echo "➕ $relative_path"
        ((COUNT++))
    fi
}

# Traiter les fichiers Python (exclure node_modules et OLD_BACKEND)
echo "🐍 Fichiers Python..."
find "$BASE_DIR" -name "*.py" -type f \
    -not -path "*/node_modules/*" \
    -not -path "*/OLD_BACKEND/*" \
    -not -path "*/dist/*" \
    -not -path "*/__pycache__/*" | while read -r file; do
    fix_file "$file"
done

# Traiter les fichiers TypeScript/JavaScript (exclure JSON et autres)
echo "📱 Fichiers TypeScript/JavaScript..."
find "$BASE_DIR" -type f \
    \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) \
    -not -name "*.json" \
    -not -name "*.d.ts" \
    -not -name "*.min.js" \
    -not -name "routeTree.gen.ts" \
    -not -path "*/node_modules/*" \
    -not -path "*/OLD_BACKEND/*" \
    -not -path "*/dist/*" \
    -not -path "*/build/*" | while read -r file; do
    fix_file "$file"
done

# Traiter les fichiers CSS
echo "🎨 Fichiers CSS..."
find "$BASE_DIR" -type f \
    \( -name "*.css" -o -name "*.scss" -o -name "*.sass" \) \
    -not -name "*.min.css" \
    -not -path "*/node_modules/*" \
    -not -path "*/OLD_BACKEND/*" \
    -not -path "*/dist/*" | while read -r file; do
    fix_file "$file"
done

echo ""
echo "🎉 Terminé ! $COUNT fichiers traités"