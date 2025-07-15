#!/bin/bash

# GitHub Repository Creation Script
# This script creates GitHub repositories for all standalone projects (excluding gzc)

echo "🚀 GITHUB REPOSITORY CREATION GUIDE"
echo "======================================"
echo ""
echo "Since the GitHub CLI has permission issues, you'll need to create these repositories manually."
echo "Here are the repositories to create and their descriptions:"
echo ""

# Define projects with descriptions
declare -A projects=(
    ["knowledge-graph-explorer-demo"]="Interactive knowledge graph visualization with live institutional memory integration"
    ["knowledge-graph-professional"]="Production-ready knowledge graph system with advanced features"
    ["knowledge-graph-standalone"]="Self-contained knowledge graph solution"
    ["ready-to-integrate-component"]="Production-ready React components with TypeScript and npm package structure"
    ["mcp-server-professional"]="Professional MCP server with enhanced API discovery and categorization"
    ["generic-api-collector"]="Universal API discovery framework with 7-step process guide"
    ["azure-validation-toolkit"]="Comprehensive Azure resource validation and testing toolkit"
    ["fx-client-reproduction"]="Foreign exchange client implementation and analysis tools"
    ["fx-spot-stream-project"]="FX spot streaming data analysis and visualization platform"
    ["user-dashboard-clean"]="Clean user dashboard implementation"
    ["user-dashboard-flask"]="Flask-based user dashboard with backend API"
)

echo "📋 REPOSITORIES TO CREATE:"
echo "--------------------------"
counter=1
for project in "${!projects[@]}"; do
    echo "$counter. $project"
    echo "   Description: ${projects[$project]}"
    echo "   Status: $([ -d "$project/.git" ] && echo "✅ Git initialized" || echo "❌ Needs git setup")"
    echo ""
    ((counter++))
done

echo ""
echo "🔧 MANUAL CREATION STEPS:"
echo "-------------------------"
echo "1. Go to https://github.com/new"
echo "2. For each project above:"
echo "   - Repository name: [project-name]"
echo "   - Description: [use description above]"
echo "   - Set to Public"
echo "   - Don't initialize with README (we have local files)"
echo "   - Click 'Create repository'"
echo ""

echo "📤 PUSH COMMANDS:"
echo "----------------"
echo "After creating each repository on GitHub, run these commands:"
echo ""

for project in "${!projects[@]}"; do
    if [ -d "$project/.git" ]; then
        echo "# $project"
        echo "cd '$project'"
        echo "git remote add origin https://github.com/Mich120232024/$project.git"
        echo "git branch -M main"
        echo "git push -u origin main"
        echo "cd .."
        echo ""
    fi
done

echo "🎯 QUICK SETUP REMAINING PROJECTS:"
echo "-----------------------------------"
echo "For projects that don't have git initialized yet:"
echo ""

for project in "${!projects[@]}"; do
    if [ ! -d "$project/.git" ] && [ -d "$project" ]; then
        echo "# Setup $project"
        echo "cd '$project'"
        echo "git init"
        echo "echo 'node_modules/\n*.log\n.env\n.DS_Store\n__pycache__/\n*.pyc\nbuild/\ndist/' > .gitignore"
        echo "git add ."
        echo "git commit -m 'Initial commit: ${projects[$project]}'"
        echo "git remote add origin https://github.com/Mich120232024/$project.git"
        echo "git branch -M main"
        echo "git push -u origin main"
        echo "cd .."
        echo ""
    fi
done

echo "✅ COMPLETION CHECKLIST:"
echo "------------------------"
echo "□ Created all repositories on GitHub"
echo "□ Pushed all initialized projects"
echo "□ Set up remaining projects with git"
echo "□ Verified all repositories are public and accessible"
echo ""
echo "🎉 When complete, you'll have $(echo "${!projects[@]}" | wc -w | tr -d ' ') standalone repositories!" 