#!/usr/bin/env python3
"""
IDC Migration Verification System
Verifies the successful migration and performance of the IDC Research Library.
"""

import os
import json
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from azure.cosmos import CosmosClient
from dotenv import load_dotenv
from cosmos_db_manager import store_agent_message

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('IDC_Migration_Verification')


class IDCMigrationVerifier:
    """Verifies IDC migration success and performance"""
    
    def __init__(self):
        """Initialize the verifier"""
        self.endpoint = os.getenv('COSMOS_ENDPOINT')
        self.key = os.getenv('COSMOS_KEY')
        self.database_name = os.getenv('COSMOS_DATABASE', 'research-analytics-db')
        
        if not self.endpoint or not self.key:
            raise ValueError("COSMOS_ENDPOINT and COSMOS_KEY must be set in .env file")
        
        self.client = CosmosClient(self.endpoint, self.key)
        self.database = self.client.get_database_client(self.database_name)
        self.container_name = 'institutional-data-center'
        self.container = self.database.get_container_client(self.container_name)
        
        logger.info("IDC Migration Verifier initialized")
    
    def verify_migration_completion(self) -> Dict[str, Any]:
        """Verify migration completion and data integrity"""
        logger.info("Verifying migration completion...")
        
        verification_results = {
            "schema_v2_documents": 0,
            "total_documents": 0,
            "data_quality_scores": [],
            "partition_keys": set(),
            "document_types": set(),
            "search_optimized": 0,
            "knowledge_base_structured": 0
        }
        
        try:
            # Get all documents and analyze them
            all_docs_query = "SELECT * FROM c"
            all_documents = list(self.container.query_items(
                query=all_docs_query,
                enable_cross_partition_query=True
            ))
            
            verification_results["total_documents"] = len(all_documents)
            
            for doc in all_documents:
                # Check schema v2 compliance
                if doc.get("metadata", {}).get("schemaVersion") == "2.0":
                    verification_results["schema_v2_documents"] += 1
                
                # Collect partition keys and types
                if "partitionKey" in doc:
                    verification_results["partition_keys"].add(doc["partitionKey"])
                if "type" in doc:
                    verification_results["document_types"].add(doc["type"])
                
                # Check data quality score
                quality_score = doc.get("metadata", {}).get("dataQualityScore")
                if quality_score is not None:
                    verification_results["data_quality_scores"].append(quality_score)
                
                # Check search optimization
                if doc.get("searchText"):
                    verification_results["search_optimized"] += 1
                
                # Check knowledge base structure
                if doc.get("knowledgeBase", {}).get("domain"):
                    verification_results["knowledge_base_structured"] += 1
            
            # Convert sets to lists for JSON serialization
            verification_results["partition_keys"] = list(verification_results["partition_keys"])
            verification_results["document_types"] = list(verification_results["document_types"])
            
            # Calculate percentages
            total = verification_results["total_documents"]
            if total > 0:
                verification_results["schema_v2_compliance_rate"] = round(
                    verification_results["schema_v2_documents"] / total * 100, 1
                )
                verification_results["search_optimization_rate"] = round(
                    verification_results["search_optimized"] / total * 100, 1
                )
                verification_results["knowledge_base_rate"] = round(
                    verification_results["knowledge_base_structured"] / total * 100, 1
                )
                verification_results["average_quality_score"] = round(
                    sum(verification_results["data_quality_scores"]) / len(verification_results["data_quality_scores"]), 3
                ) if verification_results["data_quality_scores"] else 0
            
            return verification_results
            
        except Exception as e:
            logger.error(f"Migration verification failed: {str(e)}")
            return {"error": str(e)}
    
    def test_query_performance(self) -> Dict[str, Any]:
        """Test query performance against <50ms target"""
        logger.info("Testing query performance...")
        
        # Get current timestamp for relative queries
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        epoch_now = int(now.timestamp())
        epoch_yesterday = int(yesterday.timestamp())
        
        performance_tests = [
            {
                "name": "Single partition query (research_finding)",
                "query": "SELECT * FROM c WHERE c.partitionKey = @partitionKey",
                "parameters": [{"name": "@partitionKey", "value": "research_finding"}],
                "cross_partition": False
            },
            {
                "name": "Single partition query (engineering_specification)",
                "query": "SELECT * FROM c WHERE c.partitionKey = @partitionKey",
                "parameters": [{"name": "@partitionKey", "value": "engineering_specification"}],
                "cross_partition": False
            },
            {
                "name": "Category filter (cross-partition)",
                "query": "SELECT * FROM c WHERE c.category = @category",
                "parameters": [{"name": "@category", "value": "research"}],
                "cross_partition": True
            },
            {
                "name": "Epoch timestamp range query",
                "query": "SELECT * FROM c WHERE c.epochTimestamp >= @start AND c.epochTimestamp <= @end",
                "parameters": [
                    {"name": "@start", "value": epoch_yesterday},
                    {"name": "@end", "value": epoch_now}
                ],
                "cross_partition": True
            },
            {
                "name": "Search text query",
                "query": "SELECT * FROM c WHERE CONTAINS(c.searchText, @searchTerm)",
                "parameters": [{"name": "@searchTerm", "value": "analysis"}],
                "cross_partition": True
            },
            {
                "name": "Status and type filter",
                "query": "SELECT * FROM c WHERE c.status = @status AND c.type = @type",
                "parameters": [
                    {"name": "@status", "value": "active"},
                    {"name": "@type", "value": "research_finding"}
                ],
                "cross_partition": True
            },
            {
                "name": "Simple count query",
                "query": "SELECT VALUE COUNT(1) FROM c WHERE c.metadata.schemaVersion = @version",
                "parameters": [{"name": "@version", "value": "2.0"}],
                "cross_partition": True
            }
        ]
        
        results = []
        
        for test in performance_tests:
            logger.info(f"Testing: {test['name']}")
            
            # Run the test 3 times and take the average
            times = []
            result_counts = []
            
            for run in range(3):
                try:
                    start_time = time.time()
                    
                    query_results = list(self.container.query_items(
                        query=test["query"],
                        parameters=test["parameters"],
                        enable_cross_partition_query=test["cross_partition"]
                    ))
                    
                    execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                    times.append(execution_time)
                    result_counts.append(len(query_results))
                    
                except Exception as e:
                    logger.error(f"Query failed: {test['name']} - {str(e)}")
                    times.append(999)  # High penalty for failed queries
                    result_counts.append(0)
            
            avg_time = sum(times) / len(times)
            avg_results = sum(result_counts) / len(result_counts)
            
            # Performance rating
            if avg_time < 25:
                performance_rating = "excellent"
            elif avg_time < 50:
                performance_rating = "good"
            elif avg_time < 100:
                performance_rating = "acceptable"
            else:
                performance_rating = "needs_improvement"
            
            result = {
                "test_name": test["name"],
                "avg_execution_time_ms": round(avg_time, 2),
                "min_time_ms": round(min(times), 2),
                "max_time_ms": round(max(times), 2),
                "avg_result_count": round(avg_results, 1),
                "meets_target": avg_time < 50,
                "performance_rating": performance_rating,
                "cross_partition": test["cross_partition"]
            }
            
            results.append(result)
            
            status = "✓" if result["meets_target"] else "✗"
            logger.info(f"{status} {test['name']}: {avg_time:.2f}ms")
        
        # Calculate overall performance metrics
        total_tests = len(results)
        tests_passed = len([r for r in results if r["meets_target"]])
        average_time = sum(r["avg_execution_time_ms"] for r in results) / total_tests
        
        return {
            "timestamp": now.isoformat(),
            "total_tests": total_tests,
            "tests_passed": tests_passed,
            "tests_failed": total_tests - tests_passed,
            "overall_success_rate": round(tests_passed / total_tests * 100, 1),
            "average_query_time_ms": round(average_time, 2),
            "test_results": results
        }
    
    def test_knowledge_base_functionality(self) -> Dict[str, Any]:
        """Test knowledge base specific functionality"""
        logger.info("Testing knowledge base functionality...")
        
        kb_tests = [
            {
                "name": "Knowledge base domain query",
                "query": "SELECT * FROM c WHERE c.knowledgeBase.domain = @domain",
                "parameters": [{"name": "@domain", "value": "research"}]
            },
            {
                "name": "Audience targeting query",
                "query": "SELECT * FROM c WHERE ARRAY_CONTAINS(c.knowledgeBase.audience, @audience)",
                "parameters": [{"name": "@audience", "value": "researchers"}]
            },
            {
                "name": "Complexity filtering",
                "query": "SELECT * FROM c WHERE c.knowledgeBase.complexity = @complexity",
                "parameters": [{"name": "@complexity", "value": "medium"}]
            }
        ]
        
        results = []
        
        for test in kb_tests:
            try:
                start_time = time.time()
                
                query_results = list(self.container.query_items(
                    query=test["query"],
                    parameters=test["parameters"],
                    enable_cross_partition_query=True
                ))
                
                execution_time = (time.time() - start_time) * 1000
                
                results.append({
                    "test_name": test["name"],
                    "execution_time_ms": round(execution_time, 2),
                    "result_count": len(query_results),
                    "success": True
                })
                
                logger.info(f"✓ {test['name']}: {execution_time:.2f}ms ({len(query_results)} results)")
                
            except Exception as e:
                results.append({
                    "test_name": test["name"],
                    "execution_time_ms": 0,
                    "result_count": 0,
                    "success": False,
                    "error": str(e)
                })
                logger.error(f"✗ {test['name']}: {str(e)}")
        
        successful_tests = len([r for r in results if r["success"]])
        
        return {
            "total_tests": len(results),
            "successful_tests": successful_tests,
            "success_rate": round(successful_tests / len(results) * 100, 1),
            "test_results": results
        }
    
    def generate_verification_report(self, migration_results: Dict[str, Any],
                                   performance_results: Dict[str, Any],
                                   kb_results: Dict[str, Any]) -> str:
        """Generate comprehensive verification report"""
        
        report = f"""
IDC Research Library Migration Verification Report
==================================================
Verification completed: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC

MIGRATION COMPLETION VERIFICATION:
----------------------------------
Total documents migrated: {migration_results.get('total_documents', 0)}
Schema v2 compliant documents: {migration_results.get('schema_v2_documents', 0)}
Schema v2 compliance rate: {migration_results.get('schema_v2_compliance_rate', 0)}%
Average data quality score: {migration_results.get('average_quality_score', 0)}

Document Distribution:
- Partition keys: {', '.join(migration_results.get('partition_keys', []))}
- Document types: {', '.join(migration_results.get('document_types', []))}

Optimization Metrics:
- Search optimized documents: {migration_results.get('search_optimized', 0)} ({migration_results.get('search_optimization_rate', 0)}%)
- Knowledge base structured: {migration_results.get('knowledge_base_structured', 0)} ({migration_results.get('knowledge_base_rate', 0)}%)

QUERY PERFORMANCE VERIFICATION:
-------------------------------
Total performance tests: {performance_results.get('total_tests', 0)}
Tests meeting <50ms target: {performance_results.get('tests_passed', 0)}
Tests exceeding target: {performance_results.get('tests_failed', 0)}
Overall success rate: {performance_results.get('overall_success_rate', 0)}%
Average query time: {performance_results.get('average_query_time_ms', 0)}ms

Performance Test Details:
"""
        
        for test in performance_results.get('test_results', []):
            status = "✓" if test['meets_target'] else "✗"
            report += f"  {status} {test['test_name']}: {test['avg_execution_time_ms']}ms ({test['performance_rating']})\n"
        
        report += f"""

KNOWLEDGE BASE FUNCTIONALITY:
------------------------------
Total KB tests: {kb_results.get('total_tests', 0)}
Successful tests: {kb_results.get('successful_tests', 0)}
KB functionality success rate: {kb_results.get('success_rate', 0)}%

Knowledge Base Test Details:
"""
        
        for test in kb_results.get('test_results', []):
            status = "✓" if test['success'] else "✗"
            if test['success']:
                report += f"  {status} {test['test_name']}: {test['execution_time_ms']}ms ({test['result_count']} results)\n"
            else:
                report += f"  {status} {test['test_name']}: Failed - {test.get('error', 'Unknown error')}\n"
        
        # Overall assessment
        overall_success = (
            migration_results.get('schema_v2_compliance_rate', 0) >= 90 and
            performance_results.get('overall_success_rate', 0) >= 80 and
            kb_results.get('success_rate', 0) >= 90
        )
        
        report += f"""

OVERALL MIGRATION ASSESSMENT:
------------------------------
Migration Status: {'SUCCESS' if overall_success else 'NEEDS ATTENTION'}
Schema v2 Implementation: {'COMPLETE' if migration_results.get('schema_v2_compliance_rate', 0) >= 90 else 'INCOMPLETE'}
Performance Target: {'MET' if performance_results.get('overall_success_rate', 0) >= 80 else 'NOT MET'}
Knowledge Base: {'OPERATIONAL' if kb_results.get('success_rate', 0) >= 90 else 'ISSUES DETECTED'}

RECOMMENDATIONS:
----------------
"""
        
        if performance_results.get('overall_success_rate', 0) < 80:
            report += "⚠ Performance optimization required - consider adding composite indexes\n"
        
        if migration_results.get('search_optimization_rate', 0) < 95:
            report += "⚠ Complete search text optimization for all documents\n"
        
        if kb_results.get('success_rate', 0) < 90:
            report += "⚠ Knowledge base functionality needs attention\n"
        
        if overall_success:
            report += "✓ Migration completed successfully - IDC Research Library is ready for production use\n"
        
        report += f"""

NEXT STEPS:
-----------
1. {'✓' if overall_success else '⚠'} Begin production data migration
2. Configure access policies for research team
3. Set up continuous performance monitoring
4. Schedule knowledge base training sessions
5. Implement semantic search capabilities

The IDC Research Library migration verification is complete.
"""
        
        return report


def main():
    """Main execution function"""
    print("🔍 IDC Migration Verification System")
    print("=" * 50)
    
    try:
        # Initialize verifier
        verifier = IDCMigrationVerifier()
        
        # Step 1: Verify migration completion
        print("\n1. Verifying migration completion...")
        migration_results = verifier.verify_migration_completion()
        if "error" not in migration_results:
            print(f"   ✓ {migration_results['schema_v2_documents']}/{migration_results['total_documents']} documents migrated with schema v2")
        else:
            print(f"   ✗ Migration verification failed: {migration_results['error']}")
        
        # Step 2: Test query performance
        print("\n2. Testing query performance...")
        performance_results = verifier.test_query_performance()
        print(f"   ✓ {performance_results['tests_passed']}/{performance_results['total_tests']} queries meet <50ms target")
        print(f"   ✓ Average query time: {performance_results['average_query_time_ms']}ms")
        
        # Step 3: Test knowledge base functionality
        print("\n3. Testing knowledge base functionality...")
        kb_results = verifier.test_knowledge_base_functionality()
        print(f"   ✓ {kb_results['successful_tests']}/{kb_results['total_tests']} KB tests passed")
        
        # Step 4: Generate verification report
        print("\n4. Generating verification report...")
        report = verifier.generate_verification_report(
            migration_results, performance_results, kb_results
        )
        
        # Save report
        report_filename = f"idc_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"   ✓ Report saved: {report_filename}")
        
        # Step 5: Send completion notification
        print("\n5. Sending verification summary...")
        
        overall_success = (
            migration_results.get('schema_v2_compliance_rate', 0) >= 90 and
            performance_results.get('overall_success_rate', 0) >= 80 and
            kb_results.get('success_rate', 0) >= 90
        )
        
        summary_content = f"""
IDC Research Library Migration Verification Complete

VERIFICATION SUMMARY:
- Migration Status: {'SUCCESS' if overall_success else 'NEEDS ATTENTION'}
- Documents Migrated: {migration_results.get('schema_v2_documents', 0)} with schema v2
- Performance Success Rate: {performance_results.get('overall_success_rate', 0)}%
- Average Query Time: {performance_results.get('average_query_time_ms', 0)}ms
- Knowledge Base Tests: {kb_results.get('success_rate', 0)}% passed

SCHEMA V2 FEATURES VERIFIED:
✓ Flattened document structure: {migration_results.get('schema_v2_compliance_rate', 0)}% compliance
✓ Optimized partition keys: {len(migration_results.get('partition_keys', []))} unique partitions
✓ Search text optimization: {migration_results.get('search_optimization_rate', 0)}% coverage
✓ Knowledge base structure: {migration_results.get('knowledge_base_rate', 0)}% implementation
✓ Query performance: {performance_results.get('tests_passed', 0)}/{performance_results.get('total_tests', 0)} tests meet <50ms target

The IDC Research Library is {'ready for production use' if overall_success else 'requires optimization before production deployment'}.

Detailed verification report: {report_filename}
"""
        
        try:
            message_result = store_agent_message(
                from_agent="HEAD_OF_ENGINEERING",
                to_agent="HEAD_OF_RESEARCH",
                message_type="VERIFICATION_COMPLETE",
                subject="IDC Migration Verification Complete - Production Ready" if overall_success else "IDC Migration Verification - Optimization Required",
                content=summary_content,
                priority="high",
                requires_response=False
            )
            print(f"   ✓ Summary sent: {message_result['id']}")
        except Exception as e:
            print(f"   ⚠ Failed to send summary: {str(e)}")
        
        # Display final summary
        print("\n" + "=" * 50)
        print("VERIFICATION COMPLETE")
        print("=" * 50)
        status_icon = "✅" if overall_success else "⚠️"
        print(f"{status_icon} Migration Status: {'SUCCESS' if overall_success else 'NEEDS ATTENTION'}")
        print(f"✓ Schema v2 Compliance: {migration_results.get('schema_v2_compliance_rate', 0)}%")
        print(f"✓ Performance Success: {performance_results.get('overall_success_rate', 0)}%")
        print(f"✓ Knowledge Base: {kb_results.get('success_rate', 0)}% functional")
        print(f"✓ Average Query Time: {performance_results.get('average_query_time_ms', 0)}ms")
        
        if overall_success:
            print("\n🎉 The IDC Research Library is ready for production use!")
        else:
            print("\n⚠️  Optimization required before production deployment.")
        
        return 0 if overall_success else 1
        
    except Exception as e:
        print(f"\n❌ Verification failed: {str(e)}")
        logger.error(f"Verification failed: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())