# dev-setup/aliases.sh
#!/bin/bash

# ================================
# HUMARI DEV ALIASES
# ================================
# Usage: source dev-setup/aliases.sh

echo "🚀 Loading Humari dev aliases..."

# Project paths
export HUMARI_ROOT="/var/www/megahub/websites"
export HUMARI_SRC="/var/www/megahub/websites/humari-site/src"

# 🚀 Build & deploy ultra-rapide
alias hbuild="echo '🚀 Building Humari...' && docker exec -it humari-nextjs-prod npm run build && echo '🔄 Restarting container...' && docker restart humari-nextjs-prod && echo '✅ Humari deployed at https://humari.fr!' && hlogs"

# 📋 Logs en temps réel
alias hlogs="docker logs -f --tail=50 humari-nextjs-prod"

# 🔧 Shell dans le container
alias hshell="docker exec -it humari-nextjs-prod sh"

# 🔍 Status & debug
alias hstatus="docker ps --filter name=humari-nextjs-prod --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
alias hrestart="docker restart humari-nextjs-prod && hlogs"
alias hstop="docker stop humari-nextjs-prod"
alias hstart="docker start humari-nextjs-prod && hlogs"

# 🧹 Nettoyage
alias hclean="docker exec -it humari-nextjs-prod rm -rf /app/.next && hrestart"

# 📊 Resource usage
alias hstats="docker stats humari-nextjs-prod --no-stream"

# 🌐 Ouvrir le site
# alias hopen="open https://humari.fr"  # macOS
alias hopen="curl -I https://humari.fr"  # Linux

# 🔄 Full redeploy
alias hredeploy="cd $HUMARI_ROOT && docker-compose down && docker-compose up -d --build humari-nextjs && hlogs"

# 📝 Navigation rapide
alias hedit="cd $HUMARI_SRC && pwd"
alias hroot="cd $HUMARI_ROOT && pwd"
alias hproject="cd /var/www/megahub/websites/humari-site && pwd"

# 📋 Help
alias hhelp="cat $HUMARI_ROOT/humari-site/dev-setup/README.md"

echo "✅ Aliases loaded! Type 'hhelp' for documentation"