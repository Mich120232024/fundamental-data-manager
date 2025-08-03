#!/usr/bin/env python3
"""
Parallel API Research Coordinator
Uses Claude Code's new /agents terminal function to research 476 APIs in parallel
"""

import json
import requests
import os
from datetime import datetime
from typing import List, Dict, Any
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

load_dotenv()

class APIResearchCoordinator:
    def __init__(self):
        # Cosmos DB setup
        self.cosmos_client = CosmosClient(
            os.getenv('COSMOS_ENDPOINT'), 
            os.getenv('COSMOS_KEY')
        )
        self.database = self.cosmos_client.get_database_client("data-collection-db")
        self.discovery_container = self.database.get_container_client("api_discovery")
        
        # Load enhanced schema
        with open('enhanced_api_research_schema.json', 'r') as f:
            self.schema = json.load(f)
    
    def get_apis_to_research(self) -> List[Dict]:
        """Get all APIs from discovery container that need research"""
        response = requests.get('http://localhost:8850/api/discovery')
        apis = response.json()
        
        # Filter APIs that need research (status = not_started or researching)
        need_research = [
            api for api in apis 
            if api.get('discovery_status') in ['not_started', 'researching']
        ]
        
        print(f"📋 Found {len(need_research)} APIs needing research out of {len(apis)} total")
        return need_research
    
    def create_research_batches(self, apis: List[Dict], batch_size: int = 25) -> List[List[Dict]]:
        """Split APIs into batches for parallel processing"""
        batches = []
        for i in range(0, len(apis), batch_size):
            batch = apis[i:i + batch_size]
            batches.append(batch)
        
        print(f"📦 Created {len(batches)} batches of ~{batch_size} APIs each")
        return batches
    
    def generate_subagent_prompt(self, batch: List[Dict], batch_id: int) -> str:
        """Generate research prompt for subagent"""
        api_list = "\n".join([
            f"- {api['name']} ({api['provider']}) - {api.get('description', 'No description')}"
            for api in batch
        ])
        
        return f"""
Research these {len(batch)} APIs comprehensively using web search and official documentation:

{api_list}

For EACH API, provide this JSON structure using REAL DATA from official sources:
{{
  "id": "original_api_id",
  "name": "Official API Name from documentation",
  "provider": "Actual Organization/Company Name", 
  "description": "2-3 sentence summary based on official documentation",
  "discovery_status": "documented",
  "tags": ["actual", "relevant", "tags"],
  "access_info": {{
    "is_free": true/false/null,
    "requires_api_key": true/false/null,
    "requires_approval": false,
    "pricing_model": "actual pricing model from docs",
    "rate_limits": "specific limits from documentation or 'unknown'"
  }},
  "technical_info": {{
    "base_url": "actual base URL from documentation",
    "protocol": "REST/GraphQL/SOAP based on documentation",
    "data_formats": ["formats supported by API"],
    "auth_method": "actual authentication method",
    "endpoints": [
      "List real endpoint paths with descriptions from official docs"
    ]
  }},
  "content_summary": {{
    "data_categories": ["Actual data categories from documentation"],
    "geographic_scope": "based on API documentation",
    "update_frequency": "from official documentation",
    "historical_data": true/false/null
  }},
  "research_notes": {{
    "documentation_url": "actual URL to official API documentation",
    "sample_endpoints": ["real endpoints from documentation"],
    "data_quality": "assessment based on documentation quality",
    "last_researched": "{datetime.utcnow().isoformat()}Z",
    "researcher_notes": "insights from researching official sources",
    "api_summary": "comprehensive paragraph based on official documentation about capabilities, data, users, and value"
  }}
}}

RESEARCH REQUIREMENTS:
1. Find OFFICIAL documentation for each API - use web search
2. Extract REAL endpoint paths from documentation
3. Get ACTUAL pricing and authentication info
4. Identify REAL data categories provided
5. Write comprehensive summary based on official sources

OUTPUT: Return a JSON array with all researched APIs using REAL data only.

BATCH ID: {batch_id}
"""

    def save_research_prompts(self, batches: List[List[Dict]]) -> None:
        """Save individual research prompts for each batch"""
        os.makedirs('api_research_prompts', exist_ok=True)
        
        for i, batch in enumerate(batches):
            prompt = self.generate_subagent_prompt(batch, i+1)
            
            with open(f'api_research_prompts/batch_{i+1}_prompt.txt', 'w') as f:
                f.write(prompt)
            
            # Also save the API list for reference
            api_list = [{"id": api["id"], "name": api["name"], "provider": api["provider"]} for api in batch]
            with open(f'api_research_prompts/batch_{i+1}_apis.json', 'w') as f:
                json.dump(api_list, f, indent=2)
        
        print(f"💾 Saved {len(batches)} research prompts to api_research_prompts/")
    
    def create_results_merger(self) -> None:
        """Create script to merge results and update database"""
        merger_script = '''#!/usr/bin/env python3
"""
Merge API research results and update Cosmos DB
"""
import json
import os
import glob
from azure.cosmos import CosmosClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def merge_and_update_results():
    # Load all batch results
    result_files = glob.glob('api_research_results/batch_*.json')
    all_results = []
    
    for file_path in result_files:
        with open(file_path, 'r') as f:
            batch_results = json.load(f)
            all_results.extend(batch_results)
    
    print(f"📊 Loaded {len(all_results)} researched APIs from {len(result_files)} batches")
    
    # Connect to Cosmos DB
    cosmos_client = CosmosClient(os.getenv('COSMOS_ENDPOINT'), os.getenv('COSMOS_KEY'))
    database = cosmos_client.get_database_client("data-collection-db")
    container = database.get_container_client("api_discovery")
    
    # Update each API in the database
    updated_count = 0
    error_count = 0
    
    for api_data in all_results:
        try:
            # Add system metadata
            api_data['system_metadata'] = {
                'created_at': api_data.get('system_metadata', {}).get('created_at', datetime.utcnow().isoformat() + 'Z'),
                'updated_at': datetime.utcnow().isoformat() + 'Z',
                'version': 2,
                'research_completed': True
            }
            
            # Update in Cosmos DB
            container.upsert_item(api_data)
            updated_count += 1
            print(f"✅ Updated: {api_data['name']}")
            
        except Exception as e:
            print(f"❌ Failed to update {api_data.get('name', 'unknown')}: {e}")
            error_count += 1
    
    print(f"\\n🎉 Research merge complete!")
    print(f"   ✅ Updated: {updated_count} APIs")
    print(f"   ❌ Errors: {error_count} APIs")
    print(f"   📈 Success rate: {(updated_count/(updated_count+error_count)*100):.1f}%")

if __name__ == "__main__":
    merge_and_update_results()
'''
        
        with open('merge_research_results.py', 'w') as f:
            f.write(merger_script)
        
        print("💾 Created merge_research_results.py")

def main():
    coordinator = APIResearchCoordinator()
    
    print("🔍 Parallel API Research Coordinator")
    print("=" * 50)
    
    # Get APIs needing research
    apis = coordinator.get_apis_to_research()
    
    if not apis:
        print("✅ No APIs need research - all are already documented!")
        return
    
    # Create batches for parallel processing
    batches = coordinator.create_research_batches(apis, batch_size=25)
    
    # Save research prompts
    coordinator.save_research_prompts(batches)
    
    # Create results merger
    coordinator.create_results_merger()
    
    print("\\n🚀 PARALLEL RESEARCH SYSTEM READY!")
    print("=" * 50)
    print("Next steps:")
    print("1. Use /agents command to create research subagents")
    print("2. Give each subagent a research prompt from api_research_prompts/")
    print("3. Save results to api_research_results/batch_N.json")
    print("4. Run python merge_research_results.py to update database")
    
    print(f"\\n📂 Files created:")
    print(f"   📋 api_research_prompts/ - {len(batches)} research prompts")
    print(f"   🔄 merge_research_results.py - results processor")
    print(f"   📊 enhanced_api_research_schema.json - data schema")

if __name__ == "__main__":
    main()