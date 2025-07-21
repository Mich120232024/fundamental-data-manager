#!/bin/bash
# Bloomberg API Curl Examples - Checkpoint July 16, 2025
# All commands tested and working with real Bloomberg data

API_URL="http://20.172.249.92:8080"
API_KEY="test"

echo "=== Bloomberg API Curl Examples ==="
echo "API URL: $API_URL"
echo ""

echo "1. Health Check:"
echo "curl $API_URL/health"
echo ""

echo "2. FX Rates (Live):"
cat << 'EOF'
curl -X POST http://20.172.249.92:8080/api/fx/rates/live \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{
    "currency_pairs": ["EURUSD", "GBPUSD", "USDJPY"]
  }'
EOF
echo ""

echo "3. FX Volatility - ATM 1 Month:"
cat << 'EOF'
curl -X POST http://20.172.249.92:8080/api/fx/volatility \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{
    "currency_pairs": ["EURUSD", "GBPUSD"],
    "tenors": ["1M"],
    "deltas": ["ATM"]
  }'
EOF
echo ""

echo "4. FX Volatility - Full Smile:"
cat << 'EOF'
curl -X POST http://20.172.249.92:8080/api/fx/volatility \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{
    "currency_pairs": ["EURUSD"],
    "tenors": ["1M", "3M"],
    "deltas": ["25D", "10D", "ATM", "10C", "25C"]
  }'
EOF
echo ""

echo "5. FX Volatility - All Tenors:"
cat << 'EOF'
curl -X POST http://20.172.249.92:8080/api/fx/volatility \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{
    "currency_pairs": ["EURUSD"],
    "tenors": ["1W", "1M", "3M", "6M", "1Y"],
    "deltas": ["ATM"]
  }'
EOF
echo ""

echo "6. Bloomberg Reference Data:"
cat << 'EOF'
curl -X POST http://20.172.249.92:8080/api/bloomberg/reference \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{
    "securities": ["EURUSD Curncy", "GBPUSD Curncy", "SPX Index"],
    "fields": ["PX_LAST", "PX_BID", "PX_ASK", "CHG_PCT_1D"]
  }'
EOF
echo ""

echo "=== Working Bloomberg Tickers ==="
echo ""
echo "Currency Spot: EURUSD Curncy, GBPUSD Curncy, USDJPY Curncy"
echo "FX Vol ATM: EURUSDATM1M Curncy, GBPUSDATM3M Curncy"
echo "FX Vol Smile: EURUSD25D1M Curncy, EURUSD10C1M Curncy"
echo "Indices: SPX Index, DXY Index, VIX Index"
echo "Equities: AAPL US Equity, MSFT US Equity"
echo ""

echo "=== Maintenance Commands ==="
echo ""
echo "Check if API is running:"
echo 'az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 --command-id RunPowerShellScript --scripts "Get-Process python*"'
echo ""
echo "Restart API:"
echo 'az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 --command-id RunPowerShellScript --scripts "Get-Process python* | Stop-Process -Force; cd C:\BloombergAPI; Start-Process C:\Python311\python.exe -ArgumentList \"main.py\" -WindowStyle Hidden"'
echo ""
echo "View recent logs:"
echo 'az vm run-command invoke -g bloomberg-terminal-rg -n bloomberg-vm-02 --command-id RunPowerShellScript --scripts "Get-Content C:\BloombergAPI\logs\api_requests.log -Tail 20"'