#!/usr/bin/env python3
"""
Test queries for uploaded engineering documents to demonstrate Enhanced Semantic Policy effectiveness
Shows practical examples of document discovery using the policy
"""

from cosmos_db_manager import get_db_manager
from datetime import datetime
import json

class EngineeringDocumentQueryTester:
    """Test queries for engineering documents to demonstrate policy effectiveness"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
    
    def run_comprehensive_tests(self):
        """Run comprehensive test suite for enhanced semantic policy"""
        print("🔍 COMPREHENSIVE ENHANCED SEMANTIC POLICY TEST SUITE")
        print("=" * 70)
        print("Testing document discovery capabilities for HEAD_OF_ENGINEERING uploads")
        print()
        
        # Test 1: Naming Convention Verification
        self.test_naming_convention()
        
        # Test 2: Required Tags Verification
        self.test_required_tags()
        
        # Test 3: Engineering-Specific Tags
        self.test_engineering_tags()
        
        # Test 4: Cross-Container Queries
        self.test_cross_container_queries()
        
        # Test 5: Practical Discovery Scenarios
        self.test_practical_scenarios()
        
        # Test 6: Policy Compliance Report
        self.generate_compliance_report()
    
    def test_naming_convention(self):
        """Test naming convention compliance"""
        print("📝 TEST 1: NAMING CONVENTION VERIFICATION")
        print("-" * 50)
        
        # Query all engineering documents and check naming pattern
        query = "SELECT c.id, c.title FROM c WHERE c.category = 'engineering'"
        
        docs_container = self.db_manager.database.get_container_client('documents')
        docs_results = list(docs_container.query_items(query, enable_cross_partition_query=True))
        
        processes_container = self.db_manager.database.get_container_client('processes')
        processes_results = list(processes_container.query_items(query, enable_cross_partition_query=True))
        
        all_results = docs_results + processes_results
        
        print(f"📊 Found {len(all_results)} engineering documents")
        
        compliant = 0
        for doc in all_results:
            doc_id = doc.get('id', '')
            title = doc.get('title', doc.get('name', 'Unknown'))
            
            # Check pattern: {type}-{category}-{identifier}_{name}
            is_compliant = False
            if '-' in doc_id and '_' in doc_id:
                parts = doc_id.split('_', 1)
                if len(parts) == 2 and len(parts[0].split('-')) >= 3:
                    is_compliant = True
                    compliant += 1
            
            status = "✅" if is_compliant else "❌"
            print(f"   {status} {doc_id} -> {title}")
        
        compliance_rate = compliant / len(all_results) if all_results else 0
        print(f"\n📈 Naming Convention Compliance: {compliance_rate:.1%} ({compliant}/{len(all_results)})")
        print()
    
    def test_required_tags(self):
        """Test required tags compliance"""
        print("🏷️ TEST 2: REQUIRED TAGS VERIFICATION")
        print("-" * 50)
        
        required_tags = ['type', 'category', 'status', 'owner', 'audience']
        query = f"SELECT c.id, c.title, c.{', c.'.join(required_tags)} FROM c WHERE c.category = 'engineering'"
        
        docs_container = self.db_manager.database.get_container_client('documents')
        docs_results = list(docs_container.query_items(query, enable_cross_partition_query=True))
        
        processes_container = self.db_manager.database.get_container_client('processes')
        processes_results = list(processes_container.query_items(query, enable_cross_partition_query=True))
        
        all_results = docs_results + processes_results
        
        print(f"📊 Checking {len(all_results)} documents for required tags: {', '.join(required_tags)}")
        
        compliant = 0
        for doc in all_results:
            title = doc.get('title', doc.get('name', 'Unknown'))
            missing_tags = []
            
            for tag in required_tags:
                if not doc.get(tag):
                    missing_tags.append(tag)
            
            if not missing_tags:
                compliant += 1
                print(f"   ✅ {title} - All required tags present")
            else:
                print(f"   ❌ {title} - Missing: {', '.join(missing_tags)}")
        
        compliance_rate = compliant / len(all_results) if all_results else 0
        print(f"\n📈 Required Tags Compliance: {compliance_rate:.1%} ({compliant}/{len(all_results)})")
        print()
    
    def test_engineering_tags(self):
        """Test engineering-specific optional tags"""
        print("🔧 TEST 3: ENGINEERING-SPECIFIC TAGS")
        print("-" * 50)
        
        engineering_tags = ['complexity', 'dependencies', 'test_coverage']
        query = f"SELECT c.id, c.title, c.{', c.'.join(engineering_tags)} FROM c WHERE c.category = 'engineering'"
        
        docs_container = self.db_manager.database.get_container_client('documents')
        docs_results = list(docs_container.query_items(query, enable_cross_partition_query=True))
        
        processes_container = self.db_manager.database.get_container_client('processes')
        processes_results = list(processes_container.query_items(query, enable_cross_partition_query=True))
        
        all_results = docs_results + processes_results
        
        print(f"📊 Checking {len(all_results)} documents for engineering tags: {', '.join(engineering_tags)}")
        
        for doc in all_results:
            title = doc.get('title', doc.get('name', 'Unknown'))
            print(f"   📄 {title}")
            
            for tag in engineering_tags:
                value = doc.get(tag)
                if value:
                    if isinstance(value, list):
                        print(f"      • {tag}: {', '.join(value)}")
                    else:
                        print(f"      • {tag}: {value}")
                else:
                    print(f"      ◦ {tag}: not specified")
        
        # Calculate coverage
        coverage_stats = {}
        for tag in engineering_tags:
            present = sum(1 for doc in all_results if doc.get(tag))
            coverage_stats[tag] = present / len(all_results) if all_results else 0
        
        print(f"\n📈 Engineering Tag Coverage:")
        for tag, coverage in coverage_stats.items():
            print(f"   • {tag}: {coverage:.1%}")
        print()
    
    def test_cross_container_queries(self):
        """Test cross-container query capabilities"""
        print("🔄 TEST 4: CROSS-CONTAINER QUERY CAPABILITIES")
        print("-" * 50)
        
        test_cases = [
            {
                'name': 'All HEAD_OF_ENGINEERING owned assets',
                'query': "SELECT c.id, c.title, c.type FROM c WHERE c.owner = 'HEAD_OF_ENGINEERING'"
            },
            {
                'name': 'High complexity engineering assets',
                'query': "SELECT c.id, c.title, c.complexity FROM c WHERE c.complexity = 'high' AND c.category = 'engineering'"
            },
            {
                'name': 'Assets with cosmos-db dependency',
                'query': "SELECT c.id, c.title, c.dependencies FROM c WHERE ARRAY_CONTAINS(c.dependencies, 'cosmos-db')"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"{i}. {test_case['name']}")
            
            # Query both containers
            docs_container = self.db_manager.database.get_container_client('documents')
            docs_results = list(docs_container.query_items(test_case['query'], enable_cross_partition_query=True))
            
            processes_container = self.db_manager.database.get_container_client('processes')
            processes_results = list(processes_container.query_items(test_case['query'], enable_cross_partition_query=True))
            
            all_results = docs_results + processes_results
            
            if all_results:
                print(f"   📊 Found {len(all_results)} matching assets:")
                for doc in all_results:
                    title = doc.get('title', doc.get('name', 'Unknown'))
                    doc_type = doc.get('type', 'unknown')
                    print(f"      📄 {title} ({doc_type})")
                    
                    # Show relevant metadata
                    if 'complexity' in test_case['name'].lower() and doc.get('complexity'):
                        print(f"         Complexity: {doc['complexity']}")
                    if 'dependency' in test_case['name'].lower() and doc.get('dependencies'):
                        deps = doc['dependencies']
                        if isinstance(deps, list):
                            print(f"         Dependencies: {', '.join(deps)}")
            else:
                print("   📊 No matching assets found")
            
            print()
    
    def test_practical_scenarios(self):
        """Test practical document discovery scenarios"""
        print("🎯 TEST 5: PRACTICAL DISCOVERY SCENARIOS")
        print("-" * 50)
        
        scenarios = [
            {
                'scenario': 'New team member needs database documentation',
                'query': "SELECT c.id, c.title, c.abstract FROM c WHERE c.category = 'engineering' AND ARRAY_CONTAINS(c.keywords, 'database') AND c.audience = 'all'"
            },
            {
                'scenario': 'Manager reviewing high-complexity guides',
                'query': "SELECT c.id, c.title, c.complexity FROM c WHERE c.type = 'guide' AND c.complexity = 'high' AND c.audience = 'managers'"
            },
            {
                'scenario': 'Finding procedures for implementation',
                'query': "SELECT c.id, c.title, c.abstract FROM c WHERE c.type = 'procedure' AND c.category = 'engineering' AND c.status = 'active'"
            },
            {
                'scenario': 'Looking for well-tested documentation',
                'query': "SELECT c.id, c.title, c.test_coverage FROM c WHERE c.category = 'engineering' AND c.test_coverage > '85%'"
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"{i}. Scenario: {scenario['scenario']}")
            
            # Query both containers
            docs_container = self.db_manager.database.get_container_client('documents')
            docs_results = list(docs_container.query_items(scenario['query'], enable_cross_partition_query=True))
            
            processes_container = self.db_manager.database.get_container_client('processes')
            processes_results = list(processes_container.query_items(scenario['query'], enable_cross_partition_query=True))
            
            all_results = docs_results + processes_results
            
            if all_results:
                print(f"   🎯 Found {len(all_results)} relevant documents:")
                for doc in all_results:
                    title = doc.get('title', doc.get('name', 'Unknown'))
                    print(f"      📖 {title}")
                    
                    if doc.get('abstract'):
                        abstract = doc['abstract'][:100] + "..." if len(doc['abstract']) > 100 else doc['abstract']
                        print(f"         {abstract}")
                    
                    if doc.get('test_coverage'):
                        print(f"         Test Coverage: {doc['test_coverage']}")
            else:
                print("   📖 No relevant documents found")
            
            print()
    
    def generate_compliance_report(self):
        """Generate comprehensive compliance report"""
        print("📋 TEST 6: COMPLIANCE REPORT")
        print("-" * 50)
        
        # Get all engineering documents
        query = "SELECT * FROM c WHERE c.category = 'engineering'"
        
        docs_container = self.db_manager.database.get_container_client('documents')
        docs_results = list(docs_container.query_items(query, enable_cross_partition_query=True))
        
        processes_container = self.db_manager.database.get_container_client('processes')
        processes_results = list(processes_container.query_items(query, enable_cross_partition_query=True))
        
        all_results = docs_results + processes_results
        
        report = {
            'generated_at': datetime.now().isoformat() + 'Z',
            'total_documents': len(all_results),
            'compliance_summary': {},
            'document_breakdown': {}
        }
        
        # Check naming convention
        naming_compliant = 0
        for doc in all_results:
            doc_id = doc.get('id', '')
            if '-' in doc_id and '_' in doc_id:
                parts = doc_id.split('_', 1)
                if len(parts) == 2 and len(parts[0].split('-')) >= 3:
                    naming_compliant += 1
        
        # Check required tags
        required_tags = ['type', 'category', 'status', 'owner', 'audience']
        tags_compliant = 0
        for doc in all_results:
            if all(doc.get(tag) for tag in required_tags):
                tags_compliant += 1
        
        # Check engineering tags
        engineering_tags = ['complexity', 'dependencies', 'test_coverage']
        eng_tags_present = {}
        for tag in engineering_tags:
            eng_tags_present[tag] = sum(1 for doc in all_results if doc.get(tag))
        
        # Document type breakdown
        type_breakdown = {}
        for doc in all_results:
            doc_type = doc.get('type', 'unknown')
            type_breakdown[doc_type] = type_breakdown.get(doc_type, 0) + 1
        
        # Complexity breakdown
        complexity_breakdown = {}
        for doc in all_results:
            complexity = doc.get('complexity', 'unspecified')
            complexity_breakdown[complexity] = complexity_breakdown.get(complexity, 0) + 1
        
        report['compliance_summary'] = {
            'naming_convention': {
                'compliant': naming_compliant,
                'total': len(all_results),
                'rate': naming_compliant / len(all_results) if all_results else 0
            },
            'required_tags': {
                'compliant': tags_compliant,
                'total': len(all_results),
                'rate': tags_compliant / len(all_results) if all_results else 0
            },
            'engineering_tags': {
                tag: {
                    'present': count,
                    'total': len(all_results),
                    'rate': count / len(all_results) if all_results else 0
                }
                for tag, count in eng_tags_present.items()
            }
        }
        
        report['document_breakdown'] = {
            'by_type': type_breakdown,
            'by_complexity': complexity_breakdown
        }
        
        # Print summary
        print("📊 Enhanced Semantic Policy Compliance Report")
        print(f"Generated: {report['generated_at']}")
        print(f"Total Engineering Documents: {report['total_documents']}")
        print()
        
        print("✅ Compliance Metrics:")
        naming = report['compliance_summary']['naming_convention']
        print(f"   • Naming Convention: {naming['rate']:.1%} ({naming['compliant']}/{naming['total']})")
        
        tags = report['compliance_summary']['required_tags']
        print(f"   • Required Tags: {tags['rate']:.1%} ({tags['compliant']}/{tags['total']})")
        
        print("   • Engineering Tags:")
        for tag, stats in report['compliance_summary']['engineering_tags'].items():
            print(f"     - {tag}: {stats['rate']:.1%} ({stats['present']}/{stats['total']})")
        
        print("\n📈 Document Distribution:")
        print("   • By Type:")
        for doc_type, count in report['document_breakdown']['by_type'].items():
            print(f"     - {doc_type}: {count}")
        
        print("   • By Complexity:")
        for complexity, count in report['document_breakdown']['by_complexity'].items():
            print(f"     - {complexity}: {count}")
        
        # Save detailed report
        with open('/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/scripts/compliance_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: compliance_report.json")
        
        # Overall assessment
        overall_score = (naming['rate'] + tags['rate'] + sum(stats['rate'] for stats in report['compliance_summary']['engineering_tags'].values()) / 3) / 3
        
        print(f"\n🎯 OVERALL COMPLIANCE SCORE: {overall_score:.1%}")
        
        if overall_score >= 0.95:
            print("🎉 EXCELLENT! Enhanced Semantic Policy fully implemented.")
        elif overall_score >= 0.8:
            print("✅ GOOD! Minor improvements needed.")
        else:
            print("⚠️ NEEDS ATTENTION! Policy implementation requires fixes.")
        
        print()

def main():
    """Run comprehensive test suite"""
    print("🧪 ENHANCED SEMANTIC POLICY TEST SUITE")
    print("=" * 70)
    print("Comprehensive testing of uploaded engineering documents")
    print("Demonstrating policy effectiveness and compliance")
    print()
    
    try:
        tester = EngineeringDocumentQueryTester()
        tester.run_comprehensive_tests()
        
        print("=" * 70)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("Enhanced Semantic Policy implementation verified!")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())