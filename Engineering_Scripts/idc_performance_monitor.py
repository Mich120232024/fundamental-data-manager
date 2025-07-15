#!/usr/bin/env python3
"""
IDC Performance Monitoring System
Comprehensive monitoring for the institutional-data-center container
to ensure <50ms query performance target and optimal system health.
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
logger = logging.getLogger('IDC_Performance_Monitor')


class IDCPerformanceMonitor:
    """Monitors IDC container performance and system health"""
    
    def __init__(self):
        """Initialize the performance monitor"""
        self.endpoint = os.getenv('COSMOS_ENDPOINT')
        self.key = os.getenv('COSMOS_KEY')
        self.database_name = os.getenv('COSMOS_DATABASE', 'research-analytics-db')
        
        if not self.endpoint or not self.key:
            raise ValueError("COSMOS_ENDPOINT and COSMOS_KEY must be set in .env file")
        
        self.client = CosmosClient(self.endpoint, self.key)
        self.database = self.client.get_database_client(self.database_name)
        self.container_name = 'institutional-data-center'
        self.container = self.database.get_container_client(self.container_name)
        
        logger.info("IDC Performance Monitor initialized")
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run comprehensive performance tests"""
        logger.info("Starting performance tests...")
        
        # Get current timestamp for relative queries
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        epoch_now = int(now.timestamp())
        epoch_yesterday = int(yesterday.timestamp())
        
        performance_tests = [
            {
                "name": "Query by category (research)",
                "query": "SELECT * FROM c WHERE c.category = @category",
                "parameters": [{"name": "@category", "value": "research"}],
                "partition_optimized": False,
                "expected_performance": "good"
            },
            {
                "name": "Query by partition key (research_finding)",
                "query": "SELECT * FROM c WHERE c.partitionKey = @partitionKey",
                "parameters": [{"name": "@partitionKey", "value": "research_finding"}],
                "partition_optimized": True,
                "expected_performance": "excellent"
            },
            {
                "name": "Query by partition key (engineering_specification)",
                "query": "SELECT * FROM c WHERE c.partitionKey = @partitionKey",
                "parameters": [{"name": "@partitionKey", "value": "engineering_specification"}],
                "partition_optimized": True,
                "expected_performance": "excellent"
            },
            {
                "name": "Range query by epoch timestamp",
                "query": "SELECT * FROM c WHERE c.epochTimestamp >= @start AND c.epochTimestamp <= @end",
                "parameters": [
                    {"name": "@start", "value": epoch_yesterday},
                    {"name": "@end", "value": epoch_now}
                ],
                "partition_optimized": False,
                "expected_performance": "good"
            },
            {
                "name": "Full-text search (contains cosmos)",
                "query": "SELECT * FROM c WHERE CONTAINS(c.searchText, @searchTerm)",
                "parameters": [{"name": "@searchTerm", "value": "cosmos"}],
                "partition_optimized": False,
                "expected_performance": "good"
            },
            {
                "name": "Knowledge base domain query",
                "query": "SELECT * FROM c WHERE c.knowledgeBase.domain = @domain",
                "parameters": [{"name": "@domain", "value": "research"}],
                "partition_optimized": False,
                "expected_performance": "good"
            },
            {
                "name": "Multi-field composite query",
                "query": "SELECT * FROM c WHERE c.category = @category AND c.type = @type ORDER BY c.epochTimestamp DESC",
                "parameters": [
                    {"name": "@category", "value": "research"},
                    {"name": "@type", "value": "research_finding"}
                ],
                "partition_optimized": False,
                "expected_performance": "good"
            },
            {
                "name": "Count documents by schema version",
                "query": "SELECT VALUE COUNT(1) FROM c WHERE c.metadata.schemaVersion = @version",
                "parameters": [{"name": "@version", "value": "2.0"}],
                "partition_optimized": False,
                "expected_performance": "good"
            }
        ]
        
        results = []
        
        for test in performance_tests:
            logger.info(f"Running test: {test['name']}")
            
            # Warm-up query
            list(self.container.query_items(
                query=test["query"],
                parameters=test["parameters"],
                enable_cross_partition_query=not test["partition_optimized"]
            ))
            
            # Actual performance test (run 3 times and take average)
            times = []
            for run in range(3):
                start_time = time.time()
                
                query_results = list(self.container.query_items(
                    query=test["query"],
                    parameters=test["parameters"],
                    enable_cross_partition_query=not test["partition_optimized"]
                ))
                
                execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                times.append(execution_time)
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
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
                "min_time_ms": round(min_time, 2),
                "max_time_ms": round(max_time, 2),
                "result_count": len(query_results),
                "meets_target": avg_time < 50,
                "performance_rating": performance_rating,
                "expected_performance": test["expected_performance"],
                "partition_optimized": test["partition_optimized"]
            }
            
            results.append(result)
            
            status = "✓" if result["meets_target"] else "✗"
            logger.info(f"{status} {test['name']}: {avg_time:.2f}ms ({len(query_results)} results)")
        
        return {
            "timestamp": now.isoformat(),
            "total_tests": len(results),
            "tests_passed": len([r for r in results if r["meets_target"]]),
            "tests_failed": len([r for r in results if not r["meets_target"]]),
            "overall_success_rate": round(len([r for r in results if r["meets_target"]]) / len(results) * 100, 1),
            "test_results": results
        }
    
    def analyze_data_distribution(self) -> Dict[str, Any]:
        """Analyze data distribution across partitions"""
        logger.info("Analyzing data distribution...")
        
        try:
            # Get document counts by partition key
            partition_query = """
                SELECT c.partitionKey, COUNT(1) as documentCount
                FROM c 
                WHERE c.metadata.schemaVersion = '2.0'
                GROUP BY c.partitionKey
            """
            
            partition_results = list(self.container.query_items(
                query=partition_query,
                enable_cross_partition_query=True
            ))
            
            # Get document counts by category
            category_query = """
                SELECT c.category, COUNT(1) as documentCount
                FROM c 
                WHERE c.metadata.schemaVersion = '2.0'
                GROUP BY c.category
            """
            
            category_results = list(self.container.query_items(
                query=category_query,
                enable_cross_partition_query=True
            ))
            
            # Get document counts by type
            type_query = """
                SELECT c.type, COUNT(1) as documentCount
                FROM c 
                WHERE c.metadata.schemaVersion = '2.0'
                GROUP BY c.type
            """
            
            type_results = list(self.container.query_items(
                query=type_query,
                enable_cross_partition_query=True
            ))
            
            # Calculate total documents
            total_query = "SELECT VALUE COUNT(1) FROM c WHERE c.metadata.schemaVersion = '2.0'"
            total_docs = list(self.container.query_items(
                query=total_query,
                enable_cross_partition_query=True
            ))[0]
            
            return {
                "total_documents": total_docs,
                "partition_distribution": partition_results,
                "category_distribution": category_results,
                "type_distribution": type_results,
                "analysis": {
                    "partitions_count": len(partition_results),
                    "categories_count": len(category_results),
                    "types_count": len(type_results),
                    "well_distributed": len(partition_results) > 1,  # Multiple partitions indicate good distribution
                }
            }
            
        except Exception as e:
            logger.error(f"Data distribution analysis failed: {str(e)}")
            return {"error": str(e)}
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        logger.info("Checking system health...")
        
        health_checks = []
        
        try:
            # Test 1: Basic connectivity
            start_time = time.time()
            container_props = self.container.read()
            connectivity_time = (time.time() - start_time) * 1000
            
            health_checks.append({
                "check": "Container Connectivity",
                "status": "healthy",
                "response_time_ms": round(connectivity_time, 2),
                "details": f"Container accessible in {connectivity_time:.2f}ms"
            })
            
            # Test 2: Schema v2 compliance
            schema_query = "SELECT VALUE COUNT(1) FROM c WHERE c.metadata.schemaVersion = '2.0'"
            schema_compliant_count = list(self.container.query_items(
                query=schema_query,
                enable_cross_partition_query=True
            ))[0]
            
            total_query = "SELECT VALUE COUNT(1) FROM c"
            total_count = list(self.container.query_items(
                query=total_query,
                enable_cross_partition_query=True
            ))[0]
            
            schema_compliance_rate = (schema_compliant_count / total_count * 100) if total_count > 0 else 0
            
            health_checks.append({
                "check": "Schema v2 Compliance",
                "status": "healthy" if schema_compliance_rate > 80 else "warning",
                "compliance_rate": round(schema_compliance_rate, 1),
                "details": f"{schema_compliant_count}/{total_count} documents use schema v2"
            })
            
            # Test 3: Search optimization
            search_query = "SELECT VALUE COUNT(1) FROM c WHERE IS_DEFINED(c.searchText) AND LENGTH(c.searchText) > 0"
            search_optimized_count = list(self.container.query_items(
                query=search_query,
                enable_cross_partition_query=True
            ))[0]
            
            search_optimization_rate = (search_optimized_count / total_count * 100) if total_count > 0 else 0
            
            health_checks.append({
                "check": "Search Optimization",
                "status": "healthy" if search_optimization_rate > 90 else "warning",
                "optimization_rate": round(search_optimization_rate, 1),
                "details": f"{search_optimized_count}/{total_count} documents have search text"
            })
            
            # Test 4: Knowledge base structure
            kb_query = "SELECT VALUE COUNT(1) FROM c WHERE IS_DEFINED(c.knowledgeBase) AND IS_DEFINED(c.knowledgeBase.domain)"
            kb_count = list(self.container.query_items(
                query=kb_query,
                enable_cross_partition_query=True
            ))[0]
            
            kb_coverage_rate = (kb_count / total_count * 100) if total_count > 0 else 0
            
            health_checks.append({
                "check": "Knowledge Base Structure",
                "status": "healthy" if kb_coverage_rate > 90 else "warning",
                "coverage_rate": round(kb_coverage_rate, 1),
                "details": f"{kb_count}/{total_count} documents have knowledge base structure"
            })
            
            # Overall health status
            healthy_checks = len([c for c in health_checks if c["status"] == "healthy"])
            overall_status = "healthy" if healthy_checks == len(health_checks) else "warning"
            
            return {
                "overall_status": overall_status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "checks_passed": healthy_checks,
                "total_checks": len(health_checks),
                "health_checks": health_checks
            }
            
        except Exception as e:
            logger.error(f"System health check failed: {str(e)}")
            return {
                "overall_status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def generate_monitoring_report(self, performance_results: Dict[str, Any], 
                                  distribution_analysis: Dict[str, Any], 
                                  health_check: Dict[str, Any]) -> str:
        """Generate comprehensive monitoring report"""
        
        report = f"""
IDC Performance Monitoring Report
=================================
Report generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC

PERFORMANCE TEST RESULTS:
--------------------------
Total tests: {performance_results['total_tests']}
Tests passed: {performance_results['tests_passed']}
Tests failed: {performance_results['tests_failed']}
Overall success rate: {performance_results['overall_success_rate']}%

Query Performance Details:
"""
        
        for test in performance_results['test_results']:
            status = "✓" if test['meets_target'] else "✗"
            report += f"  {status} {test['test_name']}: {test['avg_execution_time_ms']}ms ({test['result_count']} results)\n"
            report += f"    Range: {test['min_time_ms']}ms - {test['max_time_ms']}ms, Rating: {test['performance_rating']}\n"
        
        report += f"""

DATA DISTRIBUTION ANALYSIS:
----------------------------
Total documents: {distribution_analysis.get('total_documents', 'N/A')}
Partition count: {distribution_analysis.get('analysis', {}).get('partitions_count', 'N/A')}
Well distributed: {distribution_analysis.get('analysis', {}).get('well_distributed', False)}

Partition Distribution:
"""
        
        for partition in distribution_analysis.get('partition_distribution', []):
            report += f"  - {partition.get('partitionKey', 'N/A')}: {partition.get('documentCount', 0)} documents\n"
        
        report += "\nCategory Distribution:\n"
        for category in distribution_analysis.get('category_distribution', []):
            report += f"  - {category.get('category', 'N/A')}: {category.get('documentCount', 0)} documents\n"
        
        report += f"""

SYSTEM HEALTH CHECK:
--------------------
Overall status: {health_check['overall_status'].upper()}
Checks passed: {health_check.get('checks_passed', 0)}/{health_check.get('total_checks', 0)}

Health Check Details:
"""
        
        for check in health_check.get('health_checks', []):
            status_icon = "✓" if check['status'] == "healthy" else "⚠"
            report += f"  {status_icon} {check['check']}: {check['status'].upper()}\n"
            report += f"    {check['details']}\n"
        
        # Performance recommendations
        failed_tests = [t for t in performance_results['test_results'] if not t['meets_target']]
        if failed_tests:
            report += "\nPERFORMANCE RECOMMENDATIONS:\n"
            report += "----------------------------\n"
            for test in failed_tests:
                if test['avg_execution_time_ms'] > 100:
                    report += f"  ⚠ {test['test_name']}: Consider adding composite index\n"
                elif test['avg_execution_time_ms'] > 50:
                    report += f"  ⚠ {test['test_name']}: Monitor RU consumption and optimize query\n"
        
        report += f"""

MONITORING SUMMARY:
-------------------
✓ Performance monitoring active
✓ Data distribution tracking enabled
✓ System health verification operational
✓ Query optimization recommendations provided

Target: All queries < 50ms
Current: {performance_results['tests_passed']}/{performance_results['total_tests']} queries meet target

The IDC container is {'performing optimally' if performance_results['overall_success_rate'] >= 90 else 'requires attention'}.
"""
        
        return report


def main():
    """Main execution function"""
    print("🔍 IDC Performance Monitoring System")
    print("=" * 50)
    
    try:
        # Initialize monitor
        monitor = IDCPerformanceMonitor()
        
        # Step 1: Run performance tests
        print("\n1. Running performance tests...")
        performance_results = monitor.run_performance_tests()
        print(f"   ✓ {performance_results['tests_passed']}/{performance_results['total_tests']} tests passed")
        
        # Step 2: Analyze data distribution
        print("\n2. Analyzing data distribution...")
        distribution_analysis = monitor.analyze_data_distribution()
        print(f"   ✓ {distribution_analysis.get('total_documents', 0)} documents analyzed")
        
        # Step 3: Check system health
        print("\n3. Checking system health...")
        health_check = monitor.check_system_health()
        print(f"   ✓ {health_check.get('checks_passed', 0)}/{health_check.get('total_checks', 0)} health checks passed")
        
        # Step 4: Generate report
        print("\n4. Generating monitoring report...")
        report = monitor.generate_monitoring_report(
            performance_results, distribution_analysis, health_check
        )
        
        # Save report
        report_filename = f"idc_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"   ✓ Report saved: {report_filename}")
        
        # Step 5: Send summary if needed
        if performance_results['overall_success_rate'] < 90 or health_check['overall_status'] != 'healthy':
            print("\n5. Sending performance alert...")
            alert_content = f"""
IDC Performance Alert - Attention Required

PERFORMANCE SUMMARY:
- Query success rate: {performance_results['overall_success_rate']}%
- System health: {health_check['overall_status']}
- Failed tests: {performance_results['tests_failed']}

IMMEDIATE ACTIONS REQUIRED:
{chr(10).join(f'- {test["test_name"]}: {test["avg_execution_time_ms"]}ms (exceeds 50ms target)' 
              for test in performance_results['test_results'] if not test['meets_target'])}

Detailed report: {report_filename}
"""
            
            try:
                alert_result = store_agent_message(
                    from_agent="HEAD_OF_ENGINEERING",
                    to_agent="HEAD_OF_RESEARCH",
                    message_type="PERFORMANCE_ALERT",
                    subject="IDC Performance Alert - Optimization Required",
                    content=alert_content,
                    priority="high",
                    requires_response=True
                )
                print(f"   ✓ Alert sent: {alert_result['id']}")
            except Exception as e:
                print(f"   ⚠ Failed to send alert: {str(e)}")
        else:
            print("\n5. All systems optimal - no alerts needed")
        
        # Display summary
        print("\n" + "=" * 50)
        print("MONITORING SUMMARY")
        print("=" * 50)
        print(f"✓ Performance Tests: {performance_results['tests_passed']}/{performance_results['total_tests']} passed")
        print(f"✓ Average Query Time: {sum(t['avg_execution_time_ms'] for t in performance_results['test_results']) / len(performance_results['test_results']):.2f}ms")
        print(f"✓ System Health: {health_check['overall_status'].upper()}")
        print(f"✓ Documents Monitored: {distribution_analysis.get('total_documents', 0)}")
        
        overall_status = "OPTIMAL" if (performance_results['overall_success_rate'] >= 90 and 
                                     health_check['overall_status'] == 'healthy') else "NEEDS ATTENTION"
        print(f"\nOverall IDC Status: {overall_status}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Monitoring failed: {str(e)}")
        logger.error(f"Monitoring failed: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())