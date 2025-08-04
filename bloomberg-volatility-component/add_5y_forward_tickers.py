#!/usr/bin/env python3
"""Add 4Y and 5Y FX forward tickers to bloomberg_tickers table"""

import os
import psycopg2
from azure.keyvault.secrets import SecretClient
from azure.identity import AzureCliCredential
from datetime import datetime

# Setup Azure Key Vault
os.environ['KEY_VAULT_URL'] = 'https://gzc-finma-keyvault.vault.azure.net/'
credential = AzureCliCredential()
client = SecretClient(vault_url=os.environ['KEY_VAULT_URL'], credential=credential)

# Get connection string
conn_string = client.get_secret("postgres-connection-string").value
if conn_string.startswith("postgresql+asyncpg://"):
    conn_string = conn_string.replace("postgresql+asyncpg://", "postgresql://")

conn = psycopg2.connect(conn_string)
conn.autocommit = True
cursor = conn.cursor()

print("\n=== Adding 4Y and 5Y FX Forward Tickers ===\n")

# First, get all unique currency pairs that have FX forwards
cursor.execute("""
    SELECT DISTINCT 
        CASE 
            WHEN bloomberg_ticker LIKE 'EUR%' THEN SUBSTRING(bloomberg_ticker, 1, 6)
            WHEN bloomberg_ticker LIKE 'GBP%' THEN SUBSTRING(bloomberg_ticker, 1, 6)
            WHEN bloomberg_ticker LIKE 'USD%' THEN SUBSTRING(bloomberg_ticker, 1, 6)
            WHEN bloomberg_ticker LIKE 'AUD%' THEN SUBSTRING(bloomberg_ticker, 1, 6)
            WHEN bloomberg_ticker LIKE 'NZD%' THEN SUBSTRING(bloomberg_ticker, 1, 6)
            WHEN bloomberg_ticker LIKE 'CAD%' THEN SUBSTRING(bloomberg_ticker, 1, 6)
            WHEN bloomberg_ticker LIKE 'CHF%' THEN SUBSTRING(bloomberg_ticker, 1, 6)
            WHEN bloomberg_ticker LIKE 'SEK%' THEN SUBSTRING(bloomberg_ticker, 1, 6)
            WHEN bloomberg_ticker LIKE 'NOK%' THEN SUBSTRING(bloomberg_ticker, 1, 6)
            WHEN bloomberg_ticker LIKE 'JPY%' THEN SUBSTRING(bloomberg_ticker, 1, 6)
            ELSE SUBSTRING(bloomberg_ticker, 1, 6)
        END as pair,
        currency_code
    FROM public.bloomberg_tickers
    WHERE category = 'fx_forward'
    AND bloomberg_ticker LIKE '%3Y%'
    ORDER BY pair
""")
pairs_with_3y = cursor.fetchall()

print(f"Found {len(pairs_with_3y)} currency pairs with 3Y forwards:")
for pair, curr in pairs_with_3y:
    print(f"  {pair} ({curr})")

# Now add 4Y and 5Y for each pair
added_count = 0
for pair, curr in pairs_with_3y:
    for tenor in ['4Y', '5Y']:
        ticker = f"{pair}{tenor} Curncy"
        
        # Check if already exists
        cursor.execute("""
            SELECT 1 FROM public.bloomberg_tickers 
            WHERE bloomberg_ticker = %s
        """, (ticker,))
        
        if not cursor.fetchone():
            # Add the ticker
            cursor.execute("""
                INSERT INTO public.bloomberg_tickers 
                (bloomberg_ticker, currency_code, category, subcategory)
                VALUES (%s, %s, %s, %s)
            """, (ticker, curr, 'fx_forward', tenor))
            added_count += 1
            print(f"  Added: {ticker}")

print(f"\n✅ Added {added_count} new FX forward tickers (4Y and 5Y)")

# Verify the additions
cursor.execute("""
    SELECT COUNT(*) 
    FROM public.bloomberg_tickers 
    WHERE category = 'fx_forward'
    AND (bloomberg_ticker LIKE '%4Y%' OR bloomberg_ticker LIKE '%5Y%')
""")
count_5y = cursor.fetchone()[0]
print(f"Total 4Y/5Y forward tickers in database: {count_5y}")

cursor.close()
conn.close()

print("\n✅ FX Forward tickers now support up to 5 years!")