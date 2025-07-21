#!/bin/bash

echo "Bloomberg Volatility Surface Web Application"
echo "==========================================="
echo ""
echo "Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "Starting web server..."
echo "Open http://localhost:8000 in your browser"
echo ""

python3 web_app.py