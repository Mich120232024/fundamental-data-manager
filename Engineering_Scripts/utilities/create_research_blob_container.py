#!/usr/bin/env python3
"""
Create Research Blob Container - HEAD_OF_RESEARCH
"""

import os
from pathlib import Path
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Load environment - try multiple paths
env_paths = [
    Path(__file__).parent.parent / '.env',
    Path(__file__).parent.parent.parent / '.env',
    Path.cwd() / '.env'
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded environment from: {env_path}")
        break
else:
    print("⚠️  No .env file found, checking environment variables")

def create_research_container():
    """Create dedicated blob container for HEAD_OF_RESEARCH"""
    
    print("🗂️  Creating Research Blob Container")
    print("=" * 60)
    
    try:
        # Initialize blob service client
        connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        if not connection_string:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING not found in environment")
            
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Container name for research content
        container_name = "research-content-blob"
        
        # Create container with metadata
        container_metadata = {
            "owner": "HEAD_OF_RESEARCH",
            "purpose": "hybrid_storage_pipeline",
            "content_type": "research_documents",
            "created": "2025-06-20",
            "architecture": "blob_cosmos_gremlin"
        }
        
        # Check if container exists
        container_client = blob_service_client.get_container_client(container_name)
        
        try:
            properties = container_client.get_container_properties()
            print(f"✅ Container '{container_name}' already exists")
            print(f"   Created: {properties.last_modified}")
            print(f"   Metadata: {properties.metadata}")
            
        except Exception:
            # Container doesn't exist, create it
            container_client = blob_service_client.create_container(
                name=container_name,
                metadata=container_metadata
            )
            print(f"✅ Created container: {container_name}")
            print(f"   Metadata: {container_metadata}")
        
        # Create directory structure via empty blobs with metadata
        directory_structure = [
            "raw_research/documents/",
            "raw_research/papers/", 
            "raw_research/reports/",
            "processed/chunks/",
            "processed/embeddings/",
            "processed/metadata/",
            "ai_ready/llm_formatted/",
            "ai_ready/nlp_jobs/",
            "archive/",
        ]
        
        print(f"\n📁 Creating directory structure:")
        for directory in directory_structure:
            try:
                # Create .gitkeep equivalent for blob storage
                blob_name = f"{directory}.directory_marker"
                blob_client = container_client.get_blob_client(blob_name)
                
                # Check if marker exists
                try:
                    blob_client.get_blob_properties()
                    print(f"   ✓ {directory} (exists)")
                except:
                    # Create directory marker
                    blob_client.upload_blob(
                        data=f"Directory marker for {directory}",
                        metadata={
                            "type": "directory_marker",
                            "path": directory,
                            "created": "2025-06-20"
                        }
                    )
                    print(f"   ✓ {directory} (created)")
                    
            except Exception as e:
                print(f"   ❌ {directory} (error: {e})")
        
        # Test container access
        print(f"\n🔍 Testing container access:")
        blobs = list(container_client.list_blobs(name_starts_with="raw_research/"))
        print(f"   Accessible blobs in raw_research/: {len(blobs)}")
        
        # Return container info
        container_info = {
            "container_name": container_name,
            "connection_verified": True,
            "directory_structure": directory_structure,
            "blob_count": len(list(container_client.list_blobs())),
            "url": f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}"
        }
        
        print(f"\n✅ Container setup complete:")
        print(f"   Name: {container_name}")
        print(f"   URL: {container_info['url']}")
        print(f"   Total blobs: {container_info['blob_count']}")
        
        return container_info
        
    except Exception as e:
        print(f"❌ Error creating container: {str(e)}")
        return None

if __name__ == "__main__":
    result = create_research_container()
    if result:
        print(f"\n🎯 SUCCESS: Research blob container ready for hybrid pipeline")
    else:
        print(f"\n❌ FAILED: Could not create research blob container")