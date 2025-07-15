#!/usr/bin/env python3
"""
Azure Tool Validation Monitor
HEAD_OF_ENGINEERING - June 14, 2025

Monitor Azure_Infrastructure_Agent's testing progress on 858 tools
Verify evidence is being created and validate quality
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class AzureToolValidationMonitor:
    """Monitor and validate Azure agent's tool testing progress"""
    
    def __init__(self, tools_json_path: str):
        self.tools_json_path = tools_json_path
        self.load_tools_data()
        
    def load_tools_data(self):
        """Load current tools data"""
        with open(self.tools_json_path, 'r') as f:
            self.data = json.load(f)
        self.tools = {tool['id']: tool for tool in self.data['tools']}
        
    def check_validation_progress(self) -> Dict[str, Any]:
        """Check overall validation progress"""
        stats = {
            "total_tools": len(self.tools),
            "tested": 0,
            "amended": 0, 
            "failed": 0,
            "pending": 0,
            "has_evidence": 0,
            "missing_evidence": 0,
            "cli_progress": {"tested": 0, "total": 0},
            "mcp_progress": {"tested": 0, "total": 0},
            "sdk_progress": {"tested": 0, "total": 0}
        }
        
        for tool_id, tool in self.tools.items():
            tool_type = tool['tool_type']
            
            # Count by type
            if tool_type == "cli":
                stats["cli_progress"]["total"] += 1
            elif tool_type == "mcp":
                stats["mcp_progress"]["total"] += 1
            elif tool_type == "sdk":
                stats["sdk_progress"]["total"] += 1
            
            # Check validation status
            status = tool.get('tested_status', 'pending')
            stats[status] += 1
            
            if status != 'pending':
                if tool_type == "cli":
                    stats["cli_progress"]["tested"] += 1
                elif tool_type == "mcp":
                    stats["mcp_progress"]["tested"] += 1
                elif tool_type == "sdk":
                    stats["sdk_progress"]["tested"] += 1
            
            # Check evidence
            if tool.get('evidence_file') and tool.get('test_result'):
                stats["has_evidence"] += 1
            else:
                stats["missing_evidence"] += 1
        
        return stats
    
    def validate_evidence_quality(self, sample_size: int = 10) -> List[Dict[str, Any]]:
        """Spot check evidence quality for random sample"""
        import random
        
        tested_tools = [tool for tool in self.tools.values() 
                       if tool.get('tested_status') in ['tested', 'amended']]
        
        if len(tested_tools) < sample_size:
            sample_tools = tested_tools
        else:
            sample_tools = random.sample(tested_tools, sample_size)
        
        evidence_checks = []
        
        for tool in sample_tools:
            check = {
                "tool_id": tool['id'],
                "tool_type": tool['tool_type'],
                "tested_status": tool.get('tested_status'),
                "has_test_command": bool(tool.get('test_command')),
                "has_test_result": bool(tool.get('test_result')),
                "has_evidence_file": bool(tool.get('evidence_file')),
                "has_timestamp": bool(tool.get('test_timestamp')),
                "evidence_file_exists": False,
                "quality_score": 0
            }
            
            # Check if evidence file exists
            evidence_path = tool.get('evidence_file')
            if evidence_path:
                full_path = os.path.join(os.path.dirname(self.tools_json_path), evidence_path)
                check["evidence_file_exists"] = os.path.exists(full_path)
            
            # Calculate quality score
            quality_factors = [
                check["has_test_command"],
                check["has_test_result"], 
                check["has_evidence_file"],
                check["has_timestamp"],
                check["evidence_file_exists"]
            ]
            check["quality_score"] = sum(quality_factors) / len(quality_factors)
            
            evidence_checks.append(check)
        
        return evidence_checks
    
    def identify_testing_gaps(self) -> Dict[str, List[str]]:
        """Identify tools that claim to be tested but lack proper evidence"""
        gaps = {
            "missing_test_command": [],
            "missing_test_result": [],
            "missing_evidence_file": [],
            "missing_timestamp": [],
            "evidence_file_not_found": []
        }
        
        for tool_id, tool in self.tools.items():
            status = tool.get('tested_status', 'pending')
            
            if status in ['tested', 'amended']:
                if not tool.get('test_command'):
                    gaps["missing_test_command"].append(tool_id)
                if not tool.get('test_result'):
                    gaps["missing_test_result"].append(tool_id)
                if not tool.get('evidence_file'):
                    gaps["missing_evidence_file"].append(tool_id)
                if not tool.get('test_timestamp'):
                    gaps["missing_timestamp"].append(tool_id)
                
                # Check if evidence file actually exists
                evidence_path = tool.get('evidence_file')
                if evidence_path:
                    full_path = os.path.join(os.path.dirname(self.tools_json_path), evidence_path)
                    if not os.path.exists(full_path):
                        gaps["evidence_file_not_found"].append(tool_id)
        
        return gaps
    
    def generate_progress_report(self) -> str:
        """Generate comprehensive progress report"""
        stats = self.check_validation_progress()
        gaps = self.identify_testing_gaps()
        evidence_quality = self.validate_evidence_quality()
        
        report_lines = [
            "=== AZURE TOOL VALIDATION PROGRESS REPORT ===",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "OVERALL PROGRESS:",
            f"  Total Tools: {stats['total_tools']}",
            f"  Tested: {stats['tested']} ({stats['tested']/stats['total_tools']*100:.1f}%)",
            f"  Amended: {stats['amended']} ({stats['amended']/stats['total_tools']*100:.1f}%)",
            f"  Failed: {stats['failed']} ({stats['failed']/stats['total_tools']*100:.1f}%)",
            f"  Pending: {stats['pending']} ({stats['pending']/stats['total_tools']*100:.1f}%)",
            "",
            "PROGRESS BY TOOL TYPE:",
            f"  CLI Tools: {stats['cli_progress']['tested']}/{stats['cli_progress']['total']} ({stats['cli_progress']['tested']/stats['cli_progress']['total']*100:.1f}%)",
            f"  MCP Tools: {stats['mcp_progress']['tested']}/{stats['mcp_progress']['total']} ({stats['mcp_progress']['tested']/stats['mcp_progress']['total']*100:.1f}%)",
            f"  SDK Tools: {stats['sdk_progress']['tested']}/{stats['sdk_progress']['total']} ({stats['sdk_progress']['tested']/stats['sdk_progress']['total']*100:.1f}%)",
            "",
            "EVIDENCE QUALITY:",
            f"  Tools with Evidence: {stats['has_evidence']}/{stats['total_tools']}",
            f"  Missing Evidence: {stats['missing_evidence']}/{stats['total_tools']}",
            ""
        ]
        
        # Evidence quality sampling
        avg_quality = sum(check["quality_score"] for check in evidence_quality) / len(evidence_quality) if evidence_quality else 0
        report_lines.extend([
            f"EVIDENCE QUALITY SAMPLE ({len(evidence_quality)} tools):",
            f"  Average Quality Score: {avg_quality:.2f}/1.0",
            f"  High Quality (>0.8): {sum(1 for c in evidence_quality if c['quality_score'] > 0.8)}",
            f"  Low Quality (<0.6): {sum(1 for c in evidence_quality if c['quality_score'] < 0.6)}",
            ""
        ])
        
        # Testing gaps
        report_lines.extend([
            "TESTING GAPS IDENTIFIED:",
            f"  Missing Test Commands: {len(gaps['missing_test_command'])}",
            f"  Missing Test Results: {len(gaps['missing_test_result'])}",
            f"  Missing Evidence Files: {len(gaps['missing_evidence_file'])}",
            f"  Missing Timestamps: {len(gaps['missing_timestamp'])}",
            f"  Evidence Files Not Found: {len(gaps['evidence_file_not_found'])}",
            ""
        ])
        
        # Show specific gap examples
        if gaps['missing_test_result']:
            report_lines.extend([
                "EXAMPLES OF TOOLS CLAIMING 'TESTED' WITHOUT RESULTS:",
                *[f"  • {tool_id}" for tool_id in gaps['missing_test_result'][:5]],
                ""
            ])
        
        # Recommendations
        completion_pct = (stats['tested'] + stats['amended']) / stats['total_tools'] * 100
        report_lines.extend([
            "RECOMMENDATIONS:",
            f"  Current Completion: {completion_pct:.1f}%"
        ])
        
        if completion_pct < 25:
            report_lines.append("  • Azure agent is just getting started - monitor progress")
        elif completion_pct < 50:
            report_lines.append("  • Good progress - verify evidence quality")
        elif completion_pct < 90:
            report_lines.append("  • Excellent progress - focus on remaining tools")
        else:
            report_lines.append("  • Near completion - final quality validation")
        
        if gaps['missing_test_result']:
            report_lines.append("  • ⚠️ CRITICAL: Tools marked 'tested' without evidence")
        
        if avg_quality < 0.7:
            report_lines.append("  • ⚠️ Evidence quality below standards - require improvement")
        
        return "\n".join(report_lines)
    
    def save_monitoring_report(self, output_path: str):
        """Save monitoring report to file"""
        report = self.generate_progress_report()
        
        with open(output_path, 'w') as f:
            f.write(report)
        
        print(f"Monitoring report saved to: {output_path}")
        return report

def monitor_azure_validation():
    """Run monitoring check on Azure tool validation"""
    
    tools_path = "/Users/mikaeleage/Research & Analytics Services/azure_tools_comprehensive.json"
    monitor_path = "/Users/mikaeleage/Research & Analytics Services/azure_validation_monitor_report.md"
    
    monitor = AzureToolValidationMonitor(tools_path)
    report = monitor.save_monitoring_report(monitor_path)
    
    print("=== MONITORING AZURE TOOL VALIDATION ===")
    print(report)
    
    # Quick summary for immediate feedback
    stats = monitor.check_validation_progress()
    completion = (stats['tested'] + stats['amended']) / stats['total_tools'] * 100
    
    print(f"\n🎯 QUICK STATUS:")
    print(f"   Progress: {completion:.1f}% complete")
    print(f"   Tested: {stats['tested']}, Amended: {stats['amended']}, Failed: {stats['failed']}")
    print(f"   Evidence Quality: {stats['has_evidence']}/{stats['total_tools']} have evidence")
    
    if completion < 10:
        print("   Status: Azure agent should be starting soon")
    elif completion < 50:
        print("   Status: Good progress, continue monitoring")
    elif completion > 90:
        print("   Status: Near completion, final validation needed")

if __name__ == "__main__":
    monitor_azure_validation()