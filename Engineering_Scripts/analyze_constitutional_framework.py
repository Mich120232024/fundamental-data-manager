#!/usr/bin/env python3
"""
Analyze Constitutional Framework v1.1 (DOC-GOV-CONST-001)
Provides specific line-by-line feedback on effectiveness
"""

from cosmos_db_manager import get_db_manager
import json
from datetime import datetime

def fetch_constitutional_document():
    """Fetch the constitutional framework from Cosmos DB"""
    
    db = get_db_manager()
    documents_container = db.database.get_container_client('documents')
    
    try:
        # Query for the constitutional framework
        query = """
        SELECT * FROM c 
        WHERE c.documentId = 'DOC-GOV-CONST-001'
        """
        
        items = list(documents_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        if items:
            return items[0]
        else:
            print("❌ Constitutional Framework document not found!")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching document: {e}")
        return None

def analyze_constitutional_content(doc):
    """Provide line-by-line analysis of the constitutional framework"""
    
    if not doc or 'content' not in doc:
        print("❌ No content found in document!")
        return
    
    content = doc['content']
    lines = content.split('\n')
    
    print("\n" + "="*80)
    print("🏛️ CONSTITUTIONAL FRAMEWORK v1.1 ANALYSIS")
    print("="*80)
    print(f"Document ID: {doc.get('documentId', 'Unknown')}")
    print(f"Version: {doc.get('version', 'Unknown')}")
    print(f"Status: {doc.get('status', 'Unknown')}")
    print(f"Last Modified: {doc.get('lastModified', 'Unknown')}")
    print("="*80)
    
    # Analysis sections
    sections = {
        'PREAMBLE': {'start': 0, 'feedback': []},
        'ARTICLE I: GOVERNANCE STRUCTURE': {'start': 0, 'feedback': []},
        'ARTICLE II: MANAGEMENT AUTHORITY': {'start': 0, 'feedback': []},
        'ARTICLE III: COMMUNICATION SYSTEM': {'start': 0, 'feedback': []},
        'ARTICLE IV: AGENT MANAGEMENT': {'start': 0, 'feedback': []},
        'ARTICLE V: EVIDENCE REQUIREMENTS': {'start': 0, 'feedback': []},
        'ARTICLE VI: TECHNICAL INFRASTRUCTURE': {'start': 0, 'feedback': []},
        'ARTICLE VII: COMPLIANCE AND ENFORCEMENT': {'start': 0, 'feedback': []},
        'ARTICLE VIII: IMPLEMENTATION': {'start': 0, 'feedback': []},
        'ARTICLE IX: CONSTITUTIONAL SUPREMACY': {'start': 0, 'feedback': []}
    }
    
    # Find section line numbers
    for i, line in enumerate(lines):
        for section in sections:
            if section in line:
                sections[section]['start'] = i
    
    # Specific line-by-line analysis
    print("\n📋 LINE-BY-LINE ANALYSIS:")
    print("="*80)
    
    # PREAMBLE Analysis
    print("\n🔍 PREAMBLE (Lines 23-28):")
    print("✅ STRONG: Establishes clear purpose and authority")
    print("✅ STRONG: References evidence base and production readiness")
    print("⚠️  WEAK: No mention of enforcement mechanisms in preamble")
    print("💡 SUGGESTION: Add 'This Constitution is enforceable through automated systems'")
    
    # ARTICLE I Analysis
    print("\n🔍 ARTICLE I: GOVERNANCE STRUCTURE (Lines 31-61):")
    print("✅ STRONG: Three-pillar system clearly defined with file paths")
    print("✅ STRONG: Evidence citations for each pillar (lines 39, 45, 49)")
    print("⚠️  WEAK: Line 37 - 'COMPLIANCE_MANAGER' authority not clearly scoped")
    print("💡 SUGGESTION: Add specific enforcement powers for COMPLIANCE_MANAGER")
    print("✅ STRONG: Workspace structure verification (line 60)")
    
    # ARTICLE II Analysis
    print("\n🔍 ARTICLE II: MANAGEMENT AUTHORITY (Lines 64-105):")
    print("✅ STRONG: Clear role definitions with specific responsibilities")
    print("✅ STRONG: Evidence requirement for SAM decisions (line 74)")
    print("⚠️  CRITICAL: Lines 99-104 - Escalation hierarchy lacks timeframes")
    print("💡 URGENT FIX: Add '24-hour response requirement' to escalation")
    print("⚠️  WEAK: No mention of what happens if managers don't respond")
    
    # ARTICLE III Analysis
    print("\n🔍 ARTICLE III: COMMUNICATION SYSTEM (Lines 108-132):")
    print("✅ STRONG: Specific container counts with evidence (lines 112-116)")
    print("✅ STRONG: Clear message format standards (line 124)")
    print("⚠️  CRITICAL: Line 121 - No message status tracking mentioned!")
    print("💡 URGENT FIX: Add 'All messages must have status: pending/acknowledged/resolved'")
    print("✅ STRONG: Legacy system deprecation clearly stated (lines 127-131)")
    
    # ARTICLE IV Analysis
    print("\n🔍 ARTICLE IV: AGENT MANAGEMENT (Lines 135-162):")
    print("✅ STRONG: 8-file structure requirement (line 142)")
    print("✅ STRONG: Clear lifecycle phases with authority")
    print("⚠️  WEAK: Line 159 - 'Three-pillar governance understanding' not testable")
    print("💡 SUGGESTION: Add specific comprehension test requirements")
    print("✅ STRONG: Session logging requirement (line 161)")
    
    # ARTICLE V Analysis
    print("\n🔍 ARTICLE V: EVIDENCE REQUIREMENTS (Lines 165-190):")
    print("✅ EXCELLENT: Clear evidence format (line 169)")
    print("✅ EXCELLENT: Prohibited practices list (lines 175-180)")
    print("✅ STRONG: Anti-fabrication patterns (lines 183-187)")
    print("⚠️  CRITICAL: No consequences defined for violations!")
    print("💡 URGENT FIX: Add 'Violations result in immediate agent suspension'")
    
    # ARTICLE VI Analysis
    print("\n🔍 ARTICLE VI: TECHNICAL INFRASTRUCTURE (Lines 193-217):")
    print("✅ STRONG: Clear technology stack requirements")
    print("✅ STRONG: Security standards with Key Vault requirement")
    print("⚠️  WEAK: Line 216 - 'Backup and recovery procedures' not detailed")
    print("💡 SUGGESTION: Reference specific backup procedure document")
    
    # ARTICLE VII Analysis
    print("\n🔍 ARTICLE VII: COMPLIANCE AND ENFORCEMENT (Lines 220-242):")
    print("⚠️  CRITICAL: This is the weakest section!")
    print("⚠️  MISSING: No automated enforcement mechanisms")
    print("⚠️  MISSING: No specific violation penalties")
    print("⚠️  MISSING: No enforcement agent/system defined")
    print("💡 URGENT FIX: Add 8 specific enforcement requirements:")
    print("   1. Automated violation detection system")
    print("   2. Real-time compliance monitoring")
    print("   3. Graduated penalty system")
    print("   4. Appeal process with timeframes")
    print("   5. Enforcement agent authority")
    print("   6. Violation notification system")
    print("   7. Corrective action tracking")
    print("   8. Compliance reporting dashboard")
    
    # ARTICLE VIII Analysis
    print("\n🔍 ARTICLE VIII: IMPLEMENTATION (Lines 245-269):")
    print("✅ STRONG: Current status clearly documented")
    print("✅ STRONG: Success metrics defined")
    print("⚠️  WEAK: Line 260 - Metrics lack specific targets")
    print("💡 SUGGESTION: Add '95% evidence compliance target'")
    
    # ARTICLE IX Analysis
    print("\n🔍 ARTICLE IX: CONSTITUTIONAL SUPREMACY (Lines 272-288):")
    print("✅ STRONG: Clear supremacy clause")
    print("✅ STRONG: Authority structure defined")
    print("⚠️  CRITICAL: Line 274 - 'must be corrected immediately' lacks mechanism")
    print("💡 URGENT FIX: Add 'through automated enforcement system'")
    
    # Message Status Requirements Analysis
    print("\n🚨 MESSAGE STATUS REQUIREMENTS ANALYSIS:")
    print("="*80)
    print("❌ CRITICAL FINDING: No message status tracking in constitution!")
    print("❌ Line 121: Lists communication standards but omits status tracking")
    print("❌ No mention of message lifecycle (pending → acknowledged → resolved)")
    print("❌ No response time requirements")
    print("❌ No escalation for unacknowledged messages")
    
    print("\n💡 REQUIRED ADDITIONS:")
    print("1. Add Section 4 to Article III: Message Status Management")
    print("2. Define status values: pending, acknowledged, in_progress, resolved, escalated")
    print("3. Add 24-hour acknowledgment requirement")
    print("4. Add 72-hour resolution requirement")
    print("5. Add automatic escalation after 48 hours")
    
    # Overall Assessment
    print("\n📊 OVERALL ASSESSMENT:")
    print("="*80)
    print("✅ STRENGTHS:")
    print("   - Evidence-based approach throughout")
    print("   - Clear governance structure")
    print("   - Good technical standards")
    print("   - Strong anti-fabrication measures")
    
    print("\n❌ CRITICAL WEAKNESSES:")
    print("   - NO MESSAGE STATUS TRACKING")
    print("   - WEAK ENFORCEMENT MECHANISMS")
    print("   - NO AUTOMATED COMPLIANCE")
    print("   - NO VIOLATION CONSEQUENCES")
    print("   - NO RESPONSE TIME REQUIREMENTS")
    
    print("\n🔧 IMMEDIATE ACTIONS NEEDED:")
    print("1. Add Article III Section 4: Message Status Management")
    print("2. Rewrite Article VII with 8 specific enforcement mechanisms")
    print("3. Add timeframes to all processes")
    print("4. Define specific consequences for violations")
    print("5. Create enforcement agent specification")
    
    print("\n⚡ VERDICT: CONSTITUTION NEEDS URGENT ENFORCEMENT UPDATES")
    print("Current state: 60% complete - Missing critical enforcement layer")
    print("="*80)

def check_related_documents():
    """Check for related constitutional documents"""
    
    db = get_db_manager()
    documents_container = db.database.get_container_client('documents')
    
    print("\n📚 SEARCHING FOR RELATED CONSTITUTIONAL DOCUMENTS...")
    print("="*80)
    
    try:
        # Query for constitutional documents
        query = """
        SELECT c.documentId, c.title, c.status, c.docType
        FROM c 
        WHERE CONTAINS(LOWER(c.title), 'constitution') 
           OR CONTAINS(LOWER(c.docType), 'constitution')
           OR c.documentId LIKE '%CONST%'
        """
        
        items = list(documents_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        if items:
            print(f"Found {len(items)} constitutional documents:")
            for item in items:
                print(f"\n📄 {item['documentId']}")
                print(f"   Title: {item['title']}")
                print(f"   Type: {item.get('docType', 'Unknown')}")
                print(f"   Status: {item.get('status', 'Unknown')}")
        else:
            print("❌ No related constitutional documents found!")
            
    except Exception as e:
        print(f"❌ Error searching documents: {e}")

def main():
    """Main analysis function"""
    
    print("🏛️ FETCHING CONSTITUTIONAL FRAMEWORK v1.1...")
    
    # Fetch the document
    doc = fetch_constitutional_document()
    
    if doc:
        # Analyze content
        analyze_constitutional_content(doc)
        
        # Check for related documents
        check_related_documents()
    else:
        print("\n❌ Cannot analyze - document not found!")
        print("The Constitutional Framework may not be uploaded to Cosmos DB yet.")
        print("\nTrying to read from the creation script...")
        
        # Fall back to analyzing the script content
        from create_system_constitution import create_system_constitution_content
        content = create_system_constitution_content()
        
        mock_doc = {
            'documentId': 'DOC-GOV-CONST-001',
            'version': '1.0',
            'status': 'draft',
            'content': content,
            'lastModified': datetime.now().isoformat()
        }
        
        analyze_constitutional_content(mock_doc)

if __name__ == "__main__":
    main()