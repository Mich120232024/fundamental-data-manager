# 🔧 SCRIPTS - Utility Scripts & Automation

This directory contains organized scripts following the "NO SCRIPTS at source" policy.

## Directory Structure

### 🛠️ utilities/
**Purpose**: Common utility scripts for research and migration operations
- `migrate_missing_files.py` - Migrate files with encoding detection  
- `check_total_library_content.py` - Verify complete content integrity
- `migrate_and_verify_5_files.py` - Test migration with small batch
- `check_migration_failures.py` - Analyze and fix migration issues
- `analyze_actual_research_library.py` - Research library content analysis

### 🔄 automation/
**Purpose**: Automated workflow scripts
- Reserved for automated processes and scheduled tasks

### 🧹 maintenance/
**Purpose**: System maintenance and cleanup scripts  
- Reserved for system health, cleanup, and maintenance operations

## Usage Guidelines

### Script Execution:
```bash
# Run from workspace root
python3 SCRIPTS/utilities/migrate_missing_files.py
python3 SCRIPTS/utilities/check_total_library_content.py
```

### Policy Compliance:
- ✅ All scripts organized in SCRIPTS directory
- ✅ NO SCRIPTS at source level
- ✅ Clear categorization by purpose
- ✅ Documented functionality

### Adding New Scripts:
1. Place in appropriate subdirectory based on purpose
2. Document functionality in this README
3. Follow naming conventions (descriptive_action.py)
4. Include header comments with purpose and usage

---
*Last Updated: 2025-06-20*  
*Purpose: Organized script access following workspace policy*