#!/usr/bin/env python3
"""
FRED Failed Series Diagnostic Tool
Author: Research Quantitative Analyst
Date: 2025-06-25
Purpose: Investigate failed series and find correct alternatives
"""

import os
import sys
from dotenv import load_dotenv
from fredapi import Fred
import pandas as pd
import time

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# Initialize FRED client
FRED_API_KEY = os.getenv('FRED_API_KEY')
if not FRED_API_KEY:
    print("❌ ERROR: FRED_API_KEY not found")
    sys.exit(1)

fred = Fred(api_key=FRED_API_KEY)

# List of failed series from previous run
FAILED_SERIES = {
    'GDP': ['NYGDPMKTPCDWLD', 'DNDGRC1', 'DSERGC1', 'GDPC1CTM', 'NGDPPOT'],
    'EMPLOYMENT': ['JTSQUL', 'JTSJOL'],
    'INFLATION': ['TRIMAFEM158SFRBCLE', 'CUSR0000SA0', 'BPCCRO1Q156NBEA'],
    'RATES': ['DFII10', 'GS1M', 'GS3M', 'GS6M', 'GS1', 'GS2', 'GS3', 'GS5', 'GS7', 'GS20'],
    'HOUSING': ['PERMITS', 'MORTGAGE15US', 'MSACSR', 'HSN1F', 'COMPUTSA', 'COMREPUSQ159N', 
                'NHSUSSPT', 'EVACANTUSQ176N', 'RHVRUSQ156N', 'EXHOSLUSM495S'],
    'MANUFACTURING': ['CAPUTLG2211S', 'MCUMFN', 'IPFINAL', 'IPCONGD', 'NAPMEI', 'NAPMNOI', 
                      'NAPMSDI', 'NAPMII', 'DGORDER', 'NEWORDER', 'BUSINV', 'ISRATIO', 'TOTALSA'],
    'CONSUMER': ['A229RX0', 'TOTALSL', 'CONSUMER', 'DTCOLNVHFNM', 'TDSP', 'REVOLSL'],
    'FINANCIAL': ['DEXJPUS', 'DEXCAUS', 'DEXUSUK', 'DEXCHUS', 'DEXMXUS', 'DTWEXBGS', 
                  'BAMLC0A0CM', 'TEDRATE', 'GOLDPMGBD228NLBM', 'DHHNGSP', 'DCOILBRENTEU', 'GASREGW'],
    'MONEY_CREDIT': ['M1SL', 'REALLN', 'NONREVSL', 'CCLACBW027SBOG', 'DRISCFLM', 'DPSACBW027SBOG', 
                     'H8B1001NCBCMG', 'TOTBKCR', 'USGSEC', 'OTHSEC', 'INVEST'],
    'TRADE': ['NETEXP', 'EXPGS', 'IMPGS', 'BOPGSTB', 'IEABC', 'XTEXVA01USM664S', 'XTIMVA01USM664S', 
              'USATRADEBALGDPB6PT', 'CURCIR', 'EXUSEU', 'EXJPUS', 'EXCAUS', 'EXMXUS', 'EXCHUS', 'EXUSUK'],
    'GOVERNMENT': ['FYFSD', 'FYFR', 'FYONET', 'W006RC1Q027SBEA', 'A191RC1Q027SBEA', 'GEXPND', 
                   'GRECPT', 'FGEXPND', 'FGRECPT', 'SLEXPND', 'SLRECPT'],
    'BUSINESS': ['CORPPROFIT', 'CP', 'CPROFIT', 'BCNSDODNS', 'BCFDDODNS', 'NCBDBIQ027S', 'TODNS', 
                 'DODFS', 'FBCELLQ027S', 'TNWBSHNO', 'BOGZ1FL072051003Q', 'BOGZ1FL073164003Q', 
                 'BOGZ1FL073169175Q', 'TABSHNO', 'NETINC'],
    'REGIONAL': ['NYSTHPI', 'CASTHPI', 'TXSTHPI', 'FLSTHPI', 'WASTHPI', 'NYUR', 'CAUR', 'TXUR', 'FLUR', 'ILUR']
}

def diagnose_series(series_id):
    """Diagnose why a series failed and find alternatives"""
    diagnosis = {
        'series_id': series_id,
        'exists': False,
        'error': None,
        'alternatives': [],
        'suggested_replacement': None
    }
    
    try:
        # Try to get series info
        info = fred.get_series_info(series_id)
        diagnosis['exists'] = True
        
        # Try to get recent data
        try:
            data = fred.get_series(series_id)
            if data is not None and len(data) > 0:
                diagnosis['status'] = 'Active'
                diagnosis['last_observation'] = str(data.index[-1])
            else:
                diagnosis['status'] = 'No recent data'
        except:
            diagnosis['status'] = 'Error retrieving data'
            
    except Exception as e:
        diagnosis['error'] = str(e)
        
        # Search for similar series
        try:
            # Extract meaningful part of series ID for search
            search_term = series_id.replace('_', ' ').replace('-', ' ')
            
            # Special handling for known patterns
            if series_id.startswith('GS'):
                search_term = f"treasury constant maturity {series_id[2:]}"
            elif 'NAPM' in series_id:
                search_term = "ISM manufacturing PMI"
            elif 'DNDG' in series_id or 'DSERG' in series_id:
                search_term = "durable goods nondurable services"
            elif 'MORT' in series_id:
                search_term = "mortgage rate"
            
            # Search for alternatives
            results = fred.search(search_term, limit=5)
            
            if results is not None and len(results) > 0:
                for idx, (alt_id, alt_info) in enumerate(results.iterrows()):
                    diagnosis['alternatives'].append({
                        'id': alt_id,
                        'title': alt_info.get('title', 'Unknown'),
                        'units': alt_info.get('units', 'Unknown'),
                        'frequency': alt_info.get('frequency', 'Unknown')
                    })
                
                # Suggest the most popular alternative
                diagnosis['suggested_replacement'] = diagnosis['alternatives'][0]['id']
                
        except Exception as search_error:
            diagnosis['search_error'] = str(search_error)
    
    return diagnosis

def main():
    """Run diagnostic on all failed series"""
    
    print("🔍 FRED Failed Series Diagnostic Report")
    print("="*80)
    
    all_diagnostics = []
    replacements = {}
    
    for category, series_list in FAILED_SERIES.items():
        print(f"\n📊 Diagnosing {category} series...")
        replacements[category] = {}
        
        for series_id in series_list:
            time.sleep(0.1)  # Rate limiting
            
            diagnosis = diagnose_series(series_id)
            diagnosis['category'] = category
            all_diagnostics.append(diagnosis)
            
            if diagnosis['suggested_replacement']:
                replacements[category][series_id] = diagnosis['suggested_replacement']
                print(f"   {series_id} → {diagnosis['suggested_replacement']}")
            else:
                print(f"   {series_id} ❌ No replacement found")
    
    # Create diagnostic DataFrame
    df = pd.DataFrame(all_diagnostics)
    df.to_csv('fred_failed_series_diagnostic.csv', index=False)
    
    # Create replacements mapping
    print("\n" + "="*80)
    print("📋 SUGGESTED REPLACEMENTS:")
    print("="*80)
    
    replacement_list = []
    for category, mappings in replacements.items():
        print(f"\n{category}:")
        for old_id, new_id in mappings.items():
            print(f"   '{old_id}' → '{new_id}'")
            replacement_list.append({
                'category': category,
                'old_series_id': old_id,
                'new_series_id': new_id
            })
    
    # Save replacements
    if replacement_list:
        replacements_df = pd.DataFrame(replacement_list)
        replacements_df.to_csv('fred_series_replacements.csv', index=False)
        print(f"\n💾 Replacements saved to: fred_series_replacements.csv")
    
    # Summary statistics
    print(f"\n📊 SUMMARY:")
    print(f"   Total failed series: {len(all_diagnostics)}")
    print(f"   Series with replacements found: {len([d for d in all_diagnostics if d['suggested_replacement']])}")
    print(f"   Series truly missing: {len([d for d in all_diagnostics if not d['suggested_replacement']])}")
    
    # Show examples of alternatives found
    print("\n🔍 SAMPLE ALTERNATIVES FOUND:")
    samples = [d for d in all_diagnostics if d.get('alternatives', [])][:3]
    for sample in samples:
        print(f"\n{sample['series_id']}:")
        for alt in sample['alternatives'][:2]:
            print(f"   - {alt['id']}: {alt['title'][:60]}...")

if __name__ == "__main__":
    main()