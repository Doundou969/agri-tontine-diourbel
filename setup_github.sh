#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
#  TONTINE+ — Script de mise en ligne sur GitHub
#  Usage : bash setup_github.sh
# ═══════════════════════════════════════════════════════════════════

set -e

REPO_URL="https://github.com/doundou969/agri-tontine-diourbel.git"
BRANCH="main"

echo ""
echo "🌾 TONTINE+ — Initialisation GitHub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Configuration Git identité
git config --global user.name  "doundou969"
git config --global user.email "doundou969@users.noreply.github.com"

# Init si pas encore un repo git
if [ ! -d ".git" ]; then
  git init
  echo "✅ Git initialisé"
fi

# Remote
if git remote get-url origin &>/dev/null; then
  git remote set-url origin "$REPO_URL"
  echo "✅ Remote mis à jour : $REPO_URL"
else
  git remote add origin "$REPO_URL"
  echo "✅ Remote ajouté : $REPO_URL"
fi

# Staging + commit initial
git add .
git commit -m "feat: MVP initial — modèles, routes Flask, scoring IA, CI GitHub Actions" || echo "ℹ️  Rien à committer (déjà à jour)"

# Push
echo ""
echo "📤 Push vers GitHub..."
git push -u origin "$BRANCH"

echo ""
echo "✅ Repo en ligne : https://github.com/doundou969/agri-tontine-diourbel"
echo "✅ Actions CI    : https://github.com/doundou969/agri-tontine-diourbel/actions"
echo "✅ Site Pages    : https://doundou969.github.io/agri-tontine-diourbel"
echo ""
echo "🚀 Prochaine étape : python run.py"
