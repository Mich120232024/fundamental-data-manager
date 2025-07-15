#!/usr/bin/env python3
"""
Azure FRED Data Validation Script
Validates that FRED foundation data in Azure matches local data
"""

import json
import os
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

# Azure Configuration
STORAGE_ACCOUNT = "gzcstorageaccount"
CONTAINER_NAME = "federal-reserve-data"
LOCAL_DATA_DIR = "fred_metadata_extraction/fred_complete_data"

def compare_json_files(azure_data, local_file_path):
    """Compare Azure JSON data with local file"""
    try:
        with open(local_file_path, 'r') as f:
            local_data = json.load(f)
        
        if azure_data == local_data:
            return "✅ MATCH", len(local_data) if isinstance(local_data, list) else "N/A"
        else:
            return "❌ DIFFERENT", f"Azure: {len(azure_data) if isinstance(azure_data, list) else 'N/A'}, Local: {len(local_data) if isinstance(local_data, list) else 'N/A'}"
    except Exception as e:
        return f"❌ ERROR: {str(e)}", "N/A"

def main():
    print("🔍 FRED Azure Data Validation")
    print("=" * 50)
    
    try:
        # Initialize Azure client
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(
            account_url=f"https://{STORAGE_ACCOUNT}.blob.core.windows.net",
            credential=credential
        )
        
        # Files to validate
        files_to_check = [
            "categories_complete_hierarchy.json",
            "categories_leaf_only.json", 
            "sample_150_series_complete.json",
            "tags_complete.json"
        ]
        
        print("📊 Validation Results:")
        print("-" * 50)
        
        total_matches = 0
        for filename in files_to_check:
            try:
                # Download from Azure
                blob_client = blob_service_client.get_blob_client(
                    container=CONTAINER_NAME, 
                    blob=filename
                )
                azure_content = blob_client.download_blob().readall()
                azure_data = json.loads(azure_content.decode('utf-8'))
                
                # Compare with local
                local_path = os.path.join(LOCAL_DATA_DIR, filename)
                status, details = compare_json_files(azure_data, local_path)
                
                print(f"{filename:<35} {status} ({details})")
                
                if "✅ MATCH" in status:
                    total_matches += 1
                    
            except Exception as e:
                print(f"{filename:<35} ❌ ERROR: {str(e)}")
        
        print("-" * 50)
        print(f"📋 Summary: {total_matches}/{len(files_to_check)} files match")
        
        if total_matches == len(files_to_check):
            print("🎉 EXCELLENT! All FRED foundation data in Azure matches local data")
            print("✅ Ready to proceed with Azure-scale collection")
        else:
            print("⚠️  Some files don't match - investigation needed")
            
        # Test Azure infrastructure connectivity
        print("\n🏗️ Azure Infrastructure Test:")
        print("-" * 50)
        
        # List all containers
        containers = blob_service_client.list_containers()
        container_names = [c.name for c in containers]
        print(f"✅ Storage containers accessible: {len(container_names)}")
        
        # Check if FRED container exists
        if CONTAINER_NAME in container_names:
            print(f"✅ FRED container '{CONTAINER_NAME}' found")
        else:
            print(f"❌ FRED container '{CONTAINER_NAME}' not found")
            
    except Exception as e:
        print(f"❌ Azure connection failed: {str(e)}")
        print("💡 Tip: Run 'az login' to authenticate with Azure")

if __name__ == "__main__":
    main() 