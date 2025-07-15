# Enhanced Semantic Policy Implementation Guide

## Quick Start

### 1. Naming Your Assets
Follow the pattern: `{type}-{category}-{identifier}_{name}`

Examples:
- `report-financial-q4-2024_earnings_summary`
- `dataset-customer-2024-01_purchase_history`
- `model-ml-v2.3_fraud_detection`

### 2. Required Tags (All Teams)
Every asset MUST have these tags:
- **type**: What kind of asset (report, dataset, model, etc.)
- **category**: Business area (financial, customer, operational, etc.)
- **status**: Current state (draft, active, archived)
- **owner**: Who's responsible (team or individual)
- **audience**: Who it's for (executive, analyst, public)

### 3. Team-Specific Optional Tags

#### Engineering Team
- **complexity**: low, medium, high
- **dependencies**: List of dependent systems/assets
- **test_coverage**: Percentage of test coverage

#### Governance Team  
- **compliance_level**: Level 1, Level 2, Level 3
- **evidence_required**: yes/no
- **audit_frequency**: monthly, quarterly, annually

#### Research Team
- **methodology**: experimental, observational, analytical
- **confidence_level**: high, medium, low
- **peer_reviewed**: yes/no

#### Business Team
- **roi_impact**: high, medium, low
- **stakeholders**: List of key stakeholders
- **market_segment**: Target market segment

#### Executive Team
- **strategic_priority**: P1, P2, P3
- **decision_impact**: critical, important, informational
- **board_visibility**: yes/no

#### Digital Labor Team
- **skill_level**: junior, intermediate, senior, expert
- **utilization_rate**: Percentage utilization
- **performance_tier**: tier1, tier2, tier3

## Validation Checklist
- [ ] Asset name follows the pattern
- [ ] All components are lowercase
- [ ] Hyphens used within components
- [ ] Underscores used between components
- [ ] All required tags are present
- [ ] Tag values are non-empty
- [ ] Team-specific tags applied where relevant
