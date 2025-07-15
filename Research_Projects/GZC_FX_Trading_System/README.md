# GZC FX Trading System

## Project Overview
**Ground Zero Capital Foreign Exchange Trading System**

This project contains the backend infrastructure for analyzing and managing FX (Foreign Exchange) trading positions for Ground Zero Capital funds.

## Project Details
- **Created**: July 2, 2025
- **Primary Funds**: GMF (Ground Zero Master Fund) and GCF (Ground Zero Capital Fund)
- **Database**: Azure PostgreSQL (migrated from GZCDB SQL Server)
- **Focus**: FX position calculations, trade analysis, and fund reporting

## Backend Components

### 📊 Position Analysis
- `calculate_fx_positions.py` - Net FX position calculations using GZCDB methodology
- `fund_positions_report.py` - Comprehensive fund position reporting (GMF & GCF)
- `check_fund_ids.py` - Fund ID validation and analysis

### 🔄 Database Migration
- `migrate_gzcdb_to_postgres.py` - Primary migration tool (GZCDB → PostgreSQL)
- `migrate_fx_data_proper.py` - Enhanced FX data migration (15KB, 385 lines)
- `migrate_fx_batch.py` - Batch migration processing
- `migrate_fx_bulk.py` - Bulk data migration utilities
- `migrate_fx_essentials.py` - Essential FX data migration
- `migrate_fx_options_complete.py` - FX options data migration
- `migrate_remaining_fx_trades.py` - Remaining trades migration

### 🔍 Data Validation
- `check_postgres_fx_data.py` - PostgreSQL data integrity verification
- `check_fx_trades_count.py` - Trade count validation
- `explore_gzcdb_structure.py` - Database structure analysis
- `connect_gzcdb_s002.py` - GZCDB connection testing

### 🧹 Maintenance
- `remove_test_trades.py` - Test data cleanup utilities

## Database Architecture
- **Source**: GZCDB (SQL Server on s002.groundzero.local)
- **Target**: Azure PostgreSQL with SSL
- **Authentication**: Azure Key Vault integration
- **Key Tables**: tblFXTrade, tblFXPosition, tblFXOptionTrade, tblCurrency

## Key Features
- **Position Calculations**: Net long/short positions by currency pair
- **Fund Analysis**: GMF vs GCF position comparison
- **Real-time Monitoring**: Active trade tracking
- **P&L Potential**: Framework for profit/loss calculations
- **Risk Management**: Position size categorization

## Technical Stack
- **Language**: Python 3.12
- **Database**: PostgreSQL (Azure)
- **Authentication**: Azure Key Vault
- **Data Processing**: pandas, psycopg2, pyodbc
- **Connectivity**: Azure DefaultAzureCredential

## Usage
This backend supports the GZC trading infrastructure by providing:
1. Accurate FX position calculations
2. Fund performance analysis
3. Risk management data
4. Regulatory reporting capabilities

## Integration
Part of the broader Research & Analytics Services ecosystem, supporting quantitative analysis and financial research operations.

---
*Project Location*: `Research & Analytics Services/Research Workspace/Projects/GZC_FX_Trading_System/`  
*Classification*: Financial Data Processing & Analysis  
*Status*: Active Development 