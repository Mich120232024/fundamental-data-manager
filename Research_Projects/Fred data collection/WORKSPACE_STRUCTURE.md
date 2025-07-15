# FRED Data Collection - Clean Workspace Structure

## Active Directories

### `/fred_production/` - Production Ready Code
- **core_analysis/** - Our proven FRED analysis from Safe
  - All collection scripts with adaptive rate limiting
  - Complete 31 endpoint documentation
  - Tag relationship analysis
- **azure_deployment/** - Azure specific implementations
  - Delta Lake test notebook
  - Implementation guide

### `/fred_data_local/` - Local Test Data
- Sample data for 9 key indicators
- Observations for testing

### `/fred_metadata_extraction/` - Original Development
- All our development scripts
- Test results and logs
- Can be archived after Azure deployment

### `/archive/` - Historical Files
- Old Azure attempts
- Workspace templates
- Development iterations

## Next Steps
1. Focus on `/fred_production/` for deployment
2. Use Delta Lake notebook in `azure_deployment/`
3. Reference documentation in `core_analysis/`