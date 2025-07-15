#!/usr/bin/env python3
"""
Deploy Claude Code Database Specialist to Azure
"""
import subprocess
import json

def deploy_claude_specialist():
    """Deploy Claude Code web wrapper to Azure Container Apps."""
    
    print("🚀 Deploying Claude Code Database Specialist to Azure")
    print("=" * 60)
    
    # Configuration
    config = {
        "resource_group": "research-analytics-rg",
        "container_app_name": "claude-code-db-specialist",
        "container_registry": "gzcacr.azurecr.io",
        "image_name": "claude-code-db-specialist",
        "image_tag": "v1.0.0"
    }
    
    deployment_steps = [
        "1. Build Docker image with Claude Code + Web wrapper",
        "2. Push to Azure Container Registry", 
        "3. Deploy to Azure Container Apps",
        "4. Configure environment variables",
        "5. Set up custom domain (optional)",
        "6. Test web interface"
    ]
    
    print("📋 Deployment Plan:")
    for step in deployment_steps:
        print(f"   {step}")
    
    print(f"\n🎯 Target Configuration:")
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    print(f"\n🌐 Expected URLs:")
    print(f"   Web Interface: https://{config['container_app_name']}.azurecontainerapps.io")
    print(f"   Health Check: https://{config['container_app_name']}.azurecontainerapps.io/health")
    
    print(f"\n💡 Usage:")
    print("   • Access via web browser for interactive prompts")
    print("   • Send database architecture questions")
    print("   • Get specialized responses for Cosmos DB, SQL, data pipelines")
    print("   • Integrated with your Azure environment")
    
    return config

def create_dockerfile():
    """Create Dockerfile for Claude Code specialist."""
    
    dockerfile_content = """
# Claude Code Database Specialist Container
FROM python:3.11-slim

# Install Node.js for Claude Code
RUN apt-get update && apt-get install -y \\
    curl \\
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \\
    && apt-get install -y nodejs \\
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY claude_code_web_wrapper.py .

# Create workspace directory
RUN mkdir -p /workspace

# Expose port
EXPOSE 8080

# Set environment variables
ENV ANTHROPIC_API_KEY=""
ENV AZURE_TENANT_ID=""
ENV AZURE_CLIENT_ID=""

# Run the web wrapper
CMD ["python", "claude_code_web_wrapper.py"]
"""
    
    with open("/Users/mikaeleage/Research & Analytics Services/Dockerfile.claude-specialist", "w") as f:
        f.write(dockerfile_content)
    
    print("✅ Created Dockerfile.claude-specialist")

def create_requirements():
    """Create requirements.txt for deployment."""
    
    requirements = """
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.12
aiofiles>=23.0.0
"""
    
    with open("/Users/mikaeleage/Research & Analytics Services/requirements-claude-specialist.txt", "w") as f:
        f.write(requirements)
    
    print("✅ Created requirements-claude-specialist.txt")

if __name__ == "__main__":
    config = deploy_claude_specialist()
    create_dockerfile()
    create_requirements()
    
    print(f"\n🎊 Ready to Deploy!")
    print("Next steps:")
    print("1. Run: az acr build --registry gzcacr --image claude-code-db-specialist:v1.0.0 -f Dockerfile.claude-specialist .")
    print("2. Deploy to Container Apps with the image")
    print("3. Configure ANTHROPIC_API_KEY environment variable")
    print("4. Access your Claude Code Database Specialist via web browser!")