#!/bin/bash

# Test script for Bloomberg historical data endpoint

echo "Testing Bloomberg Historical Data Endpoint"
echo "========================================"

# Calculate dates (10 days back)
END_DATE=$(date +%Y%m%d)
START_DATE=$(date -d "10 days ago" +%Y%m%d 2>/dev/null || date -v-10d +%Y%m%d)

echo "Date range: $START_DATE to $END_DATE"
echo ""

# Test 1: Get 10D butterfly historical data for last 10 days
echo "Test 1: EURUSD 10D Butterfly - Last 10 Days"
echo "--------------------------------------------"
curl -X POST http://20.172.249.92:8080/api/bloomberg/historical \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d "{
    \"security\": \"EURUSD10B1M BGN Curncy\",
    \"fields\": [\"PX_LAST\", \"PX_BID\", \"PX_ASK\"],
    \"start_date\": \"20250706\",
    \"end_date\": \"20250716\",
    \"periodicity\": \"DAILY\"
  }" | jq '.'

echo ""
echo ""

# Test 2: Get ATM volatility historical data
echo "Test 2: EURUSD ATM Volatility - Last 10 Days"
echo "---------------------------------------------"
curl -X POST http://20.172.249.92:8080/api/bloomberg/historical \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d "{
    \"security\": \"EURUSDV1M BGN Curncy\",
    \"fields\": [\"PX_LAST\", \"PX_HIGH\", \"PX_LOW\"],
    \"start_date\": \"20250706\",
    \"end_date\": \"20250716\",
    \"periodicity\": \"DAILY\"
  }" | jq '.'

echo ""
echo ""

# Test 3: Weekly data for 25D Risk Reversal
echo "Test 3: EURUSD 25D Risk Reversal - Weekly Data"
echo "-----------------------------------------------"
curl -X POST http://20.172.249.92:8080/api/bloomberg/historical \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d "{
    \"security\": \"EURUSD25R1M BGN Curncy\",
    \"fields\": [\"PX_LAST\"],
    \"start_date\": \"20250601\",
    \"end_date\": \"20250716\",
    \"periodicity\": \"WEEKLY\"
  }" | jq '.'