#!/usr/bin/env python3
"""
Constitutional Compliance Dashboard
Real-time monitoring of system compliance with Unified Constitutional Framework v2.0
"""

from cosmos_db_manager import get_db_manager
from datetime import datetime, timedelta
import json

class ComplianceDashboard:
    """Generate compliance reports and metrics"""
    
    def __init__(self):
        self.db = get_db_manager()
        self.messages_container = self.db.database.get_container_client('system_inbox')
        self.enforcement_container = self.db.database.get_container_client('enforcement')
        self.documents_container = self.db.database.get_container_client('documents')
        self.audit_container = self.db.database.get_container_client('audit')
    
    def generate_executive_summary(self):
        """Generate executive summary of constitutional compliance"""
        
        print("\n" + "="*80)
        print("🏛️ CONSTITUTIONAL COMPLIANCE DASHBOARD")
        print("="*80)
        print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Constitutional Framework: v2.0 (Unified Enforcement Edition)")
        print("="*80)
        
        # Get key metrics
        metrics = self._calculate_metrics()
        
        # Executive Summary
        print("\n📊 EXECUTIVE SUMMARY")
        print("-"*60)
        print(f"Overall Compliance Score: {metrics['overall_compliance']:.1f}%")
        print(f"Active Violations: {metrics['active_violations']}")
        print(f"Messages Requiring Action: {metrics['pending_messages']}")
        print(f"Average Response Time: {metrics['avg_response_time']}")
        print(f"Enforcement Status: {'ACTIVE' if metrics['enforcement_active'] else 'INACTIVE'}")
        
        # Compliance by Category
        print("\n📈 COMPLIANCE BY CATEGORY")
        print("-"*60)
        print(f"Message Schema Compliance: {metrics['schema_compliance']:.1f}%")
        print(f"Evidence Compliance: {metrics['evidence_compliance']:.1f}%")
        print(f"Response Time Compliance: {metrics['response_compliance']:.1f}%")
        print(f"Filing Standards Compliance: {metrics['filing_compliance']:.1f}%")
        
        # Violation Summary
        print("\n⚠️  VIOLATION SUMMARY")
        print("-"*60)
        for vtype, count in metrics['violations_by_type'].items():
            print(f"{vtype}: {count}")
        
        # Agent Compliance Scores
        print("\n👥 AGENT COMPLIANCE SCORES")
        print("-"*60)
        for agent, score in sorted(metrics['agent_scores'].items(), key=lambda x: x[1], reverse=True)[:10]:
            status = "✅" if score >= 90 else "⚠️" if score >= 70 else "❌"
            print(f"{status} {agent}: {score:.1f}%")
        
        # Critical Issues
        if metrics['critical_issues']:
            print("\n🚨 CRITICAL ISSUES REQUIRING IMMEDIATE ACTION")
            print("-"*60)
            for issue in metrics['critical_issues']:
                print(f"❗ {issue}")
        
        return metrics
    
    def _calculate_metrics(self):
        """Calculate all compliance metrics"""
        
        metrics = {
            'overall_compliance': 0,
            'active_violations': 0,
            'pending_messages': 0,
            'avg_response_time': 'N/A',
            'enforcement_active': True,
            'schema_compliance': 0,
            'evidence_compliance': 0,
            'response_compliance': 0,
            'filing_compliance': 0,
            'violations_by_type': {},
            'agent_scores': {},
            'critical_issues': []
        }
        
        # Get active violations
        try:
            violations = list(self.enforcement_container.query_items(
                query="SELECT * FROM c WHERE c.status = 'active'",
                enable_cross_partition_query=True
            ))
            metrics['active_violations'] = len(violations)
            
            # Count by type
            for v in violations:
                vtype = v.get('violation_type', 'unknown')
                metrics['violations_by_type'][vtype] = metrics['violations_by_type'].get(vtype, 0) + 1
            
        except:
            metrics['critical_issues'].append("Cannot access enforcement container")
            metrics['enforcement_active'] = False
        
        # Check message compliance
        try:
            recent_messages = list(self.messages_container.query_items(
                query=f"SELECT * FROM c WHERE c.timestamp >= '{(datetime.now() - timedelta(days=1)).isoformat()}Z'",
                enable_cross_partition_query=True
            ))
            
            # Schema compliance
            schema_valid = sum(1 for m in recent_messages if self._check_schema(m))
            metrics['schema_compliance'] = (schema_valid / len(recent_messages) * 100) if recent_messages else 100
            
            # Evidence compliance
            messages_with_claims = [m for m in recent_messages if self._has_claims(m)]
            evidence_valid = sum(1 for m in messages_with_claims if m.get('evidence'))
            metrics['evidence_compliance'] = (evidence_valid / len(messages_with_claims) * 100) if messages_with_claims else 100
            
            # Response time compliance
            pending = [m for m in recent_messages if m.get('status') == 'pending' and m.get('requires_response')]
            metrics['pending_messages'] = len(pending)
            
            # Check for overdue messages
            overdue = [m for m in pending if self._is_overdue(m)]
            if overdue:
                metrics['critical_issues'].append(f"{len(overdue)} messages overdue for response")
            
        except Exception as e:
            metrics['critical_issues'].append(f"Cannot analyze messages: {e}")
        
        # Calculate agent scores
        try:
            agents = {}
            for v in violations:
                agent = v.get('agent_id', 'UNKNOWN')
                if agent not in agents:
                    agents[agent] = {'violations': 0, 'messages': 0}
                agents[agent]['violations'] += 1
            
            # Count messages per agent
            for m in recent_messages:
                agent = m.get('from', 'UNKNOWN')
                if agent not in agents:
                    agents[agent] = {'violations': 0, 'messages': 0}
                agents[agent]['messages'] += 1
            
            # Calculate scores
            for agent, data in agents.items():
                if data['messages'] > 0:
                    compliance_rate = max(0, 100 - (data['violations'] / data['messages'] * 100))
                    metrics['agent_scores'][agent] = compliance_rate
            
        except:
            pass
        
        # Overall compliance score
        scores = [
            metrics['schema_compliance'],
            metrics['evidence_compliance'],
            metrics['response_compliance'],
            metrics['filing_compliance']
        ]
        metrics['overall_compliance'] = sum(scores) / len(scores)
        
        # Critical thresholds
        if metrics['overall_compliance'] < 70:
            metrics['critical_issues'].append("Overall compliance below 70% threshold")
        
        if metrics['active_violations'] > 50:
            metrics['critical_issues'].append("Excessive active violations (>50)")
        
        return metrics
    
    def _check_schema(self, message):
        """Check if message follows required schema"""
        required = ['id', 'type', 'from', 'to', 'subject', 'content', 'status']
        return all(field in message for field in required)
    
    def _has_claims(self, message):
        """Check if message makes claims requiring evidence"""
        content = str(message.get('content', '')).lower()
        claim_words = ['successfully', 'completed', 'fixed', 'deployed', 'implemented']
        return any(word in content for word in claim_words)
    
    def _is_overdue(self, message):
        """Check if message is overdue for response"""
        try:
            created = datetime.fromisoformat(message['timestamp'].replace('Z', '+00:00'))
            age = datetime.now(created.tzinfo) - created
            return age.total_seconds() > 24 * 3600  # 24 hour limit
        except:
            return False
    
    def generate_violation_report(self):
        """Generate detailed violation report"""
        
        print("\n\n📋 DETAILED VIOLATION REPORT")
        print("="*80)
        
        try:
            # Get all violations from last 7 days
            cutoff = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
            violations = list(self.enforcement_container.query_items(
                query=f"SELECT * FROM c WHERE c.timestamp >= '{cutoff}' ORDER BY c.timestamp DESC",
                enable_cross_partition_query=True
            ))
            
            print(f"Total violations (7 days): {len(violations)}")
            
            # Group by agent
            by_agent = {}
            for v in violations:
                agent = v.get('agent_id', 'UNKNOWN')
                if agent not in by_agent:
                    by_agent[agent] = []
                by_agent[agent].append(v)
            
            # Show worst offenders
            print("\n🚨 TOP VIOLATORS")
            print("-"*60)
            sorted_agents = sorted(by_agent.items(), key=lambda x: len(x[1]), reverse=True)
            
            for agent, agent_violations in sorted_agents[:5]:
                print(f"\n{agent}: {len(agent_violations)} violations")
                
                # Show violation types
                types = {}
                for v in agent_violations:
                    vtype = v.get('violation_type', 'unknown')
                    types[vtype] = types.get(vtype, 0) + 1
                
                for vtype, count in types.items():
                    print(f"  - {vtype}: {count}")
                
                # Current penalty level
                active = [v for v in agent_violations if v.get('status') == 'active']
                if active:
                    penalty_level = max(v.get('penalty_level', 1) for v in active)
                    penalty_names = {1: "WARNING", 2: "RESTRICTION", 3: "SUSPENSION", 4: "TERMINATION"}
                    print(f"  Current penalty level: {penalty_names.get(penalty_level, 'UNKNOWN')}")
            
        except Exception as e:
            print(f"❌ Error generating violation report: {e}")
    
    def check_constitutional_acknowledgments(self):
        """Check which agents have acknowledged the constitution"""
        
        print("\n\n📜 CONSTITUTIONAL ACKNOWLEDGMENT STATUS")
        print("="*80)
        
        try:
            # Get the constitution document
            constitution = self.documents_container.read_item(
                item='DOC-GOV-CONST-002_unified_constitutional_framework_v2',
                partition_key='DOC-GOV-CONST-002'
            )
            
            deadline = constitution.get('acknowledgment_deadline', 'Not set')
            print(f"Acknowledgment deadline: {deadline}")
            
            # In a real system, we'd track acknowledgments
            # For now, we'll check for acknowledgment messages
            query = """
            SELECT * FROM messages 
            WHERE messages.subject LIKE '%constitution%acknowledge%'
            OR messages.content LIKE '%acknowledge%constitution%'
            ORDER BY messages.timestamp DESC
            """
            
            acks = list(self.messages_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            print(f"\nAcknowledgments received: {len(acks)}")
            
            if acks:
                print("\nRecent acknowledgments:")
                for ack in acks[:5]:
                    print(f"  - {ack.get('from', 'UNKNOWN')} at {ack.get('timestamp', 'Unknown time')}")
            
            # Warning for agents who haven't acknowledged
            print("\n⚠️  WARNING: Agents who haven't acknowledged face automatic suspension!")
            
        except Exception as e:
            print(f"❌ Error checking acknowledgments: {e}")

def main():
    """Generate comprehensive compliance dashboard"""
    
    dashboard = ComplianceDashboard()
    
    # Generate executive summary
    metrics = dashboard.generate_executive_summary()
    
    # Generate violation report
    dashboard.generate_violation_report()
    
    # Check constitutional acknowledgments
    dashboard.check_constitutional_acknowledgments()
    
    # Final status
    print("\n\n🏁 DASHBOARD SUMMARY")
    print("="*80)
    
    if metrics['overall_compliance'] >= 90:
        print("✅ System is in GOOD compliance with constitutional requirements")
    elif metrics['overall_compliance'] >= 70:
        print("⚠️  System compliance is ADEQUATE but needs improvement")
    else:
        print("❌ System compliance is POOR - immediate action required")
    
    print(f"\nNext dashboard update: {(datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nFor real-time monitoring, run: python3 automated_violation_detection_service.py")

if __name__ == "__main__":
    main()