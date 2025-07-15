#!/bin/bash

# AUTO GIT PUSH SCRIPT
# Automatically commits and pushes all changes to GitHub
# Author: HEAD_OF_ENGINEERING
# Date: $(date)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 AUTO GIT PUSH - $(date)${NC}"
echo "============================================================"

# Navigate to repository root
cd "$(dirname "$0")"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    exit 1
fi

# Configure git to use the token for authentication
git config credential.helper store

# Check for changes
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${GREEN}✅ No changes to commit${NC}"
    exit 0
fi

echo -e "${YELLOW}📝 Changes detected, processing...${NC}"

# Add all changes
echo -e "${BLUE}📁 Adding all changes...${NC}"
git add -A

# Check if there are staged changes
if [ -z "$(git diff --cached --name-only)" ]; then
    echo -e "${GREEN}✅ No staged changes${NC}"
    exit 0
fi

# Create commit message with timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
COMMIT_MSG="Auto-commit: $TIMESTAMP"

# Count changes
ADDED=$(git diff --cached --name-only --diff-filter=A | wc -l)
MODIFIED=$(git diff --cached --name-only --diff-filter=M | wc -l)
DELETED=$(git diff --cached --name-only --diff-filter=D | wc -l)

echo -e "${BLUE}📊 Changes summary:${NC}"
echo -e "  Added: ${GREEN}$ADDED${NC} files"
echo -e "  Modified: ${YELLOW}$MODIFIED${NC} files"
echo -e "  Deleted: ${RED}$DELETED${NC} files"

# Commit changes
echo -e "${BLUE}💾 Committing changes...${NC}"
git commit -m "$COMMIT_MSG"

# Push to GitHub
echo -e "${BLUE}🚀 Pushing to GitHub...${NC}"
if git push origin main; then
    echo -e "${GREEN}✅ Successfully pushed to GitHub!${NC}"
    echo -e "${GREEN}🎉 Commit: $COMMIT_MSG${NC}"
else
    echo -e "${RED}❌ Failed to push to GitHub${NC}"
    exit 1
fi

echo -e "${GREEN}🔄 Auto-push completed successfully!${NC}"
echo "============================================================" 