#!/bin/bash
# Helper script to push snippet-manager to GitHub

set -e

REPO_NAME="snippet-manager"

echo "🚀 Snippet Manager - GitHub Push Helper"
echo "========================================"
echo ""

# Check if git is configured
if [ -z "$(git config user.name)" ] || [ -z "$(git config user.email)" ]; then
    echo "⚠️  Git not configured. Let's set it up:"
    read -p "Your name: " GIT_NAME
    read -p "Your email: " GIT_EMAIL
    git config user.name "$GIT_NAME"
    git config user.email "$GIT_EMAIL"
    echo "✅ Git configured!"
    echo ""
fi

# Check for GitHub CLI
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI found!"
    
    # Check if logged in
    if ! gh auth status &> /dev/null; then
        echo "🔐 Please login to GitHub:"
        gh auth login
    fi
    
    echo ""
    read -p "Make repo public? [Y/n]: " PUBLIC
    PUBLIC_FLAG="--public"
    if [[ $PUBLIC =~ ^[Nn]$ ]]; then
        PUBLIC_FLAG="--private"
    fi
    
    echo ""
    echo "📤 Creating GitHub repo and pushing..."
    gh repo create "$REPO_NAME" $PUBLIC_FLAG --source=. --push
    
    echo ""
    echo "✅ SUCCESS! Repository created at:"
    gh repo view "$REPO_NAME" --json url -q .url
    
else
    echo "ℹ️  GitHub CLI not found. Using HTTPS method..."
    echo ""
    read -p "Your GitHub username: " GH_USER
    
    # Add remote
    git remote add origin "https://github.com/$GH_USER/$REPO_NAME.git" 2>/dev/null || \
        git remote set-url origin "https://github.com/$GH_USER/$REPO_NAME.git"
    
    git branch -M main
    
    echo ""
    echo "📤 Pushing to GitHub..."
    echo "💡 When prompted for password, use a Personal Access Token"
    echo "   Create one at: https://github.com/settings/tokens"
    echo ""
    
    git push -u origin main
    
    echo ""
    echo "✅ SUCCESS! Repository pushed!"
    echo "🌐 Visit: https://github.com/$GH_USER/$REPO_NAME"
fi

echo ""
echo "🎉 Done! Your snippet manager is now on GitHub!"
