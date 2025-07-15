#!/usr/bin/env python3
"""
Email Response Quality Analyzer
Analyzes responses for quality and creates reports in DB for Claude Code review
"""

import os
import sys
from datetime import datetime, timedelta
import json
import re
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cosmos_db_manager import CosmosDBManager

class EmailQualityAnalyzer:
    def __init__(self):
        self.db_manager = CosmosDBManager()
        self.database = self.db_manager.database
        self.responses_container = self.database.get_container_client('email_responses')
        self.reports_container = self.database.get_container_client('quality_reports')
        
        # Quality criteria
        self.quality_criteria = {
            "evidence_format": {
                "weight": 0.3,
                "pattern": r'[a-zA-Z0-9_/.-]+\.(py|md|json|yaml|txt):\d+',
                "description": "filepath:line_number format"
            },
            "completeness": {
                "weight": 0.25,
                "required_fields": ["agent_id", "evidence", "status", "timestamp"],
                "description": "All required fields present"
            },
            "no_mock_data": {
                "weight": 0.2,
                "forbidden_patterns": ["test_", "dummy_", "placeholder", "fake_", "example.com", "lorem ipsum"],
                "description": "No mock or placeholder data"
            },
            "response_time": {
                "weight": 0.15,
                "max_minutes": 60,
                "description": "Responded within deadline"
            },
            "format_compliance": {
                "weight": 0.1,
                "description": "Follows requested JSON format"
            }
        }
    
    def analyze_response(self, response, request):
        """Analyze a single response for quality"""
        
        quality_scores = {}
        issues = []
        
        # 1. Evidence Format Check
        evidence_score = 0
        response_text = json.dumps(response).lower()
        evidence_matches = re.findall(self.quality_criteria["evidence_format"]["pattern"], json.dumps(response))
        
        if evidence_matches:
            evidence_score = min(1.0, len(evidence_matches) * 0.2)  # Up to 5 evidence items
        else:
            issues.append("No evidence in filepath:line format")
        
        quality_scores["evidence_format"] = evidence_score
        
        # 2. Completeness Check
        completeness_score = 0
        required_fields = self.quality_criteria["completeness"]["required_fields"]
        missing_fields = []
        
        for field in required_fields:
            if field not in response or not response[field]:
                missing_fields.append(field)
        
        completeness_score = 1.0 - (len(missing_fields) / len(required_fields))
        if missing_fields:
            issues.append(f"Missing required fields: {missing_fields}")
        
        quality_scores["completeness"] = completeness_score
        
        # 3. Mock Data Check
        mock_score = 1.0
        found_mock = []
        
        for pattern in self.quality_criteria["no_mock_data"]["forbidden_patterns"]:
            if pattern in response_text:
                found_mock.append(pattern)
                mock_score = 0
        
        if found_mock:
            issues.append(f"Mock data detected: {found_mock}")
        
        quality_scores["no_mock_data"] = mock_score
        
        # 4. Response Time Check
        time_score = 1.0
        if request.get("sent_timestamp") and response.get("timestamp"):
            sent_time = datetime.fromisoformat(request["sent_timestamp"].replace('Z', '+00:00'))
            response_time = datetime.fromisoformat(response["timestamp"].replace('Z', '+00:00'))
            minutes_elapsed = (response_time - sent_time).total_seconds() / 60
            
            if minutes_elapsed > self.quality_criteria["response_time"]["max_minutes"]:
                time_score = max(0, 1 - (minutes_elapsed - 60) / 60)  # Gradual decrease after 60 min
                issues.append(f"Late response: {minutes_elapsed:.0f} minutes")
        
        quality_scores["response_time"] = time_score
        
        # 5. Format Compliance
        format_score = 0
        try:
            # Check if response follows expected structure
            if isinstance(response, dict) and "agent_id" in response:
                format_score = 1.0
            else:
                issues.append("Response not in expected format")
        except:
            issues.append("Response format invalid")
        
        quality_scores["format_compliance"] = format_score
        
        # Calculate weighted total
        total_score = sum(
            quality_scores[criterion] * self.quality_criteria[criterion]["weight"]
            for criterion in quality_scores
        )
        
        return {
            "total_score": round(total_score * 100, 1),
            "scores": quality_scores,
            "issues": issues,
            "pass_fail": "PASS" if total_score >= 0.7 else "FAIL"
        }
    
    def generate_quality_report(self, analysis_period_hours=24):
        """Generate comprehensive quality report for review"""
        
        print(f"\n📊 GENERATING QUALITY REPORT FOR LAST {analysis_period_hours} HOURS")
        print("=" * 60)
        
        # Get recent responses
        cutoff_time = (datetime.utcnow() - timedelta(hours=analysis_period_hours)).isoformat() + "Z"
        
        query = f"""
        SELECT * FROM c 
        WHERE c.timestamp > '{cutoff_time}'
        ORDER BY c.timestamp DESC
        """
        
        try:
            responses = list(self.responses_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            print(f"Found {len(responses)} responses to analyze")
            
            # Analyze each response
            agent_scores = {}
            all_issues = []
            failed_responses = []
            
            for response in responses:
                agent_id = response.get("agent_id", "Unknown")
                
                # Mock request for analysis (would get real request in production)
                mock_request = {
                    "sent_timestamp": response.get("request_timestamp", cutoff_time),
                    "template_type": response.get("response_to", "Unknown")
                }
                
                analysis = self.analyze_response(response, mock_request)
                
                if agent_id not in agent_scores:
                    agent_scores[agent_id] = []
                
                agent_scores[agent_id].append(analysis["total_score"])
                
                if analysis["pass_fail"] == "FAIL":
                    failed_responses.append({
                        "agent_id": agent_id,
                        "response_id": response.get("id", "Unknown"),
                        "score": analysis["total_score"],
                        "issues": analysis["issues"]
                    })
                
                all_issues.extend(analysis["issues"])
            
            # Calculate agent averages
            agent_averages = {}
            for agent, scores in agent_scores.items():
                agent_averages[agent] = {
                    "average_score": round(sum(scores) / len(scores), 1),
                    "response_count": len(scores),
                    "failure_count": len([s for s in scores if s < 70])
                }
            
            # Identify patterns
            issue_frequency = {}
            for issue in all_issues:
                issue_frequency[issue] = issue_frequency.get(issue, 0) + 1
            
            top_issues = sorted(issue_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Create report
            report = {
                "id": f"quality_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "report_type": "EMAIL_RESPONSE_QUALITY",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "analysis_period": {
                    "start": cutoff_time,
                    "end": datetime.utcnow().isoformat() + "Z",
                    "hours": analysis_period_hours
                },
                "summary": {
                    "total_responses": len(responses),
                    "average_quality_score": round(sum(sum(scores) for scores in agent_scores.values()) / max(1, sum(len(scores) for scores in agent_scores.values())), 1),
                    "passed": len(responses) - len(failed_responses),
                    "failed": len(failed_responses),
                    "response_rate": f"{len(agent_scores)} agents responded"
                },
                "agent_scores": agent_averages,
                "top_quality_issues": top_issues,
                "failed_responses": failed_responses[:20],  # Top 20 failures
                "recommendations": self.generate_recommendations(agent_averages, top_issues),
                "for_claude_review": True,
                "priority_agents": [
                    agent for agent, data in agent_averages.items() 
                    if data["average_score"] < 70 or data["failure_count"] > 2
                ]
            }
            
            # Save report
            self.reports_container.create_item(report)
            print(f"✅ Quality report created: {report['id']}")
            
            # Display summary
            print("\n📊 QUALITY REPORT SUMMARY")
            print("=" * 40)
            print(f"Total Responses: {report['summary']['total_responses']}")
            print(f"Average Score: {report['summary']['average_quality_score']}/100")
            print(f"Pass/Fail: {report['summary']['passed']}/{report['summary']['failed']}")
            print(f"\nTop Issues:")
            for issue, count in top_issues[:5]:
                print(f"  - {issue}: {count} occurrences")
            print(f"\nAgents Needing Attention: {len(report['priority_agents'])}")
            for agent in report['priority_agents']:
                print(f"  - {agent}: {agent_averages[agent]['average_score']}/100")
            
            return report
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_recommendations(self, agent_averages, top_issues):
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Overall quality recommendations
        avg_score = sum(data["average_score"] for data in agent_averages.values()) / max(1, len(agent_averages))
        
        if avg_score < 70:
            recommendations.append({
                "priority": "HIGH",
                "category": "OVERALL_QUALITY",
                "action": "Implement mandatory quality training for all agents",
                "rationale": f"Average quality score {avg_score:.1f} is below acceptable threshold"
            })
        
        # Evidence format issues
        if any("evidence" in issue for issue, _ in top_issues):
            recommendations.append({
                "priority": "HIGH",
                "category": "EVIDENCE_FORMAT",
                "action": "Reinforce filepath:line_number evidence requirement",
                "rationale": "Evidence format violations are most common issue"
            })
        
        # Response time issues
        if any("late response" in issue.lower() for issue, _ in top_issues):
            recommendations.append({
                "priority": "MEDIUM",
                "category": "RESPONSE_TIME",
                "action": "Review workload distribution and deadline feasibility",
                "rationale": "Multiple agents missing response deadlines"
            })
        
        # Agent-specific recommendations
        for agent, data in agent_averages.items():
            if data["average_score"] < 60:
                recommendations.append({
                    "priority": "CRITICAL",
                    "category": "AGENT_SPECIFIC",
                    "action": f"Immediate intervention required for {agent}",
                    "rationale": f"Consistently low quality score: {data['average_score']}/100"
                })
        
        return recommendations

def main():
    """Run quality analysis"""
    analyzer = EmailQualityAnalyzer()
    
    # Generate report for last 24 hours
    report = analyzer.generate_quality_report(24)
    
    if report:
        print(f"\n✅ Report available for Claude Code review:")
        print(f"   Container: quality_reports")
        print(f"   Report ID: {report['id']}")
        print(f"   Priority agents to review: {len(report['priority_agents'])}")

if __name__ == "__main__":
    main()