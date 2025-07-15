#!/usr/bin/env python3
"""
Test the Generic API Discovery Framework
Demonstrates real-world usage with multiple APIs
"""

import os
import json
from datetime import datetime

# Import our framework implementations
from fred_implementation import FREDDiscovery
from eurostat_implementation import EurostatDiscovery, BankOfJapanDiscovery

def test_fred_discovery():
    """Test FRED API discovery"""
    print("\n" + "="*60)
    print("🏦 Testing FRED API Discovery")
    print("="*60)
    
    # Use environment variable or placeholder
    api_key = os.getenv("FRED_API_KEY", "21acd97c4988e53af02e98587d5424d0")
    
    try:
        fred = FREDDiscovery(api_key)
        fred.setup_authentication()
        
        # Discover endpoints
        endpoints = fred.discover_endpoints()
        print(f"\n✅ Discovered {len(endpoints)} FRED endpoints:")
        for name, ep in list(endpoints.items())[:5]:
            print(f"   - {name}: {ep.description}")
        
        # Analyze patterns
        patterns = fred.analyze_fred_patterns()
        print(f"\n📊 FRED Patterns:")
        print(f"   - Rate limit: {patterns['rate_limiting']['limit']} req/min")
        print(f"   - Pagination: {patterns['pagination']['type']}")
        print(f"   - Max page size: {patterns['pagination']['max_limit']}")
        
        # Generate collection strategy
        strategy = fred.generate_collection_strategy()
        print(f"\n📋 Collection Strategy:")
        print(f"   Priority order: {strategy['collection_order'][:3]}...")
        
        # Export schema
        fred.export_schema("output/fred_schema.yaml")
        print(f"\n💾 Schema exported to: output/fred_schema.yaml")
        
        return True
        
    except Exception as e:
        print(f"❌ FRED test failed: {e}")
        return False


def test_eurostat_discovery():
    """Test Eurostat API discovery"""
    print("\n" + "="*60)
    print("🇪🇺 Testing Eurostat API Discovery")
    print("="*60)
    
    try:
        eurostat = EurostatDiscovery()
        eurostat.setup_authentication()
        
        # Discover endpoints
        endpoints = eurostat.discover_endpoints()
        print(f"\n✅ Discovered {len(endpoints)} Eurostat endpoints:")
        for name, ep in endpoints.items():
            print(f"   - {name}: {ep.description}")
        
        # Discover hierarchy
        eurostat.discover_eurostat_hierarchy()
        print(f"\n🏗️ Eurostat Hierarchy:")
        for parent, children in eurostat.schema.data_hierarchy.items():
            print(f"   {parent} → {', '.join(children)}")
        
        # Analyze patterns
        patterns = eurostat.analyze_eurostat_patterns()
        print(f"\n📊 Eurostat Patterns:")
        print(f"   - Data format: {patterns['data_format']['primary']}")
        print(f"   - Multilingual: {patterns['metadata_structure']['multilingual']}")
        
        # Export schema
        eurostat.export_schema("output/eurostat_schema.yaml")
        print(f"\n💾 Schema exported to: output/eurostat_schema.yaml")
        
        return True
        
    except Exception as e:
        print(f"❌ Eurostat test failed: {e}")
        return False


def test_boj_discovery():
    """Test Bank of Japan API discovery"""
    print("\n" + "="*60)
    print("🏯 Testing Bank of Japan API Discovery")
    print("="*60)
    
    try:
        boj = BankOfJapanDiscovery()
        boj.setup_authentication()
        
        # Discover endpoints
        endpoints = boj.discover_endpoints()
        print(f"\n✅ Discovered {len(endpoints)} BoJ endpoints:")
        for name, ep in endpoints.items():
            print(f"   - {name}: {ep.description}")
        
        # Generate collection strategy
        strategy = boj.generate_collection_strategy()
        print(f"\n📋 Collection Strategy:")
        for name, details in strategy['endpoint_strategies'].items():
            print(f"   - {name}: {details['strategy']} (priority: {details['priority']})")
        
        # Export schema
        boj.export_schema("output/boj_schema.yaml")
        print(f"\n💾 Schema exported to: output/boj_schema.yaml")
        
        return True
        
    except Exception as e:
        print(f"❌ BoJ test failed: {e}")
        return False


def compare_api_patterns():
    """Compare patterns across different APIs"""
    print("\n" + "="*60)
    print("🔍 Comparing API Patterns")
    print("="*60)
    
    comparison = {
        "FRED": {
            "auth": "API key in query params",
            "pagination": "offset/limit",
            "hierarchy": "categories → series → observations",
            "id_system": "mixed (numeric + string)",
            "rate_limit": "120/minute"
        },
        "Eurostat": {
            "auth": "public/open",
            "pagination": "dimension filtering",
            "hierarchy": "themes → datasets → dimensions",
            "id_system": "string codes",
            "rate_limit": "generous"
        },
        "Bank of Japan": {
            "auth": "public/open",
            "pagination": "date range",
            "hierarchy": "categories → statistics → timeseries",
            "id_system": "alphanumeric codes",
            "rate_limit": "reasonable"
        }
    }
    
    print("\n📊 API Comparison Matrix:")
    print(f"{'Feature':<20} {'FRED':<25} {'Eurostat':<25} {'BoJ':<25}")
    print("-" * 95)
    
    for feature in ['auth', 'pagination', 'hierarchy', 'id_system', 'rate_limit']:
        print(f"{feature:<20}", end="")
        for api in ['FRED', 'Eurostat', 'Bank of Japan']:
            value = comparison.get(api.replace(" ", ""), {}).get(feature, "N/A")
            print(f" {value:<24}", end="")
        print()


def main():
    """Run all tests"""
    print("🚀 Generic API Discovery Framework Test Suite")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Run tests
    results = {
        "FRED": test_fred_discovery(),
        "Eurostat": test_eurostat_discovery(),
        "Bank of Japan": test_boj_discovery()
    }
    
    # Compare patterns
    compare_api_patterns()
    
    # Summary
    print("\n" + "="*60)
    print("📝 Test Summary")
    print("="*60)
    
    for api, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{api:<20} {status}")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create summary report
    summary = {
        "test_run": datetime.now().isoformat(),
        "results": results,
        "apis_tested": list(results.keys()),
        "success_rate": sum(results.values()) / len(results) * 100
    }
    
    with open("output/test_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📄 Summary report saved to: output/test_summary.json")


if __name__ == "__main__":
    main()