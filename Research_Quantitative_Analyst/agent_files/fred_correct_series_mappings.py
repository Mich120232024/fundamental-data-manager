#!/usr/bin/env python3
"""
FRED Correct Series Mappings
Author: Research Quantitative Analyst
Date: 2025-06-25
Purpose: Map incorrect/old series IDs to current valid alternatives
"""

# Based on diagnostic findings and FRED documentation research
CORRECTED_SERIES_MAPPINGS = {
    'GDP': {
        # Original incorrect → Correct alternatives
        'NYGDPMKTPCDWLD': 'NYGDPPCAPCDWLD',  # World GDP per capita
        'DNDGRC1': 'DNDGRG3Q086SBEA',       # Nondurable goods
        'DSERGC1': 'DSERRC1Q156NBEA',       # Services
        'GDPC1CTM': 'GDPC1',                # Just use main GDP series
        'NGDPPOT': 'GDPPOT'                 # Real Potential GDP
    },
    
    'EMPLOYMENT': {
        'JTSQUL': 'JTSLDR',                  # Job Openings: Layoffs and Discharges
        'JTSJOL': 'JTSJOR'                   # Job Openings Rate
    },
    
    'INFLATION': {
        'TRIMAFEM158SFRBCLE': 'TRMMEANCPIM158SFRBCLE',  # Trimmed Mean CPI Cleveland Fed
        'CUSR0000SA0': 'CPIAUCSL',          # Use main CPI series
        'BPCCRO1Q156NBEA': 'DPCCRV1Q225SBEA' # Real PCE
    },
    
    'RATES': {
        # Treasury constant maturity rates - use DGS series instead of GS
        'GS1M': 'DGS1MO',
        'GS3M': 'DGS3MO', 
        'GS6M': 'DGS6MO',
        'GS1': 'DGS1',
        'GS2': 'DGS2',
        'GS3': 'DGS3',
        'GS5': 'DGS5',
        'GS7': 'DGS7',
        'GS20': 'DGS20',
        'DFII10': 'DFII10'  # This actually exists, might be data issue
    },
    
    'HOUSING': {
        'PERMITS': 'PERMIT',                 # Building Permits
        'MORTGAGE15US': 'MORTGAGE15Y',       # 15-Year Mortgage Rate
        'MSACSR': 'USSTHPI',                # US House Price Index
        'HSN1F': 'HOUST1F',                 # Single-family housing starts
        'COMPUTSA': 'COMPUTNSA',            # Housing units completed
        'COMREPUSQ159N': 'TLRESCONS',       # Residential construction loans
        'NHSUSSPT': 'MSACSR',               # Monthly supply of houses
        'EVACANTUSQ176N': 'RRVRUSQ156N',    # Rental vacancy rate
        'RHVRUSQ156N': 'RHVRUSQ156N',       # Homeowner vacancy rate
        'EXHOSLUSM495S': 'HOUST'            # Use total housing starts
    },
    
    'MANUFACTURING': {
        'CAPUTLG2211S': 'MCUMFN',           # Manufacturing capacity utilization
        'MCUMFN': 'MCUMFN',                 # Actually exists
        'IPFINAL': 'IPFINAL',               # Industrial production final products
        'IPCONGD': 'IPCONGD',               # Industrial production consumer goods
        # ISM series replacements
        'NAPMEI': 'MANEMP',                 # ISM Manufacturing Employment
        'NAPMNOI': 'NAPMNOI',               # ISM New Orders
        'NAPMSDI': 'NAPMSDI',               # ISM Supplier Deliveries
        'NAPMII': 'NAPMPRI',                # ISM Prices Paid
        'DGORDER': 'DGORDER',               # Durable goods orders
        'NEWORDER': 'AMTMNO',               # Manufacturers new orders
        'BUSINV': 'BUSINV',                 # Business inventories
        'ISRATIO': 'ISRATIO',               # Inventory to sales ratio
        'TOTALSA': 'TOTBUSSMSA'             # Total business sales
    },
    
    'CONSUMER': {
        'A229RX0': 'A229RX0Q156NBEA',       # Real disposable personal income
        'TOTALSL': 'TOTALSL',               # Total consumer credit
        'CONSUMER': 'TOTALSLAR',            # Consumer loans at banks
        'DTCOLNVHFNM': 'DTCTLVNHFNM',       # Consumer credit excluding mortgages
        'TDSP': 'FODSP',                    # Financial obligations ratio
        'REVOLSL': 'REVOLSL'                # Revolving consumer credit
    },
    
    'FINANCIAL': {
        'DEXJPUS': 'EXJPUS',                # Japan/US exchange rate
        'DEXCAUS': 'EXCAUS',                # Canada/US exchange rate
        'DEXUSUK': 'EXUSUK',                # US/UK exchange rate
        'DEXCHUS': 'EXCHUS',                # China/US exchange rate
        'DEXMXUS': 'EXMXUS',                # Mexico/US exchange rate
        'DTWEXBGS': 'DTWEXBGS',             # Trade weighted dollar index
        'BAMLC0A0CM': 'BAMLC0A0CMEY',       # Corporate bond yield
        'TEDRATE': 'TEDRATE',               # TED spread
        'GOLDPMGBD228NLBM': 'GOLDAMGBD228NLBM',  # Gold price London fix
        'DHHNGSP': 'DHHNGSP',               # Natural gas price
        'DCOILBRENTEU': 'DCOILBRENTEU',     # Brent oil price
        'GASREGW': 'GASREGW'                # US regular gas price
    },
    
    'MONEY_CREDIT': {
        'M1SL': 'WM1NS',                    # M1 money stock (weekly)
        'REALLN': 'BUSLOANS',               # Business loans
        'NONREVSL': 'NREVSL',               # Nonrevolving credit
        'CCLACBW027SBOG': 'TOTCI',          # Commercial and industrial loans
        'DRISCFLM': 'DPSACBW027SBOG',       # Deposits at banks
        'DPSACBW027SBOG': 'DPSACBW027SBOG', # Deposits 
        'H8B1001NCBCMG': 'TOTLL',           # Total loans and leases
        'TOTBKCR': 'TOTBKCR',               # Bank credit
        'USGSEC': 'USGSEC',                 # US government securities
        'OTHSEC': 'OTHSEC',                 # Other securities
        'INVEST': 'INVEST'                  # Bank credit investments
    },
    
    'TRADE': {
        'NETEXP': 'NETEXP',                 # Net exports
        'EXPGS': 'EXPGS',                   # Exports
        'IMPGS': 'IMPGS',                   # Imports  
        'BOPGSTB': 'BOPGSTB',               # Trade balance
        'IEABC': 'BOPGSTB',                 # Use trade balance
        'XTEXVA01USM664S': 'BOPTEXP',       # Exports in BOP
        'XTIMVA01USM664S': 'BOPTIMP',       # Imports in BOP
        'USATRADEBALGDPB6PT': 'NETEXPQ',    # Net exports share of GDP
        'CURCIR': 'CURRCIR',                # Currency in circulation
        # Exchange rates - use without DEX prefix
        'EXUSEU': 'DEXUSEU',
        'EXJPUS': 'DEXJPUS',
        'EXCAUS': 'DEXCAUS',
        'EXMXUS': 'DEXMXUS',
        'EXCHUS': 'DEXCHUS',
        'EXUSUK': 'DEXUSUK'
    },
    
    'GOVERNMENT': {
        'FYFSD': 'MTSDS133FMS',             # Federal surplus/deficit
        'FYFR': 'W006RC1Q027SBEA',          # Federal receipts
        'FYONET': 'G160291Q027SBEA',        # Federal outlays
        'W006RC1Q027SBEA': 'W006RC1Q027SBEA', # Federal receipts quarterly
        'A191RC1Q027SBEA': 'FGRECPT',       # Federal receipts annual
        'GEXPND': 'W018RC1Q027SBEA',        # Government expenditures
        'GRECPT': 'W006RC1Q027SBEA',        # Government receipts
        'FGEXPND': 'FGEXPND',               # Federal expenditures
        'FGRECPT': 'FGRECPT',               # Federal receipts
        'SLEXPND': 'SLEXPND',               # State & local expenditures
        'SLRECPT': 'SLRECPT'                # State & local receipts
    },
    
    'BUSINESS': {
        'CORPPROFIT': 'CP',                 # Corporate profits
        'CP': 'CP',                         # Corporate profits
        'CPROFIT': 'CPROFIT',               # Corporate profits after tax
        'BCNSDODNS': 'NCBDBIQ027S',         # Nonfinancial corporate debt
        'BCFDDODNS': 'TCMDO',               # Total credit market debt
        'NCBDBIQ027S': 'NCBDBIQ027S',       # Nonfinancial business debt
        'TODNS': 'TCMDO',                   # Total debt outstanding
        'DODFS': 'DODFS',                   # Domestic financial sector debt
        'FBCELLQ027S': 'FBCELLQ027S',       # Flow of funds liabilities
        'TNWBSHNO': 'TNWBSHNO',             # Nonfinancial business net worth
        'BOGZ1FL072051003Q': 'TABSNNCB',    # Nonfinancial corporate business assets
        'BOGZ1FL073164003Q': 'TNWMVBSNNCB', # Market value of equities
        'BOGZ1FL073169175Q': 'NCBEILQ027S', # Nonfinancial business equity
        'TABSHNO': 'TABSHNO',               # Total assets households
        'NETINC': 'A053RC1Q027SBEA'         # Corporate profits
    },
    
    'REGIONAL': {
        # State house price indices
        'NYSTHPI': 'NYSTHPI',
        'CASTHPI': 'CASTHPI', 
        'TXSTHPI': 'TXSTHPI',
        'FLSTHPI': 'FLSTHPI',
        'WASTHPI': 'WASTHPI',
        # State unemployment rates
        'NYUR': 'NYUR',
        'CAUR': 'CAUR',
        'TXUR': 'TXUR', 
        'FLUR': 'FLUR',
        'ILUR': 'ILUR'
    }
}

# Create a flat mapping for easy lookup
def get_flat_mappings():
    """Convert nested dict to flat old->new mapping"""
    flat_map = {}
    for category, mappings in CORRECTED_SERIES_MAPPINGS.items():
        for old_id, new_id in mappings.items():
            flat_map[old_id] = new_id
    return flat_map

if __name__ == "__main__":
    import json
    
    # Save mappings to JSON
    with open('fred_series_corrections.json', 'w') as f:
        json.dump(CORRECTED_SERIES_MAPPINGS, f, indent=2)
    
    # Create summary
    total_mappings = sum(len(v) for v in CORRECTED_SERIES_MAPPINGS.values())
    print(f"✅ Created {total_mappings} series corrections")
    print("\n📊 Corrections by category:")
    for cat, mappings in CORRECTED_SERIES_MAPPINGS.items():
        print(f"   {cat}: {len(mappings)} corrections")