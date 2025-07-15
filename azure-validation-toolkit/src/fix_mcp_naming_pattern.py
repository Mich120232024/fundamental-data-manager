#!/usr/bin/env python3
"""
Fix MCP Tools Naming Pattern - Standardize to mcp-azure-* pattern
Addresses all 36 MCP tools to follow consistent naming convention
"""
import json
from datetime import datetime
from pathlib import Path

def fix_mcp_naming():
    """Apply consistent naming pattern to all MCP tools"""
    print("🔧 FIXING MCP TOOLS NAMING PATTERN")
    print("=" * 60)
    
    # Load the comprehensive database
    tools_file = Path("/Users/mikaeleage/Research & Analytics Services/azure_tools_comprehensive.json")
    with open(tools_file, 'r') as f:
        data = json.load(f)
    
    # Track fixes
    fixes_applied = []
    tools_fixed = 0
    
    # Apply naming fix to all MCP tools
    for tool in data['tools']:
        if tool['tool_type'] == 'mcp':
            old_name = tool['name']
            
            # Apply consistent pattern: mcp-azure-{service}-{operation}
            if old_name.startswith('azmcp-'):
                # Extract the service and operation parts
                parts = old_name.replace('azmcp-', '').split('-')
                
                # Rebuild with proper pattern
                if len(parts) >= 2:
                    service = parts[0]
                    operation = '-'.join(parts[1:])
                    new_name = f"mcp-azure-{service}-{operation}"
                else:
                    # Fallback for unexpected patterns
                    new_name = f"mcp-azure-{old_name.replace('azmcp-', '')}"
            else:
                # Handle any other patterns
                new_name = f"mcp-azure-{old_name}"
            
            print(f"\nFixing: {tool['id']}")
            print(f"  Old name: {old_name}")
            print(f"  New name: {new_name}")
            
            # Apply the fix
            tool['name'] = new_name
            
            # Update validation status
            tool['tested_status'] = 'fixed'
            tool['test_result'] = "Fixed: Standardized naming pattern to mcp-azure-*"
            tool['amendments_made'] = f"Renamed from {old_name} to {new_name}"
            tool['test_timestamp'] = datetime.now().isoformat()
            
            # Track the fix
            fixes_applied.append({
                'tool_id': tool['id'],
                'old_name': old_name,
                'new_name': new_name,
                'timestamp': datetime.now().isoformat()
            })
            
            tools_fixed += 1
    
    # Save the updated database
    backup_file = f"/Users/mikaeleage/Research & Analytics Services/azure_tools_comprehensive_backup_mcp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    with open(tools_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Generate fix report
    fix_report = {
        'timestamp': datetime.now().isoformat(),
        'phase': 'MCP Tools Naming Standardization',
        'total_fixed': tools_fixed,
        'naming_pattern': 'mcp-azure-{service}-{operation}',
        'fixes_applied': fixes_applied,
        'backup_created': backup_file
    }
    
    report_file = "logs/mcp_naming_fix_report.json"
    with open(report_file, 'w') as f:
        json.dump(fix_report, f, indent=2)
    
    print(f"\n✅ MCP NAMING FIX COMPLETE")
    print(f"  Tools fixed: {tools_fixed}/36")
    print(f"  Naming pattern: mcp-azure-{{service}}-{{operation}}")
    print(f"  Database updated: {tools_file}")
    print(f"  Backup created: {backup_file}")
    print(f"  Fix report: {report_file}")
    
    # Show sample of fixed names
    print(f"\n📋 Sample Fixed Names:")
    for fix in fixes_applied[:5]:
        print(f"  {fix['old_name']} → {fix['new_name']}")
    
    return fix_report

if __name__ == "__main__":
    fix_report = fix_mcp_naming()
    print("\n🎯 MCP naming standardization complete!")