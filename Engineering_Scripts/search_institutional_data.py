#!/usr/bin/env python3
"""
Search institutional-data-center Cosmos DB container for documents related to:
- Multi-box architecture issues or message failures
- Governance methods adoption rates or patterns
- Architectural bugs or communication problems
- Role definition conflicts or governance theater
- System deployment issues or architectural patterns
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class InstitutionalDataSearcher:
    """Search institutional-data-center container for critical issues"""
    
    def __init__(self):
        """Initialize Cosmos DB client for institutional-data-center"""
        self.endpoint = os.getenv('COSMOS_ENDPOINT')
        self.key = os.getenv('COSMOS_KEY')
        self.database_name = os.getenv('COSMOS_DATABASE', 'research-analytics-db')
        self.container_name = 'institutional-data-center'  # Target container
        
        if not self.endpoint or not self.key:
            raise ValueError("COSMOS_ENDPOINT and COSMOS_KEY must be set in .env file")
        
        # Initialize client and connections
        self.client = CosmosClient(self.endpoint, self.key)
        self.database = self.client.get_database_client(self.database_name)
        self.container = self.database.get_container_client(self.container_name)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('InstitutionalDataSearcher')
    
    def search_architecture_issues(self) -> List[Dict[str, Any]]:
        """Search for multi-box architecture and message failure documents"""
        queries = [
            # Multi-box architecture issues
            """SELECT * FROM c WHERE 
               CONTAINS(LOWER(c.content), 'multi-box') OR 
               CONTAINS(LOWER(c.content), 'multibox') OR
               CONTAINS(LOWER(c.content), 'multi box') OR
               CONTAINS(LOWER(c.title), 'multi-box') OR
               CONTAINS(LOWER(c.subject), 'multi-box')""",
            
            # Message failures
            """SELECT * FROM c WHERE 
               CONTAINS(LOWER(c.content), 'message failure') OR 
               CONTAINS(LOWER(c.content), 'message failed') OR
               CONTAINS(LOWER(c.content), 'communication failure') OR
               CONTAINS(LOWER(c.content), 'delivery failure')""",
            
            # Architectural bugs
            """SELECT * FROM c WHERE 
               CONTAINS(LOWER(c.content), 'architectural bug') OR 
               CONTAINS(LOWER(c.content), 'architecture bug') OR
               CONTAINS(LOWER(c.content), 'system architecture') AND 
               (CONTAINS(LOWER(c.content), 'bug') OR CONTAINS(LOWER(c.content), 'issue'))"""
        ]
        
        results = []
        for query in queries:
            try:
                items = list(self.container.query_items(query, enable_cross_partition_query=True))
                results.extend(items)
                self.logger.info(f"Architecture query found {len(items)} results")
            except Exception as e:
                self.logger.error(f"Architecture query failed: {str(e)}")
        
        return self._deduplicate_results(results)
    
    def search_governance_patterns(self) -> List[Dict[str, Any]]:
        """Search for governance methods adoption and patterns"""
        queries = [
            # Governance methods adoption
            """SELECT * FROM c WHERE 
               CONTAINS(LOWER(c.content), 'governance method') OR 
               CONTAINS(LOWER(c.content), 'adoption rate') OR
               CONTAINS(LOWER(c.content), 'governance adoption') OR
               CONTAINS(LOWER(c.content), 'method adoption')""",
            
            # Governance theater
            """SELECT * FROM c WHERE 
               CONTAINS(LOWER(c.content), 'governance theater') OR 
               CONTAINS(LOWER(c.content), 'governance theatre') OR
               CONTAINS(LOWER(c.content), 'performative governance') OR
               CONTAINS(LOWER(c.content), 'checkbox governance')""",
            
            # Role definition conflicts
            """SELECT * FROM c WHERE 
               CONTAINS(LOWER(c.content), 'role definition') OR 
               CONTAINS(LOWER(c.content), 'role conflict') OR
               CONTAINS(LOWER(c.content), 'governance role') OR
               CONTAINS(LOWER(c.content), 'constitutional role')"""
        ]
        
        results = []
        for query in queries:
            try:
                items = list(self.container.query_items(query, enable_cross_partition_query=True))
                results.extend(items)
                self.logger.info(f"Governance query found {len(items)} results")
            except Exception as e:
                self.logger.error(f"Governance query failed: {str(e)}")
        
        return self._deduplicate_results(results)
    
    def search_deployment_issues(self) -> List[Dict[str, Any]]:
        """Search for system deployment and architectural pattern issues"""
        queries = [
            # Deployment issues
            """SELECT * FROM c WHERE 
               CONTAINS(LOWER(c.content), 'deployment issue') OR 
               CONTAINS(LOWER(c.content), 'deployment failure') OR
               CONTAINS(LOWER(c.content), 'system deployment') OR
               CONTAINS(LOWER(c.content), 'deploy fail')""",
            
            # Architectural patterns
            """SELECT * FROM c WHERE 
               CONTAINS(LOWER(c.content), 'architectural pattern') OR 
               CONTAINS(LOWER(c.content), 'architecture pattern') OR
               CONTAINS(LOWER(c.content), 'system pattern') OR
               CONTAINS(LOWER(c.content), 'design pattern')"""
        ]
        
        results = []
        for query in queries:
            try:
                items = list(self.container.query_items(query, enable_cross_partition_query=True))
                results.extend(items)
                self.logger.info(f"Deployment query found {len(items)} results")
            except Exception as e:
                self.logger.error(f"Deployment query failed: {str(e)}")
        
        return self._deduplicate_results(results)
    
    def search_general_terms(self, terms: List[str]) -> List[Dict[str, Any]]:
        """Search for documents containing specific terms"""
        results = []
        for term in terms:
            query = f"""SELECT * FROM c WHERE 
                       CONTAINS(LOWER(c.content), '{term.lower()}') OR 
                       CONTAINS(LOWER(c.title), '{term.lower()}') OR
                       CONTAINS(LOWER(c.subject), '{term.lower()}')"""
            
            try:
                items = list(self.container.query_items(query, enable_cross_partition_query=True))
                results.extend(items)
                self.logger.info(f"Term '{term}' found {len(items)} results")
            except Exception as e:
                self.logger.error(f"Search for '{term}' failed: {str(e)}")
        
        return self._deduplicate_results(results)
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on document ID"""
        seen = set()
        unique = []
        for item in results:
            if item.get('id') not in seen:
                seen.add(item.get('id'))
                unique.append(item)
        return unique
    
    def format_result(self, doc: Dict[str, Any]) -> str:
        """Format a document for display"""
        output = []
        output.append(f"\n{'='*80}")
        output.append(f"ID: {doc.get('id', 'N/A')}")
        output.append(f"Type: {doc.get('type', 'N/A')}")
        output.append(f"Title: {doc.get('title', doc.get('subject', 'N/A'))}")
        output.append(f"From: {doc.get('from', 'N/A')}")
        output.append(f"Date: {doc.get('timestamp', doc.get('createdDate', 'N/A'))}")
        
        if 'tags' in doc:
            output.append(f"Tags: {', '.join(doc['tags'])}")
        
        output.append("\nContent Preview:")
        content = doc.get('content', doc.get('body', 'No content available'))
        if isinstance(content, str):
            # Show first 500 characters
            preview = content[:500] + "..." if len(content) > 500 else content
            output.append(preview)
        
        return '\n'.join(output)

def main():
    """Execute searches and display results"""
    try:
        searcher = InstitutionalDataSearcher()
        
        print("\n🔍 SEARCHING INSTITUTIONAL DATA CENTER")
        print("="*80)
        
        # Search for architecture issues
        print("\n📊 ARCHITECTURE & MESSAGE FAILURE ISSUES:")
        arch_results = searcher.search_architecture_issues()
        print(f"Found {len(arch_results)} documents")
        for doc in arch_results[:5]:  # Show first 5
            print(searcher.format_result(doc))
        
        # Search for governance patterns
        print("\n📋 GOVERNANCE PATTERNS & ADOPTION:")
        gov_results = searcher.search_governance_patterns()
        print(f"Found {len(gov_results)} documents")
        for doc in gov_results[:5]:  # Show first 5
            print(searcher.format_result(doc))
        
        # Search for deployment issues
        print("\n🚀 DEPLOYMENT & SYSTEM ISSUES:")
        deploy_results = searcher.search_deployment_issues()
        print(f"Found {len(deploy_results)} documents")
        for doc in deploy_results[:5]:  # Show first 5
            print(searcher.format_result(doc))
        
        # Search for specific critical terms
        print("\n🔎 SPECIFIC CRITICAL TERMS:")
        critical_terms = [
            "SAM", "critical issue", "system failure", "communication breakdown",
            "architecture review", "governance failure", "adoption barrier"
        ]
        term_results = searcher.search_general_terms(critical_terms)
        print(f"Found {len(term_results)} documents")
        for doc in term_results[:5]:  # Show first 5
            print(searcher.format_result(doc))
        
        # Summary
        total_unique = len(set(
            doc.get('id') for results in [arch_results, gov_results, deploy_results, term_results] 
            for doc in results if doc.get('id')
        ))
        
        print(f"\n📊 SUMMARY:")
        print(f"Total unique documents found: {total_unique}")
        print(f"- Architecture issues: {len(arch_results)}")
        print(f"- Governance patterns: {len(gov_results)}")
        print(f"- Deployment issues: {len(deploy_results)}")
        print(f"- Critical terms: {len(term_results)}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("Please ensure your .env file is configured with valid Cosmos DB credentials")

if __name__ == "__main__":
    main()