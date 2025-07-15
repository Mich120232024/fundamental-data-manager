#!/usr/bin/env python3
"""
API Registry Browser - Interactive tool to browse and query the API registry container

Features:
- View all documents in table format
- Filter by category, status, auth type
- Search by name or provider
- View detailed document information
- Export results to JSON/CSV
"""

import os
import json
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
from azure.cosmos import CosmosClient
from dotenv import load_dotenv
from tabulate import tabulate
import sys

# Load environment variables
load_dotenv()

class APIRegistryBrowser:
    """Interactive browser for API Registry container"""
    
    def __init__(self):
        """Initialize browser with Cosmos DB connection"""
        cosmos_url = os.getenv("COSMOS_ENDPOINT")
        cosmos_key = os.getenv("COSMOS_KEY")
        
        if not cosmos_url or not cosmos_key:
            print("❌ Missing Cosmos DB credentials")
            sys.exit(1)
            
        self.client = CosmosClient(cosmos_url, cosmos_key)
        self.database = self.client.get_database_client("research-analytics-db")
        self.container = self.database.get_container_client("api_registry")
        self.current_results = []
    
    def run(self):
        """Main browser loop"""
        self.print_header()
        
        while True:
            self.print_menu()
            choice = input("\n📝 Enter your choice: ").strip()
            
            if choice == "1":
                self.view_all_documents()
            elif choice == "2":
                self.filter_by_category()
            elif choice == "3":
                self.filter_by_field()
            elif choice == "4":
                self.search_apis()
            elif choice == "5":
                self.view_document_details()
            elif choice == "6":
                self.view_schema_requirements()
            elif choice == "7":
                self.export_results()
            elif choice == "8":
                self.show_statistics()
            elif choice == "0":
                print("\n👋 Goodbye!")
                break
            else:
                print("\n❌ Invalid choice. Please try again.")
    
    def print_header(self):
        """Print browser header"""
        print("\n" + "="*70)
        print("🔍 API REGISTRY BROWSER")
        print("="*70)
        print("Browse and query the API Registry container interactively")
    
    def print_menu(self):
        """Print main menu"""
        print("\n" + "-"*50)
        print("MAIN MENU:")
        print("1. View all documents")
        print("2. Filter by category")
        print("3. Filter by field (status, authType, etc.)")
        print("4. Search APIs by name/provider")
        print("5. View document details")
        print("6. View schema requirements")
        print("7. Export results (JSON/CSV)")
        print("8. Show statistics")
        print("0. Exit")
    
    def view_all_documents(self):
        """View all documents in table format"""
        print("\n📊 Fetching all documents...")
        
        query = "SELECT * FROM c ORDER BY c.apiName"
        self.current_results = list(self.container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        self.display_results_table()
    
    def filter_by_category(self):
        """Filter documents by category"""
        # Get unique categories
        query = "SELECT DISTINCT c.category FROM c"
        categories = list(self.container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        print("\n📁 Available categories:")
        for i, cat in enumerate(categories):
            print(f"  {i+1}. {cat['category']}")
        
        choice = input("\nSelect category number: ").strip()
        try:
            category = categories[int(choice)-1]['category']
            
            query = f"SELECT * FROM c WHERE c.category = '{category}' ORDER BY c.apiName"
            self.current_results = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            self.display_results_table()
        except (ValueError, IndexError):
            print("❌ Invalid selection")
    
    def filter_by_field(self):
        """Filter by various fields"""
        print("\n🔍 Filter by field:")
        print("1. Status (active, deprecated, etc.)")
        print("2. Auth Type (api_key, oauth2, etc.)")
        print("3. Protocol (REST, GraphQL, etc.)")
        print("4. Pricing Model (free, paid, etc.)")
        
        field_choice = input("\nSelect field: ").strip()
        
        field_map = {
            "1": ("status", "status"),
            "2": ("authType", "authType"),
            "3": ("protocol", "protocol"),
            "4": ("metadata.pricing.model", "pricing model")
        }
        
        if field_choice in field_map:
            field_path, field_name = field_map[field_choice]
            
            # Get unique values
            query = f"SELECT DISTINCT c.{field_path} as value FROM c WHERE IS_DEFINED(c.{field_path})"
            values = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            print(f"\n📋 Available {field_name} values:")
            for i, val in enumerate(values):
                print(f"  {i+1}. {val['value']}")
            
            value_choice = input(f"\nSelect {field_name}: ").strip()
            try:
                value = values[int(value_choice)-1]['value']
                
                query = f"SELECT * FROM c WHERE c.{field_path} = '{value}' ORDER BY c.apiName"
                self.current_results = list(self.container.query_items(
                    query=query,
                    enable_cross_partition_query=True
                ))
                
                self.display_results_table()
            except (ValueError, IndexError):
                print("❌ Invalid selection")
    
    def search_apis(self):
        """Search APIs by name or provider"""
        search_term = input("\n🔍 Enter search term (name or provider): ").strip()
        
        if search_term:
            query = f"""
            SELECT * FROM c 
            WHERE CONTAINS(LOWER(c.apiName), LOWER('{search_term}'))
               OR CONTAINS(LOWER(c.provider), LOWER('{search_term}'))
            ORDER BY c.apiName
            """
            
            self.current_results = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            self.display_results_table()
    
    def view_document_details(self):
        """View detailed information for a specific document"""
        if not self.current_results:
            print("\n❌ No results to display. Please run a query first.")
            return
        
        print("\n📄 Current results:")
        for i, doc in enumerate(self.current_results):
            print(f"  {i+1}. {doc.get('apiName', doc.get('id'))}")
        
        choice = input("\nSelect document number to view details: ").strip()
        try:
            doc = self.current_results[int(choice)-1]
            
            print("\n" + "="*60)
            print(f"📋 DOCUMENT DETAILS: {doc.get('apiName', doc.get('id'))}")
            print("="*60)
            
            # Pretty print the document
            print(json.dumps(doc, indent=2, default=str))
            
            input("\nPress Enter to continue...")
        except (ValueError, IndexError):
            print("❌ Invalid selection")
    
    def view_schema_requirements(self):
        """View schema requirements document"""
        try:
            schema_doc = self.container.read_item(
                item="schema_requirements_v1",
                partition_key="system"
            )
            
            print("\n📋 SCHEMA REQUIREMENTS")
            print("="*60)
            print("Each field shows what is required for API entries:\n")
            
            # Display key fields
            fields_to_show = [
                "apiName", "provider", "version", "description",
                "baseUrl", "authType", "protocol", "dataFormat", "status"
            ]
            
            for field in fields_to_show:
                if field in schema_doc:
                    print(f"{field}:")
                    print(f"  → {schema_doc[field]}\n")
            
            input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f"❌ Error viewing schema: {e}")
    
    def show_statistics(self):
        """Show container statistics"""
        print("\n📊 API REGISTRY STATISTICS")
        print("="*60)
        
        # Total count
        count_query = "SELECT VALUE COUNT(1) FROM c"
        total_count = list(self.container.query_items(
            query=count_query,
            enable_cross_partition_query=True
        ))[0]
        
        print(f"Total documents: {total_count}")
        
        # By category
        category_query = """
        SELECT c.category, COUNT(1) as count 
        FROM c 
        GROUP BY c.category
        """
        try:
            categories = list(self.container.query_items(
                query=category_query,
                enable_cross_partition_query=True
            ))
            
            print("\nBy Category:")
            for cat in categories:
                print(f"  • {cat['category']}: {cat['count']}")
        except:
            # Fallback if GROUP BY not supported
            print("\nCategory statistics not available")
        
        # By status
        status_query = "SELECT DISTINCT c.status FROM c WHERE IS_DEFINED(c.status)"
        statuses = list(self.container.query_items(
            query=status_query,
            enable_cross_partition_query=True
        ))
        
        print("\nBy Status:")
        for status in statuses:
            count_query = f"SELECT VALUE COUNT(1) FROM c WHERE c.status = '{status['status']}'"
            count = list(self.container.query_items(
                query=count_query,
                enable_cross_partition_query=True
            ))[0]
            print(f"  • {status['status']}: {count}")
        
        input("\nPress Enter to continue...")
    
    def display_results_table(self):
        """Display query results in table format"""
        if not self.current_results:
            print("\n❌ No results found.")
            return
        
        print(f"\n📊 Found {len(self.current_results)} results:")
        
        # Prepare table data
        table_data = []
        headers = ["#", "Name", "Provider", "Category", "Status", "Auth", "Protocol"]
        
        for i, doc in enumerate(self.current_results):
            # Skip system documents in table view
            if doc.get('category') == 'system':
                continue
                
            row = [
                i + 1,
                doc.get('apiName', doc.get('id', 'N/A'))[:30],
                doc.get('provider', 'N/A')[:20],
                doc.get('category', 'N/A'),
                doc.get('status', 'N/A'),
                doc.get('authType', 'N/A'),
                doc.get('protocol', 'N/A')
            ]
            table_data.append(row)
        
        if table_data:
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        else:
            print("\n(No API documents to display)")
    
    def export_results(self):
        """Export current results to file"""
        if not self.current_results:
            print("\n❌ No results to export. Please run a query first.")
            return
        
        print("\n💾 Export format:")
        print("1. JSON")
        print("2. CSV")
        
        format_choice = input("\nSelect format: ").strip()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_choice == "1":
            # Export to JSON
            filename = f"api_registry_export_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(self.current_results, f, indent=2, default=str)
            print(f"✅ Exported to {filename}")
            
        elif format_choice == "2":
            # Export to CSV
            filename = f"api_registry_export_{timestamp}.csv"
            
            if self.current_results:
                # Get all unique keys from all documents
                all_keys = set()
                for doc in self.current_results:
                    all_keys.update(self._flatten_dict(doc).keys())
                
                with open(filename, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                    writer.writeheader()
                    
                    for doc in self.current_results:
                        flat_doc = self._flatten_dict(doc)
                        writer.writerow(flat_doc)
                
                print(f"✅ Exported to {filename}")
        else:
            print("❌ Invalid format selection")
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary for CSV export"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, json.dumps(v)))
            else:
                items.append((new_key, v))
        return dict(items)

def main():
    """Main entry point"""
    try:
        browser = APIRegistryBrowser()
        browser.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()